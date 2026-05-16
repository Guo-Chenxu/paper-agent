import argparse
import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, Iterable, List, Optional

import requests


class OpenAlexCrawler:
    """Fetch paper metadata from OpenAlex by venue aliases and query terms."""

    BASE_URL = "https://api.openalex.org/works"

    def __init__(self, request_delay: float = 0.3, mailto: Optional[str] = None):
        self.request_delay = request_delay
        self.mailto = mailto

    def _request(self, params: Dict) -> Dict:
        local_params = dict(params)
        if self.mailto:
            local_params["mailto"] = self.mailto

        max_attempts = 4
        for attempt in range(max_attempts):
            response = requests.get(self.BASE_URL, params=local_params, timeout=45)
            if response.status_code == 429 and attempt < max_attempts - 1:
                time.sleep(self.request_delay * (attempt + 1))
                continue
            response.raise_for_status()
            return response.json()

        raise RuntimeError("unreachable OpenAlex request state")

    @staticmethod
    def _parse_authors(authorships: List[Dict]) -> List[str]:
        authors: List[str] = []
        for item in authorships or []:
            author_name = ((item or {}).get("author")
                           or {}).get("display_name")
            if author_name:
                authors.append(author_name)
        return authors

    @staticmethod
    def _abstract_from_inverted_index(index: Optional[Dict]) -> str:
        if not index:
            return ""
        max_position = -1
        for positions in index.values():
            if positions:
                max_position = max(max_position, max(positions))
        if max_position < 0:
            return ""
        tokens = [""] * (max_position + 1)
        for word, positions in index.items():
            for pos in positions:
                if 0 <= pos <= max_position:
                    tokens[pos] = word
        return " ".join(token for token in tokens if token)

    @staticmethod
    def _is_recent(publication_date: str, years: int) -> bool:
        if not publication_date:
            return False
        try:
            date_obj = datetime.strptime(publication_date, "%Y-%m-%d")
        except ValueError:
            return False
        cutoff = datetime.utcnow() - timedelta(days=365 * years)
        return date_obj >= cutoff

    @staticmethod
    def _match_any_alias(text: str, aliases: Iterable[str]) -> bool:
        lowered = (text or "").lower()
        for alias in aliases:
            if alias.lower() in lowered:
                return True
        return False

    def _extract_pdf_url(self, result: Dict) -> Optional[str]:
        locations = result.get("locations") or []
        for loc in locations:
            pdf_url = loc.get("pdf_url")
            if pdf_url:
                return pdf_url
            landing_page = loc.get("landing_page_url")
            if landing_page and landing_page.lower().endswith(".pdf"):
                return landing_page

        primary_location = result.get("primary_location") or {}
        pdf_url = primary_location.get("pdf_url")
        if pdf_url:
            return pdf_url

        best_oa = result.get("best_oa_location") or {}
        pdf_url = best_oa.get("pdf_url")
        if pdf_url:
            return pdf_url
        return None

    def _normalize_paper(self, result: Dict, target_venue: str) -> Dict:
        source_obj = ((result.get("primary_location")
                      or {}).get("source") or {})
        venue_name = source_obj.get("display_name") or target_venue

        return {
            "title": result.get("title") or "",
            "authors": self._parse_authors(result.get("authorships") or []),
            "abstract": self._abstract_from_inverted_index(result.get("abstract_inverted_index")),
            "doi": result.get("doi"),
            "openalex_id": result.get("id"),
            "publication_date": result.get("publication_date"),
            "year": result.get("publication_year"),
            "venue": venue_name,
            "source": "openalex",
            "source_url": result.get("id"),
            "pdf_url": self._extract_pdf_url(result),
            "oa_url": ((result.get("primary_location") or {}).get("landing_page_url")),
            "is_open_access": (result.get("open_access") or {}).get("is_oa", False),
            "cited_by_count": result.get("cited_by_count", 0),
        }

    def search(
        self,
        query: str,
        venue_name: str,
        venue_aliases: List[str],
        max_results: int = 200,
        years: int = 3,
    ) -> List[Dict]:
        per_page = 200
        cursor = "*"
        papers: List[Dict] = []

        from_date = (datetime.utcnow() -
                     timedelta(days=365 * years)).strftime("%Y-%m-%d")
        filters = [f"from_publication_date:{from_date}"]

        while len(papers) < max_results:
            params = {
                "search": query,
                "filter": ",".join(filters),
                "cursor": cursor,
                "per-page": per_page,
                "sort": "publication_date:desc",
            }
            payload = self._request(params)
            results = payload.get("results") or []
            if not results:
                break

            for result in results:
                if len(papers) >= max_results:
                    break
                source_display = (((result.get("primary_location") or {}).get(
                    "source") or {}).get("display_name") or "")
                host_venue = (
                    ((result.get("host_venue") or {}).get("display_name") or ""))
                if not (
                    self._match_any_alias(source_display, venue_aliases)
                    or self._match_any_alias(host_venue, venue_aliases)
                ):
                    continue

                publication_date = result.get("publication_date")
                if not self._is_recent(publication_date, years):
                    continue
                paper = self._normalize_paper(result, target_venue=venue_name)
                papers.append(paper)

            meta = payload.get("meta") or {}
            next_cursor = meta.get("next_cursor")
            if not next_cursor or next_cursor == cursor:
                break
            cursor = next_cursor
            time.sleep(self.request_delay)

        return papers


def save_json(path: str, data: List[Dict]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="OpenAlex venue crawler")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--venue", required=True, help="Venue display name")
    parser.add_argument("--aliases", required=True, nargs="+",
                        help="Venue aliases for matching")
    parser.add_argument("--max-results", type=int,
                        default=200, help="Maximum number of results")
    parser.add_argument("--years", type=int, default=3,
                        help="Recent years window")
    parser.add_argument("--output", required=True, help="Output JSON path")
    parser.add_argument("--mailto", default=None,
                        help="Email for OpenAlex courtesy pool")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    crawler = OpenAlexCrawler(mailto=args.mailto)
    papers = crawler.search(
        query=args.query,
        venue_name=args.venue,
        venue_aliases=args.aliases,
        max_results=args.max_results,
        years=args.years,
    )
    save_json(args.output, papers)
    print(f"Saved {len(papers)} papers to {args.output}")


if __name__ == "__main__":
    main()
