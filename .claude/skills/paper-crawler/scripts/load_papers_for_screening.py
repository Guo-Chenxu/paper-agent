#!/usr/bin/env python3
"""
Load papers from crawler output for screening in Claude conversation.
No external API calls - screening happens via Claude subagents.
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List


def load_papers_from_abstracts(abstracts_dir: str) -> List[Dict]:
    """Load papers from abstract text files."""
    papers = []
    for txt_file in sorted(Path(abstracts_dir).glob("*.txt")):
        content = txt_file.read_text(encoding="utf-8")
        paper = {"arxiv_id": txt_file.stem}
        for line in content.split("\n"):
            if line.startswith("Title: "):
                paper["title"] = line[7:].strip()
            elif line.startswith("Authors: "):
                paper["authors"] = [a.strip() for a in line[9:].split(",")]
            elif line.startswith("Venue: "):
                paper["venue"] = line[7:].strip()
            elif line.startswith("Date: "):
                paper["publication_date"] = line[6:].strip()
                try:
                    paper["year"] = int(line[6:10])
                except:
                    pass
            elif line.startswith("ArXiv: "):
                paper["source_url"] = line[7:].strip()
        # Extract abstract
        if "Abstract:\n" in content:
            paper["abstract"] = content.split("Abstract:\n", 1)[1].strip()
        if paper.get("title"):
            papers.append(paper)
    return papers


def main():
    parser = argparse.ArgumentParser(
        description="Load papers for screening in Claude conversation"
    )
    parser.add_argument("--abstracts-dir", default="./papers/abstracts")
    parser.add_argument("--metadata-dir", default="./papers/metadata")
    parser.add_argument("--output", default="screening_input.json")
    args = parser.parse_args()

    # Load papers from abstracts
    papers = load_papers_from_abstracts(args.abstracts_dir)

    # Try to merge with metadata JSON if available
    metadata_files = sorted(Path(args.metadata_dir).glob("papers_*.json"))
    if metadata_files:
        with open(metadata_files[-1]) as f:
            meta_papers = json.load(f)
        # Merge: use metadata as primary, fill missing abstracts from txt files
        meta_by_id = {p.get("arxiv_id", ""): p for p in meta_papers if p.get("arxiv_id")}
        txt_by_id = {p.get("arxiv_id", ""): p for p in papers}
        merged = []
        for arxiv_id, mp in meta_by_id.items():
            if not mp.get("abstract") and arxiv_id in txt_by_id:
                mp["abstract"] = txt_by_id[arxiv_id].get("abstract", "")
            merged.append(mp)
        # Add any txt-only papers
        for arxiv_id, tp in txt_by_id.items():
            if arxiv_id not in meta_by_id:
                merged.append(tp)
        papers = merged

    print(f"Loaded {len(papers)} papers for screening")

    # Save to output file
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(papers, f, ensure_ascii=False, indent=2)

    print(f"Saved to {output_path}")
    print(f"\nNext steps:")
    print(f"1. Read the papers from {output_path}")
    print(f"2. Spawn 3 parallel subagents with different reviewer personas")
    print(f"3. Each agent scores papers on innovation (1-4), impact (1-3), relevance (1-3)")
    print(f"4. Aggregate scores and filter papers with avg_total >= 7.0")
    print(f"5. Generate structured summaries for passed papers")
    print(f"6. Create screening report")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
