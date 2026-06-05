import argparse
import json
import os
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import requests

from arxiv_crawler import ArxivCrawler, title_similarity
from openalex_crawler import OpenAlexCrawler
from paper_record import build_record_id, deduplicate_papers, provider_counts_for, save_abstract
from semantic_scholar_crawler import SemanticScholarCrawler
from usenix_crawler import UsenixCrawler


DEFAULT_PROVIDERS = ["openalex", "arxiv", "semanticscholar", "usenix"]


def ensure_dirs(base_dir: str) -> Dict[str, str]:
    paths = {
        "base": base_dir,
        "pdfs": os.path.join(base_dir, "pdfs"),
        "abstracts": os.path.join(base_dir, "abstracts"),
        "metadata": os.path.join(base_dir, "metadata"),
    }
    for path in paths.values():
        os.makedirs(path, exist_ok=True)
    return paths


class MultiSourcePaperCrawler:
    def __init__(self, output_dir: str = "./papers", mailto: Optional[str] = None):
        self.paths = ensure_dirs(output_dir)
        self.provider_clients = {
            "openalex": OpenAlexCrawler(mailto=mailto),
            "arxiv": ArxivCrawler(save_dir=output_dir),
            "semanticscholar": SemanticScholarCrawler(),
            "usenix": UsenixCrawler(),
        }

    def _fetch_provider(
        self,
        provider: str,
        query: str,
        max_results_per_provider: int,
        years: int,
        usenix_venues: List[str],
    ) -> Tuple[str, List[Dict], Optional[str]]:
        try:
            client = self.provider_clients.get(provider)
            if client is None:
                return provider, [], f"unknown_provider: {provider}"
            if provider == "usenix":
                papers = client.search(
                    query=query,
                    venues=usenix_venues,
                    max_results=max_results_per_provider,
                    years=years,
                )
            else:
                papers = client.search(
                    query=query,
                    max_results=max_results_per_provider,
                    years=years,
                )
            return provider, papers, None
        except Exception as exc:
            return provider, [], f"{exc.__class__.__name__}: {exc}"

    def collect_metadata(
        self,
        query: str,
        providers: List[str],
        max_results_per_provider: int,
        years: int,
        workers: int = 4,
        usenix_venues: Optional[List[str]] = None,
    ) -> Tuple[Dict[str, List[Dict]], Dict[str, str]]:
        usenix_venues = usenix_venues or ["osdi"]
        results_by_provider: Dict[str, List[Dict]] = {}
        provider_errors: Dict[str, str] = {}

        with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
            future_map = {
                pool.submit(
                    self._fetch_provider,
                    provider,
                    query,
                    max_results_per_provider,
                    years,
                    usenix_venues,
                ): provider
                for provider in providers
            }
            for future in as_completed(future_map):
                provider, papers, error = future.result()
                results_by_provider[provider] = papers
                if error:
                    provider_errors[provider] = error

        for provider in providers:
            results_by_provider.setdefault(provider, [])
        return results_by_provider, provider_errors

    @staticmethod
    def _content_looks_like_pdf(response: requests.Response) -> bool:
        content_type = (response.headers.get("Content-Type") or "").lower()
        return "pdf" in content_type or response.content.startswith(b"%PDF")

    def _download_with_status(self, url: str, out_path: str) -> Tuple[bool, str]:
        try:
            response = requests.get(url, timeout=300, allow_redirects=True)
        except requests.RequestException as exc:
            return False, f"request_error:{exc.__class__.__name__}"

        if response.status_code in (401, 403, 407):
            return False, f"auth_blocked_{response.status_code}"
        if response.status_code == 429:
            return False, "rate_limited_429"
        if response.status_code >= 400:
            return False, f"http_{response.status_code}"
        if not self._content_looks_like_pdf(response):
            return False, "non_pdf_response"

        with open(out_path, "wb") as file_obj:
            file_obj.write(response.content)
        return True, "ok"

    def _build_record_token(self, paper: Dict) -> str:
        return paper.get("record_id") or build_record_id(paper)

    def _fallback_to_arxiv(self, paper: Dict, years: int) -> Tuple[bool, Optional[Dict], str]:
        title = paper.get("title") or ""
        if not title:
            return False, None, "missing_title"

        arxiv_client = self.provider_clients.get("arxiv")
        if not arxiv_client or not hasattr(arxiv_client, "search_by_title"):
            return False, None, "arxiv_fallback_unavailable"

        matched = arxiv_client.search_by_title(title=title, years=years)
        if not matched:
            return False, None, "arxiv_not_found"

        local_name = self._build_record_token(paper) + "_fallback_arxiv"
        out_pdf = os.path.join(self.paths["pdfs"], f"{local_name}.pdf")
        ok, reason = arxiv_client.download_paper_pdf(matched, out_pdf)
        if not ok:
            return False, None, f"arxiv_download_failed:{reason}"

        merged = dict(paper)
        merged["fallback"] = {
            "source": "arxiv",
            "arxiv_id": matched.get("arxiv_id"),
            "pdf_url": matched.get("pdf_url"),
            "title_similarity": round(title_similarity(title, matched.get("title", "")), 4),
            "reason": "primary_pdf_unavailable",
        }
        merged["pdf_local_path"] = out_pdf
        merged["pdf_source"] = "arxiv_fallback"
        merged["arxiv_id"] = matched.get("arxiv_id")
        if not merged.get("abstract") and matched.get("abstract"):
            merged["abstract"] = matched["abstract"]
            merged["abstract_path"] = save_abstract(self.paths["base"], merged)
        return True, merged, "fallback_ok"

    def download_pdfs_with_fallback(self, papers: List[Dict], years: int) -> Tuple[List[Dict], Dict[str, int]]:
        downloaded: List[Dict] = []
        stats = defaultdict(int)

        for paper in papers:
            token = self._build_record_token(paper)
            out_pdf = os.path.join(self.paths["pdfs"], f"{token}.pdf")
            pdf_url = paper.get("pdf_url")
            if os.path.exists(out_pdf):
                paper["pdf_local_path"] = out_pdf
                paper["pdf_source"] = "cached"
                downloaded.append(paper)
                stats["cached"] += 1
                continue

            if pdf_url:
                ok, reason = self._download_with_status(pdf_url, out_pdf)
                if ok:
                    paper["pdf_local_path"] = out_pdf
                    paper["pdf_source"] = "primary"
                    downloaded.append(paper)
                    stats["primary_success"] += 1
                    time.sleep(0.25)
                    continue
                stats[f"primary_fail_{reason}"] += 1
            else:
                stats["primary_fail_missing_pdf_url"] += 1

            fallback_ok, merged_paper, fallback_reason = self._fallback_to_arxiv(paper, years=years)
            if fallback_ok and merged_paper:
                downloaded.append(merged_paper)
                stats["fallback_success"] += 1
            else:
                stats[f"fallback_fail_{fallback_reason}"] += 1

            time.sleep(0.25)

        return downloaded, dict(stats)

    def run(
        self,
        query: str,
        providers: List[str],
        max_results_per_provider: int,
        years: int,
        workers: int,
        download_pdf: bool,
        usenix_venues: Optional[List[str]] = None,
    ) -> Dict:
        metadata, provider_errors = self.collect_metadata(
            query=query,
            providers=providers,
            max_results_per_provider=max_results_per_provider,
            years=years,
            workers=workers,
            usenix_venues=usenix_venues,
        )

        raw_provider_counts = {provider: len(metadata.get(provider, [])) for provider in providers}
        all_raw: List[Dict] = []
        for provider in providers:
            all_raw.extend(metadata.get(provider, []))

        if not all_raw and len(provider_errors) == len(providers):
            raise RuntimeError("all providers failed")

        deduped = deduplicate_papers(all_raw)
        for paper in deduped:
            paper["abstract_path"] = save_abstract(self.paths["base"], paper)

        final_papers = deduped
        download_stats = {}
        if download_pdf:
            final_papers, download_stats = self.download_pdfs_with_fallback(deduped, years=years)

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        metadata_path = os.path.join(self.paths["metadata"], f"papers_{timestamp}.json")
        summary_path = os.path.join(self.paths["metadata"], f"summary_{timestamp}.json")

        with open(metadata_path, "w", encoding="utf-8") as file_obj:
            json.dump(final_papers, file_obj, ensure_ascii=False, indent=2)

        summary = {
            "query": query,
            "providers": providers,
            "years": years,
            "max_results_per_provider": max_results_per_provider,
            "raw_provider_counts": raw_provider_counts,
            "provider_counts": provider_counts_for(final_papers),
            "raw_count": len(all_raw),
            "deduped_count": len(deduped),
            "final_count": len(final_papers),
            "provider_errors": provider_errors,
            "download_stats": download_stats,
            "metadata_output": metadata_path,
        }

        with open(summary_path, "w", encoding="utf-8") as file_obj:
            json.dump(summary, file_obj, ensure_ascii=False, indent=2)

        summary["summary_output"] = summary_path
        return summary


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Multi-provider paper crawler with arXiv fallback")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument(
        "--providers",
        nargs="+",
        default=DEFAULT_PROVIDERS,
        choices=DEFAULT_PROVIDERS,
        help="Primary providers to query",
    )
    parser.add_argument("--max-results-per-provider", type=int, default=120, help="Max papers per provider")
    parser.add_argument("--years", type=int, default=3, help="Recent years window")
    parser.add_argument("--workers", type=int, default=4, help="Parallel workers")
    parser.add_argument("--output-dir", default="./papers", help="Output directory")
    parser.add_argument("--mailto", default=None, help="Email for OpenAlex courtesy pool")
    parser.add_argument("--usenix-venues", nargs="+", default=["osdi"], help="USENIX venues such as osdi nsdi atc")
    parser.add_argument("--download-pdf", action="store_true", help="Download PDFs and apply arXiv fallback")
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()
    crawler = MultiSourcePaperCrawler(output_dir=args.output_dir, mailto=args.mailto)
    summary = crawler.run(
        query=args.query,
        providers=args.providers,
        max_results_per_provider=args.max_results_per_provider,
        years=args.years,
        workers=args.workers,
        download_pdf=args.download_pdf,
        usenix_venues=args.usenix_venues,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
