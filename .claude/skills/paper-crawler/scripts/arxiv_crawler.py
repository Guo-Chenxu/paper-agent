import argparse
import os
import re
import time
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple

import arxiv
import requests
from tqdm import tqdm


def normalize_title(title: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", " ", title.lower())
    return " ".join(normalized.split())


def title_similarity(left: str, right: str) -> float:
    return SequenceMatcher(None, normalize_title(left), normalize_title(right)).ratio()


class ArxivCrawler:
    """Crawler for arXiv metadata and PDFs."""

    def __init__(self, save_dir: str = "./papers", request_delay: float = 0.2):
        self.save_dir = save_dir
        self.request_delay = request_delay
        self.pdf_dir = os.path.join(save_dir, "pdfs")
        self.abstract_dir = os.path.join(save_dir, "abstracts")
        os.makedirs(save_dir, exist_ok=True)
        os.makedirs(self.pdf_dir, exist_ok=True)
        os.makedirs(self.abstract_dir, exist_ok=True)

        self.client = arxiv.Client(
            page_size=100,
            delay_seconds=request_delay,
            num_retries=3,
        )

    def _result_to_dict(self, result: arxiv.Result) -> Dict:
        arxiv_id = result.entry_id.split("/")[-1]
        return {
            "title": result.title,
            "authors": [author.name for author in result.authors],
            "abstract": result.summary,
            "arxiv_id": arxiv_id,
            "pdf_url": result.pdf_url,
            "submitted_date": result.published.strftime("%Y-%m-%d"),
            "year": result.published.year,
            "venue": "arXiv",
            "categories": result.categories,
            "source": "arxiv",
            "source_url": result.entry_id,
            "doi": result.doi,
        }

    def search(self, query: str, max_results: int = 100, years: int = 3) -> List[Dict]:
        cutoff_date = datetime.utcnow() - timedelta(days=years * 365)
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending,
        )

        papers: List[Dict] = []
        for result in tqdm(self.client.results(search), desc="Searching arXiv"):
            published = result.published.replace(tzinfo=None)
            if published < cutoff_date:
                break
            paper = self._result_to_dict(result)
            papers.append(paper)
            self.save_abstract(paper)
        return papers

    def _search_raw(self, query: str, max_results: int) -> List[Dict]:
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance,
            sort_order=arxiv.SortOrder.Descending,
        )
        papers: List[Dict] = []
        try:
            for result in self.client.results(search):
                papers.append(self._result_to_dict(result))
        except arxiv.HTTPError:
            return []
        return papers

    def search_by_title(
        self,
        title: str,
        years: int = 5,
        max_results: int = 8,
        min_similarity: float = 0.84,
    ) -> Optional[Dict]:
        quoted_query = f'ti:"{title}"'
        candidates = self._search_raw(quoted_query, max_results=max_results)
        if not candidates:
            candidates = self._search_raw(title, max_results=max_results)

        cutoff_date = datetime.utcnow() - timedelta(days=years * 365)
        best_paper = None
        best_score = 0.0
        for paper in candidates:
            submitted_date = datetime.strptime(
                paper["submitted_date"], "%Y-%m-%d")
            if submitted_date < cutoff_date:
                continue
            score = title_similarity(title, paper["title"])
            if score > best_score:
                best_paper = paper
                best_score = score

        if best_paper and best_score >= min_similarity:
            return best_paper
        return None

    def save_abstract(self, paper: Dict, filename_token: Optional[str] = None) -> str:
        token = filename_token or paper.get("arxiv_id") or normalize_title(
            paper["title"]).replace(" ", "_")
        path = os.path.join(self.abstract_dir, f"{token}.txt")
        with open(path, "w", encoding="utf-8") as file_obj:
            file_obj.write(f"Title: {paper['title']}\n\n")
            file_obj.write(
                f"Authors: {', '.join(paper.get('authors', []))}\n\n")
            file_obj.write(
                f"Submitted: {paper.get('submitted_date', 'Unknown')}\n\n")
            file_obj.write(f"Venue: {paper.get('venue', 'arXiv')}\n\n")
            if paper.get("categories"):
                file_obj.write(
                    f"Categories: {', '.join(paper['categories'])}\n\n")
            file_obj.write(f"Abstract:\n{paper.get('abstract', '')}\n")
        return path

    def download_paper_pdf(self, paper: Dict, pdf_path: str) -> Tuple[bool, str]:
        pdf_url = paper.get("pdf_url")
        if not pdf_url and paper.get("arxiv_id"):
            pdf_url = f"https://arxiv.org/pdf/{paper['arxiv_id']}.pdf"
        if not pdf_url:
            return False, "missing_pdf_url"

        try:
            response = requests.get(pdf_url, timeout=45)
        except requests.RequestException as exc:
            return False, f"request_error:{exc.__class__.__name__}"

        if response.status_code >= 400:
            return False, f"http_{response.status_code}"

        content_type = response.headers.get("Content-Type", "").lower()
        if "pdf" not in content_type and not response.content.startswith(b"%PDF"):
            return False, "non_pdf_response"

        with open(pdf_path, "wb") as file_obj:
            file_obj.write(response.content)
        return True, "ok"

    def download_pdfs(self, papers: List[Dict]) -> None:
        for paper in tqdm(papers, desc="Downloading arXiv PDFs"):
            token = paper.get("arxiv_id") or normalize_title(
                paper["title"]).replace(" ", "_")
            pdf_path = os.path.join(self.pdf_dir, f"{token}.pdf")
            if os.path.exists(pdf_path):
                continue
            self.download_paper_pdf(paper, pdf_path)
            time.sleep(self.request_delay)


# Backward-compatible name for existing usage.
class PaperCrawler(ArxivCrawler):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Search and download papers from arXiv.")
    parser.add_argument(
        "--query",
        default="distribute OR scheduler OR gang scheduling OR cluster management OR resource allocation",
        help="arXiv query string",
    )
    parser.add_argument("--max-results", type=int,
                        default=200, help="Maximum number of papers")
    parser.add_argument("--years", type=int, default=3,
                        help="Look back window in years")
    parser.add_argument("--save-dir", default="./papers",
                        help="Directory for outputs")
    parser.add_argument("--download-pdf", action="store_true",
                        help="Download PDFs after search")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    crawler = ArxivCrawler(save_dir=args.save_dir)
    found_papers = crawler.search(
        args.query, max_results=args.max_results, years=args.years)
    print(f"Found {len(found_papers)} papers on arXiv")
    if args.download_pdf:
        crawler.download_pdfs(found_papers)
