import argparse
from typing import List

from openalex_crawler import OpenAlexCrawler, save_json


OSDI_ALIASES: List[str] = [
    "osdi",
    "operating systems design and implementation",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Find OSDI papers via the OpenAlex compatibility wrapper")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--max-results", type=int,
                        default=200, help="Maximum number of results")
    parser.add_argument("--years", type=int, default=3,
                        help="Recent years window")
    parser.add_argument("--output", required=True, help="Output JSON file")
    parser.add_argument("--mailto", default=None,
                        help="Email for OpenAlex courtesy pool")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    crawler = OpenAlexCrawler(mailto=args.mailto)
    papers = crawler.search(
        query=args.query,
        venue_name="OSDI",
        venue_aliases=OSDI_ALIASES,
        max_results=args.max_results,
        years=args.years,
    )
    save_json(args.output, papers)
    print(f"OSDI papers: {len(papers)} -> {args.output}")


if __name__ == "__main__":
    main()
