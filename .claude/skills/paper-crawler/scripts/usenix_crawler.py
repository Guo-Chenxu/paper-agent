import argparse
import json
import os
import re
import time
from datetime import datetime
from html import unescape
from html.parser import HTMLParser
from typing import Dict, Iterable, List, Optional
from urllib.parse import urljoin, urlparse

import requests

from paper_record import normalize_title, safe_token


BASE_URL = "https://www.usenix.org"
VENUE_NAMES = {
    "osdi": "OSDI",
    "nsdi": "NSDI",
    "atc": "USENIX ATC",
}


def query_matches(paper: Dict, query: str) -> bool:
    terms = [term for term in re.split(r"\s+", normalize_title(query)) if term not in {"or", "and"}]
    haystack = normalize_title((paper.get("title") or "") + " " + (paper.get("abstract") or ""))
    return bool(terms) and any(term in haystack for term in terms)


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links: List[Dict[str, str]] = []
        self._href = ""
        self._text_parts: List[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            attrs_dict = dict(attrs)
            self._href = attrs_dict.get("href", "")
            self._text_parts = []

    def handle_data(self, data):
        if self._href:
            self._text_parts.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._href:
            text = " ".join(part.strip() for part in self._text_parts if part.strip())
            self.links.append({"href": self._href, "text": text})
            self._href = ""
            self._text_parts = []


class UsenixCrawler:
    def __init__(self, request_delay: float = 0.5):
        self.request_delay = request_delay

    def _get(self, url: str) -> str:
        response = requests.get(url, timeout=45)
        response.raise_for_status()
        return response.text

    def _venue_year_paths(self, venues: Iterable[str], years: int, current_year: Optional[int] = None) -> List[str]:
        now = current_year or datetime.utcnow().year
        paths: List[str] = []
        for venue in venues:
            normalized = venue.lower()
            for year in range(now - years + 1, now + 1):
                short_year = str(year)[-2:]
                paths.append(f"/conference/{normalized}{short_year}/technical-sessions")
        return paths

    def _extract_paper_links(self, html: str) -> List[str]:
        parser = LinkParser()
        parser.feed(html)
        links = []
        for link in parser.links:
            href = link["href"]
            if "/presentation/" in href:
                links.append(urljoin(BASE_URL, href))
        return sorted(set(links))

    def _extract_title(self, html: str) -> str:
        match = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.IGNORECASE | re.DOTALL)
        if not match:
            return ""
        return re.sub(r"<[^>]+>", "", match.group(1)).strip()

    def _extract_pdf_url(self, html: str) -> str:
        parser = LinkParser()
        parser.feed(html)
        for link in parser.links:
            href = link["href"]
            text = link["text"].lower()
            if href.lower().endswith(".pdf") or "paper pdf" in text or text == "pdf":
                return urljoin(BASE_URL, href)
        return ""

    def _extract_abstract(self, html: str) -> str:
        match = re.search(r"<h2[^>]*>\s*Abstract\s*</h2>(.*?)(<h2|</section|</div>)", html, re.IGNORECASE | re.DOTALL)
        if not match:
            return ""
        text = re.sub(r"<[^>]+>", " ", match.group(1))
        return " ".join(text.split())

    def _extract_authors(self, html: str) -> List[str]:
        authors: List[str] = []
        for match in re.finditer(r"<meta\s+[^>]*>", html, re.IGNORECASE):
            tag = match.group(0)
            if not re.search(r"name=[\"']citation_author[\"']", tag, re.IGNORECASE):
                continue
            content = re.search(r"content=[\"']([^\"']+)[\"']", tag, re.IGNORECASE)
            if content:
                authors.append(unescape(content.group(1)).strip())
        return authors

    def _normalize_entry(self, entry: Dict) -> Dict:
        source_url = entry.get("source_url") or ""
        path = urlparse(source_url).path.strip("/")
        if path.startswith("conference/"):
            path = path[len("conference/"):]
        provider_id = safe_token(path)
        return {
            "title": entry.get("title") or "",
            "authors": entry.get("authors") or [],
            "abstract": entry.get("abstract") or "",
            "year": entry.get("year"),
            "publication_date": f"{entry.get('year')}-01-01" if entry.get("year") else "",
            "venue": entry.get("venue") or "",
            "provider": "usenix",
            "provider_id": provider_id,
            "source": "usenix",
            "source_url": source_url,
            "pdf_url": entry.get("pdf_url") or "",
            "doi": "",
            "arxiv_id": "",
            "openalex_id": "",
            "semantic_scholar_id": "",
            "cited_by_count": 0,
        }

    def search(self, query: str, venues: Iterable[str], max_results: int = 100, years: int = 3) -> List[Dict]:
        papers: List[Dict] = []
        current_year = datetime.utcnow().year
        for path in self._venue_year_paths(venues, years=years, current_year=current_year):
            page_url = urljoin(BASE_URL, path)
            try:
                page_html = self._get(page_url)
            except requests.RequestException:
                continue
            for paper_url in self._extract_paper_links(page_html):
                if len(papers) >= max_results:
                    return papers
                try:
                    paper_html = self._get(paper_url)
                except requests.RequestException:
                    continue
                venue_token = path.split("/conference/", 1)[1].split("/", 1)[0]
                venue_key = re.sub(r"\d+$", "", venue_token)
                year_match = re.search(r"(\d{2})$", venue_token)
                year = 2000 + int(year_match.group(1)) if year_match else current_year
                entry = {
                    "title": self._extract_title(paper_html),
                    "authors": self._extract_authors(paper_html),
                    "abstract": self._extract_abstract(paper_html),
                    "year": year,
                    "venue": VENUE_NAMES.get(venue_key, venue_key.upper()),
                    "source_url": paper_url,
                    "pdf_url": self._extract_pdf_url(paper_html),
                }
                paper = self._normalize_entry(entry)
                if query_matches(paper, query):
                    papers.append(paper)
                time.sleep(self.request_delay)
            time.sleep(self.request_delay)
        return papers


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="USENIX proceedings crawler")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--usenix-venues", nargs="+", default=["osdi"], help="USENIX venues such as osdi nsdi atc")
    parser.add_argument("--max-results", type=int, default=100, help="Maximum number of results")
    parser.add_argument("--years", type=int, default=3, help="Recent years window")
    parser.add_argument("--output", required=True, help="Output JSON path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    crawler = UsenixCrawler()
    papers = crawler.search(args.query, venues=args.usenix_venues, max_results=args.max_results, years=args.years)
    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as file_obj:
        json.dump(papers, file_obj, ensure_ascii=False, indent=2)
    print(f"USENIX papers: {len(papers)} -> {args.output}")


if __name__ == "__main__":
    main()
