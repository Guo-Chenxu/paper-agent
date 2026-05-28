import argparse
import json
import os
import time
from datetime import datetime
from typing import Dict, List, Optional

import requests


class SemanticScholarCrawler:
    BASE_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
    FIELDS = "paperId,title,abstract,year,venue,url,citationCount,externalIds,openAccessPdf,authors"

    def __init__(self, request_delay: float = 1.0, api_key: Optional[str] = None):
        self.request_delay = request_delay
        self.api_key = api_key or os.getenv("SEMANTIC_SCHOLAR_API_KEY")

    def _request(self, params: Dict) -> Dict:
        headers = {}
        if self.api_key:
            headers["x-api-key"] = self.api_key
        last_error = None
        for attempt in range(3):
            try:
                response = requests.get(self.BASE_URL, params=params, headers=headers, timeout=45)
                if response.status_code == 429 and attempt < 2:
                    time.sleep(self.request_delay * (attempt + 1))
                    continue
                response.raise_for_status()
                return response.json()
            except requests.RequestException as exc:
                last_error = exc
                if attempt < 2:
                    time.sleep(self.request_delay * (attempt + 1))
        raise last_error

    def _normalize_paper(self, result: Dict) -> Dict:
        external_ids = result.get("externalIds") or {}
        open_pdf = result.get("openAccessPdf") or {}
        year = result.get("year")
        return {
            "title": result.get("title") or "",
            "authors": [author.get("name", "") for author in result.get("authors") or [] if author.get("name")],
            "abstract": result.get("abstract") or "",
            "year": year,
            "publication_date": f"{year}-01-01" if year else "",
            "venue": result.get("venue") or "",
            "provider": "semanticscholar",
            "provider_id": result.get("paperId") or "",
            "source": "semanticscholar",
            "source_url": result.get("url") or "",
            "pdf_url": open_pdf.get("url") or "",
            "doi": external_ids.get("DOI") or "",
            "arxiv_id": external_ids.get("ArXiv") or "",
            "openalex_id": external_ids.get("OpenAlex") or "",
            "semantic_scholar_id": result.get("paperId") or "",
            "cited_by_count": result.get("citationCount") or 0,
        }

    def search(self, query: str, max_results: int = 100, years: int = 3) -> List[Dict]:
        min_year = datetime.utcnow().year - years + 1
        papers: List[Dict] = []
        offset = 0
        while len(papers) < max_results:
            limit = min(max_results - len(papers), 100)
            params = {
                "query": query,
                "limit": limit,
                "offset": offset,
                "fields": self.FIELDS,
                "year": f"{min_year}-",
            }
            payload = self._request(params)
            batch = payload.get("data") or []
            if not batch:
                break
            papers.extend(self._normalize_paper(item) for item in batch)
            if len(batch) < limit:
                break
            offset += len(batch)
            time.sleep(self.request_delay)
        return papers[:max_results]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Semantic Scholar paper crawler")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--max-results", type=int, default=100, help="Maximum number of results")
    parser.add_argument("--years", type=int, default=3, help="Recent years window")
    parser.add_argument("--output", required=True, help="Output JSON path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    crawler = SemanticScholarCrawler()
    papers = crawler.search(args.query, max_results=args.max_results, years=args.years)
    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as file_obj:
        json.dump(papers, file_obj, ensure_ascii=False, indent=2)
    print(f"Semantic Scholar papers: {len(papers)} -> {args.output}")


if __name__ == "__main__":
    main()
