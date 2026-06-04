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
    parser.add_argument("--pdfs-dir", default="./papers/pdfs")
    parser.add_argument("--output", default="screening_input.json")
    args = parser.parse_args()

    # Validate directories exist
    abstracts_path = Path(args.abstracts_dir)
    if not abstracts_path.is_dir():
        print(f"ERROR: abstracts directory not found: {args.abstracts_dir}")
        print("Run the crawler first to generate abstract files.")
        return 1

    # Load papers from abstracts
    papers = load_papers_from_abstracts(args.abstracts_dir)

    if not papers:
        print("WARNING: no papers loaded from abstracts directory.")
        print("Check that the directory contains .txt files with Title: and Abstract: fields.")
        return 1

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

    # Validate abstracts: warn about papers with empty or missing abstracts
    no_abstract = [p.get("arxiv_id", "?") for p in papers if not p.get("abstract", "").strip()]
    if no_abstract:
        print(f"WARNING: {len(no_abstract)} paper(s) have empty or missing abstracts: {no_abstract}")
        print("Papers without abstracts will produce unreliable Round 1 scores.")

    # Add PDF paths for Round 2
    pdfs_dir = Path(args.pdfs_dir)
    pdf_available = 0
    for paper in papers:
        arxiv_id = paper.get("arxiv_id", "")
        pdf_path = pdfs_dir / f"{arxiv_id}.pdf"
        if pdf_path.is_file():
            paper["pdf_path"] = str(pdf_path)
            pdf_available += 1
        else:
            paper["pdf_path"] = None
    if pdf_available < len(papers):
        missing = len(papers) - pdf_available
        print(f"NOTE: {missing} paper(s) missing PDFs. These will need PDF download before Round 2.")

    print(f"Loaded {len(papers)} papers for screening")

    # Save to output file
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(papers, f, ensure_ascii=False, indent=2)

    print(f"Saved to {output_path}")
    print(f"\nNext steps:")
    print(f"  Round 1 (Title+Abstract Pre-Screening):")
    print(f"  1. Read the papers from {output_path}")
    print(f"  2. Spawn 3 parallel subagents (Senior Researcher, Professor, Industry Researcher)")
    print(f"  3. Each agent scores on: relevance (5pts) + potential innovation (3pts) + publication quality (2pts) = 10pts")
    print(f"  4. Papers with avg_total >= 5.0 across 3 agents advance to Round 2")
    print(f"  Round 2 (Full-Text Deep Screening):")
    print(f"  5. Download PDFs for Round 2 papers missing from {args.pdfs_dir}")
    print(f"  6. Spawn 3 parallel subagents reading full PDFs")
    print(f"  7. Each agent scores on: innovation (4pts) + impact (3pts) + relevance (3pts) = 10pts")
    print(f"  8. Papers with avg_total >= 7.0 across 3 agents are selected for summarization")
    print(f"  9. Generate structured summaries for selected papers")
    print(f"  10. Create screening report")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
