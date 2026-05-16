import argparse
import json
import os
import re
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import requests

from arxiv_crawler import ArxivCrawler, normalize_title, title_similarity
from openalex_crawler import OpenAlexCrawler


VENUE_CONFIG = {
    "ieee": {
        "display_name": "IEEE",
        "aliases": ["ieee", "transactions on", "ieee/acm", "international conference on"],
    },
    "acm": {
        "display_name": "ACM",
        "aliases": ["acm", "sig", "international conference on", "symposium on"],
    },
    "osdi": {
        "display_name": "OSDI",
        "aliases": ["osdi", "operating systems design and implementation", "usenix"],
    },
}


def safe_filename(text: str) -> str:
    token = normalize_title(text)
    token = re.sub(r"\s+", "_", token)
    return token[:120] if len(token) > 120 else token


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
        self.openalex = OpenAlexCrawler(mailto=mailto)
        self.arxiv = ArxivCrawler(save_dir=output_dir)

    def collect_metadata(
        self,
        query: str,
        venues: List[str],
        max_results_per_venue: int,
        years: int,
        workers: int = 3,
    ) -> Dict[str, List[Dict]]:
        results_by_venue: Dict[str, List[Dict]] = {}

        def fetch_single(venue_key: str) -> Tuple[str, List[Dict]]:
            conf = VENUE_CONFIG[venue_key]
            try:
                papers = self.openalex.search(
                    query=query,
                    venue_name=conf["display_name"],
                    venue_aliases=conf["aliases"],
                    max_results=max_results_per_venue,
                    years=years,
                )
            except requests.RequestException:
                papers = []
            return venue_key, papers

        with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
            future_map = {pool.submit(
                fetch_single, venue): venue for venue in venues}
            for future in as_completed(future_map):
                venue_key, papers = future.result()
                results_by_venue[venue_key] = papers

        return results_by_venue

    @staticmethod
    def _content_looks_like_pdf(response: requests.Response) -> bool:
        content_type = (response.headers.get("Content-Type") or "").lower()
        return "pdf" in content_type or response.content.startswith(b"%PDF")

    def _download_with_status(self, url: str, out_path: str) -> Tuple[bool, str]:
        try:
            response = requests.get(url, timeout=45, allow_redirects=True)
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
        if paper.get("openalex_id"):
            return paper["openalex_id"].split("/")[-1]
        if paper.get("arxiv_id"):
            return paper["arxiv_id"].replace("/", "_")
        return safe_filename(paper.get("title") or f"paper_{int(time.time())}")

    def _save_abstract(self, paper: Dict, token: str) -> None:
        path = os.path.join(self.paths["abstracts"], f"{token}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"Title: {paper.get('title', '')}\n\n")
            f.write(f"Authors: {', '.join(paper.get('authors', []))}\n\n")
            f.write(f"Venue: {paper.get('venue', '')}\n\n")
            f.write(
                f"Publication Date: {paper.get('publication_date', paper.get('submitted_date', ''))}\n\n")
            if paper.get("doi"):
                f.write(f"DOI: {paper['doi']}\n\n")
            if paper.get("source_url"):
                f.write(f"Source URL: {paper['source_url']}\n\n")
            f.write("Abstract:\n")
            f.write((paper.get("abstract") or "") + "\n")

    @staticmethod
    def _deduplicate(papers: List[Dict]) -> List[Dict]:
        by_key: Dict[str, Dict] = {}
        for paper in papers:
            doi = (paper.get("doi") or "").lower().replace(
                "https://doi.org/", "")
            if doi:
                key = f"doi:{doi}"
            else:
                key = f"title:{safe_filename(paper.get('title') or '')}"

            if key not in by_key:
                by_key[key] = paper
                continue

            existing = by_key[key]
            existing_score = int(bool(existing.get("pdf_url"))) + \
                int(bool(existing.get("abstract")))
            incoming_score = int(bool(paper.get("pdf_url"))) + \
                int(bool(paper.get("abstract")))
            if incoming_score > existing_score:
                by_key[key] = paper

        return list(by_key.values())

    def _fallback_to_arxiv(
        self,
        paper: Dict,
        years: int,
    ) -> Tuple[bool, Optional[Dict], str]:
        title = paper.get("title") or ""
        if not title:
            return False, None, "missing_title"

        matched = self.arxiv.search_by_title(title=title, years=years)
        if not matched:
            return False, None, "arxiv_not_found"

        local_name = self._build_record_token(paper) + "_fallback_arxiv"
        out_pdf = os.path.join(self.paths["pdfs"], f"{local_name}.pdf")
        ok, reason = self.arxiv.download_paper_pdf(matched, out_pdf)
        if not ok:
            return False, None, f"arxiv_download_failed:{reason}"

        merged = dict(paper)
        merged["fallback"] = {
            "source": "arxiv",
            "arxiv_id": matched.get("arxiv_id"),
            "pdf_url": matched.get("pdf_url"),
            "title_similarity": round(title_similarity(title, matched.get("title", "")), 4),
            "reason": "primary_source_auth_or_pdf_failure",
        }
        merged["pdf_local_path"] = out_pdf
        merged["pdf_source"] = "arxiv_fallback"
        merged["arxiv_id"] = matched.get("arxiv_id")
        if not merged.get("abstract") and matched.get("abstract"):
            merged["abstract"] = matched["abstract"]
        return True, merged, "fallback_ok"

    def download_pdfs_with_fallback(
        self,
        papers: List[Dict],
        years: int,
    ) -> Tuple[List[Dict], Dict[str, int]]:
        downloaded: List[Dict] = []
        stats = defaultdict(int)

        for paper in papers:
            token = self._build_record_token(paper)
            self._save_abstract(paper, token)

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
                reason = "missing_pdf_url"
                stats["primary_fail_missing_pdf_url"] += 1

            fallback_ok, merged_paper, fallback_reason = self._fallback_to_arxiv(
                paper, years=years)
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
        venues: List[str],
        max_results_per_venue: int,
        years: int,
        workers: int,
        download_pdf: bool,
    ) -> Dict:
        metadata = self.collect_metadata(
            query=query,
            venues=venues,
            max_results_per_venue=max_results_per_venue,
            years=years,
            workers=workers,
        )

        all_raw: List[Dict] = []
        source_counts = {}
        for venue, items in metadata.items():
            source_counts[venue] = len(items)
            all_raw.extend(items)

        deduped = self._deduplicate(all_raw)

        final_papers = deduped
        download_stats = {}
        if download_pdf:
            final_papers, download_stats = self.download_pdfs_with_fallback(
                deduped, years=years)

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        metadata_path = os.path.join(
            self.paths["metadata"], f"papers_{timestamp}.json")
        summary_path = os.path.join(
            self.paths["metadata"], f"summary_{timestamp}.json")

        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(final_papers, f, ensure_ascii=False, indent=2)

        summary = {
            "query": query,
            "venues": venues,
            "years": years,
            "max_results_per_venue": max_results_per_venue,
            "source_counts": source_counts,
            "raw_count": len(all_raw),
            "deduped_count": len(deduped),
            "final_count": len(final_papers),
            "download_stats": download_stats,
            "metadata_output": metadata_path,
        }

        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        summary["summary_output"] = summary_path
        return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Multi-source conference crawler with arXiv fallback")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument(
        "--venues",
        nargs="+",
        default=["ieee", "acm", "osdi"],
        choices=list(VENUE_CONFIG.keys()),
        help="Venue groups to crawl",
    )
    parser.add_argument("--max-results-per-venue", type=int,
                        default=120, help="Max papers per venue")
    parser.add_argument("--years", type=int, default=3,
                        help="Recent years window")
    parser.add_argument("--workers", type=int, default=3,
                        help="Parallel workers")
    parser.add_argument("--output-dir", default="./papers",
                        help="Output directory")
    parser.add_argument("--mailto", default=None,
                        help="Email for OpenAlex courtesy pool")
    parser.add_argument("--download-pdf", action="store_true",
                        help="Download PDFs and apply fallback")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    crawler = MultiSourcePaperCrawler(
        output_dir=args.output_dir, mailto=args.mailto)
    summary = crawler.run(
        query=args.query,
        venues=args.venues,
        max_results_per_venue=args.max_results_per_venue,
        years=args.years,
        workers=args.workers,
        download_pdf=args.download_pdf,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
