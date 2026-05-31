#!/usr/bin/env python3
"""
CCF A/B venue helper using arXiv metadata and externally supplied queries.
Loads venue data from ccf_venues_systems.json.
"""

import argparse
import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import arxiv
import requests


def load_ccf_venues() -> Dict[str, List[str]]:
    """Load CCF venues from JSON file."""
    json_path = Path(__file__).parent.parent / \
        "references" / "ccf_venues_all.json"

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    venues = {}

    # Extract from all categories
    for category_name, category_data in data['categories'].items():
        # Extract conferences
        for tier in ['A', 'B', 'C']:
            for conf in category_data.get('conferences', {}).get(tier, []):
                abbr = conf.get('abbr', '')
                full_name = conf.get('full_name', '')
                if abbr:
                    venues[abbr] = [abbr, full_name]

        # Extract journals
        for tier in ['A', 'B', 'C']:
            for journal in category_data.get('journals', {}).get(tier, []):
                abbr = journal.get('abbr', '')
                full_name = journal.get('full_name', '')
                if abbr:
                    venues[abbr] = [abbr, full_name]

    return venues


# Load CCF venues from JSON
CCF_VENUES = load_ccf_venues()

# arXiv categories
ARXIV_CATEGORIES = [
    # 人工智能与机器学习
    "cs.AI", "cs.LG", "cs.CV", "cs.CL", "cs.RO", "cs.MM", "cs.HC",
    # 系统与架构
    "cs.AR", "cs.OS", "cs.DC", "cs.PF", "cs.SY",
    # 网络与安全
    "cs.NI", "cs.CR", "cs.MA",
    # 软件工程与编程语言
    "cs.SE", "cs.PL", "cs.FL", "cs.LO",
    # 数据库与信息检索
    "cs.DB", "cs.IR", "cs.DL",
    # 理论计算机科学
    "cs.TH", "cs.CC", "cs.DM", "cs.GT",
    # 图形学与其他计算机科学子领域
    "cs.GR", "cs.CG", "cs.IT", "cs.CE", "cs.ET",
    # 统计学
    "stat.ML", "stat.CO", "stat.TH", "stat.AP",
    # 电气工程与系统科学
    "eess.SP", "eess.IV", "eess.SY",
    # 数学（与计算机科学高度相关）
    "math.OC", "math.PR", "math.ST"
]


def is_recent(date_obj: datetime, years: int = 3) -> bool:
    cutoff = datetime.utcnow() - timedelta(days=365 * years)
    return date_obj.replace(tzinfo=None) >= cutoff


def normalize_title(title: str) -> str:
    import re
    return re.sub(r"[^a-z0-9\s]", "", title.lower()).strip()


def title_similarity(a: str, b: str) -> float:
    a_words = set(normalize_title(a).split())
    b_words = set(normalize_title(b).split())
    if not a_words or not b_words:
        return 0.0
    return len(a_words & b_words) / len(a_words | b_words)


def crawl_arxiv(
    queries: List[str],
    categories: List[str],
    years: int = 3,
    max_per_query: int = 100,
) -> List[Dict]:
    client = arxiv.Client(page_size=100, delay_seconds=3.0, num_retries=3)
    seen_ids = set()
    papers = []

    for query in queries:
        cat_filter = " OR ".join(f"cat:{c}" for c in categories)
        full_query = f"({query}) AND ({cat_filter})"

        search = arxiv.Search(
            query=full_query,
            max_results=max_per_query,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending,
        )

        try:
            for result in client.results(search):
                if result.entry_id in seen_ids:
                    continue
                if not is_recent(result.published, years):
                    continue

                seen_ids.add(result.entry_id)
                arxiv_id = result.entry_id.split("/abs/")[-1]

                paper = {
                    "title": result.title,
                    "authors": [a.name for a in result.authors],
                    "abstract": result.summary,
                    "arxiv_id": arxiv_id,
                    "pdf_url": result.pdf_url,
                    "publication_date": result.published.strftime("%Y-%m-%d"),
                    "year": result.published.year,
                    "venue": detect_venue(result.title + " " + result.summary + " " + " ".join(result.categories)),
                    "categories": result.categories,
                    "provider": "arxiv",
                    "provider_id": arxiv_id,
                    "source": "arxiv",
                    "source_url": result.entry_id,
                    "openalex_id": "",
                    "semantic_scholar_id": "",
                    "cited_by_count": 0,
                    "doi": None,
                }
                papers.append(paper)
        except Exception as e:
            print(f"[WARN] Query '{query[:50]}' failed: {e}")
            time.sleep(5)
            continue

        time.sleep(2)

    return papers


def detect_venue(text: str) -> str:
    text_lower = text.lower()
    for venue, aliases in CCF_VENUES.items():
        for alias in aliases:
            if alias.lower() in text_lower:
                return venue
    return "arXiv"


def download_pdf(pdf_url: str, out_path: str, timeout: int = 60) -> bool:
    try:
        resp = requests.get(pdf_url, timeout=timeout, allow_redirects=True)
        if resp.status_code == 200 and (
            "pdf" in resp.headers.get("Content-Type", "").lower()
            or resp.content[:4] == b"%PDF"
        ):
            with open(out_path, "wb") as f:
                f.write(resp.content)
            return True
    except Exception as e:
        print(f"[WARN] PDF download failed {pdf_url}: {e}")
    return False


def save_abstract(paper: Dict, abstracts_dir: str) -> None:
    safe_id = paper["arxiv_id"].replace("/", "_").replace(".", "_")
    path = os.path.join(abstracts_dir, f"{safe_id}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"Title: {paper['title']}\n\n")
        f.write(f"Authors: {', '.join(paper['authors'][:5])}\n\n")
        f.write(f"Venue: {paper['venue']}\n\n")
        f.write(f"Date: {paper['publication_date']}\n\n")
        f.write(f"Source URL: {paper['source_url']}\n\n")
        f.write(f"Categories: {', '.join(paper.get('categories', []))}\n\n")
        f.write("Abstract:\n")
        f.write(paper.get("abstract", "") + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="CCF A/B arXiv helper for externally supplied queries")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--years", type=int, default=3)
    parser.add_argument("--max-per-query", type=int, default=80)
    parser.add_argument("--output-dir", default="./papers")
    parser.add_argument("--download-pdf", action="store_true")
    parser.add_argument("--no-download", action="store_true")
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    pdfs_dir = out_dir / "pdfs"
    abstracts_dir = out_dir / "abstracts"
    metadata_dir = out_dir / "metadata"
    for d in [pdfs_dir, abstracts_dir, metadata_dir]:
        d.mkdir(parents=True, exist_ok=True)

    print(
        f"Crawling arXiv for query '{args.query}' (last {args.years} years)...")
    papers = crawl_arxiv(
        queries=[args.query],
        categories=ARXIV_CATEGORIES,
        years=args.years,
        max_per_query=args.max_per_query,
    )

    # Deduplicate by arxiv_id
    seen = set()
    deduped = []
    for p in papers:
        if p["arxiv_id"] not in seen:
            seen.add(p["arxiv_id"])
            deduped.append(p)

    print(f"Raw: {len(papers)}, Deduped: {len(deduped)}")

    # Save abstracts
    for paper in deduped:
        save_abstract(paper, str(abstracts_dir))

    # Download PDFs
    download_stats = {"success": 0, "failed": 0, "skipped": 0}
    if args.download_pdf and not args.no_download:
        print(f"Downloading PDFs for {len(deduped)} papers...")
        for i, paper in enumerate(deduped):
            safe_id = paper["arxiv_id"].replace("/", "_").replace(".", "_")
            out_path = str(pdfs_dir / f"{safe_id}.pdf")
            if os.path.exists(out_path):
                paper["pdf_local_path"] = out_path
                download_stats["skipped"] += 1
                continue
            if paper.get("pdf_url"):
                ok = download_pdf(paper["pdf_url"], out_path)
                if ok:
                    paper["pdf_local_path"] = out_path
                    download_stats["success"] += 1
                else:
                    download_stats["failed"] += 1
            else:
                download_stats["skipped"] += 1
            if (i + 1) % 10 == 0:
                print(f"  Progress: {i+1}/{len(deduped)}")
            time.sleep(1.5)

    # Save metadata
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    metadata_path = metadata_dir / f"papers_{timestamp}.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(deduped, f, ensure_ascii=False, indent=2)

    # Venue distribution
    venue_counts = {}
    for p in deduped:
        v = p.get("venue", "arXiv")
        venue_counts[v] = venue_counts.get(v, 0) + 1

    summary = {
        "query": args.query,
        "query_count": 1,
        "raw_count": len(papers),
        "deduped_count": len(deduped),
        "final_count": len(deduped),
        "venue_distribution": venue_counts,
        "download_stats": download_stats,
        "years": args.years,
        "metadata_output": str(metadata_path),
        "timestamp": timestamp,
    }

    summary_path = metadata_dir / f"summary_{timestamp}.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return str(metadata_path)


if __name__ == "__main__":
    main()
