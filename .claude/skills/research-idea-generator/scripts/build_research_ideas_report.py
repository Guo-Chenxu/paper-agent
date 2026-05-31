#!/usr/bin/env python3
"""
Build final research ideas report from evaluation results.
Generic version that works for any research domain.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_json(path: str) -> dict:
    """Load JSON file."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_text(path: str) -> str:
    """Load text file."""
    return Path(path).read_text(encoding="utf-8")


def idea_table(evaluations: list[dict]) -> str:
    """Generate markdown table of all ideas ranked by score."""
    rows = [
        "| Rank | Score | Innovation | Feasibility | Impact | Source | Title |",
        "|---:|---:|---:|---:|---:|---:|---|"
    ]

    ranked = sorted(evaluations, key=lambda item: (-item.get("total", 0), item.get("title", "")))

    for index, item in enumerate(ranked, start=1):
        title = item.get("title", "Untitled").replace("|", "/")
        source = item.get("source_agent", item.get("agent", "Unknown"))
        innovation = item.get("innovation", item.get("innovation_score", 0))
        feasibility = item.get("feasibility", item.get("feasibility_score", 0))
        impact = item.get("impact", item.get("impact_score", 0))
        total = item.get("total", item.get("total_score", 0))

        rows.append(
            f"| {index} | {total} | {innovation} | {feasibility} | {impact} | {source} | {title} |"
        )

    return "\n".join(rows)


def top_ideas_section(top_ideas: list[dict]) -> str:
    """Generate detailed section for top-ranked ideas."""
    sections = []

    for item in top_ideas:
        rank = item.get("rank", "?")
        title = item.get("title", "Untitled")
        source = item.get("source_agent", item.get("agent", "Unknown"))
        total = item.get("total_score", item.get("total", 0))
        reason = item.get("why_selected", item.get("reason", "No reason provided"))
        validation = item.get("required_validation", "Not specified")

        sections.append("\n".join([
            f"### Top {rank}: {title}",
            "",
            f"- Source Agent: {source}",
            f"- Total Score: {total}",
            f"- Selection Reason: {reason}",
            f"- Required Validation: {validation}",
        ]))

    return "\n\n".join(sections)


def build_report(
    knowledge_graph: str,
    evaluations: list[dict],
    top_ideas: list[dict],
    reviewer_attack: str,
    screening_stats: dict | None = None
) -> str:
    """Build complete research directions and ideas report."""

    # Build screening summary if stats provided
    screening_summary = ""
    if screening_stats:
        total = screening_stats.get("total_papers", "N/A")
        passed = screening_stats.get("passed_papers", "N/A")
        screening_summary = f"Stage 1 collected {total} papers and screened {passed} high-quality papers (score >= 7.0)."

    report_sections = [
        "# Research Directions and Ideas Report",
        "",
        "## Research Domain Overview and Gap Analysis",
        "",
    ]

    if screening_summary:
        report_sections.extend([screening_summary, ""])

    report_sections.extend([
        knowledge_graph,
        "",
        "## All Generated Ideas (Ranked by Score)",
        "",
        idea_table(evaluations),
        "",
        "## Top Ideas - Detailed Proposals",
        "",
        top_ideas_section(top_ideas),
        "",
        "## Adversarial Review and Refinement",
        "",
        reviewer_attack,
        "",
    ])

    return "\n".join(report_sections)


def main():
    parser = argparse.ArgumentParser(
        description="Build final research ideas report from evaluation results"
    )
    parser.add_argument(
        "--knowledge-graph",
        default="./reports/research_knowledge_graph.md",
        help="Path to knowledge graph markdown file"
    )
    parser.add_argument(
        "--evaluations",
        default="./reports/idea_evaluation_scores.json",
        help="Path to idea evaluation JSON file"
    )
    parser.add_argument(
        "--reviewer-attack",
        default="./reports/idea_reviewer_attack_trace.md",
        help="Path to reviewer attack trace markdown file"
    )
    parser.add_argument(
        "--screening-stats",
        help="Optional path to screening statistics JSON file"
    )
    parser.add_argument(
        "--output",
        default="./reports/research_directions_and_ideas.md",
        help="Output report path"
    )
    args = parser.parse_args()

    # Load inputs
    print("Loading knowledge graph...")
    knowledge_graph = load_text(args.knowledge_graph)

    print("Loading idea evaluations...")
    eval_data = load_json(args.evaluations)
    evaluations = eval_data.get("ideas", eval_data.get("evaluations", []))

    # Extract top ideas (score >= 8.0)
    top_ideas = [idea for idea in evaluations if idea.get("total", idea.get("total_score", 0)) >= 8.0]
    top_ideas.sort(key=lambda x: -x.get("total", x.get("total_score", 0)))

    # Add rank to top ideas
    for i, idea in enumerate(top_ideas, start=1):
        idea["rank"] = i

    print(f"Found {len(top_ideas)} top ideas (score >= 8.0)")

    print("Loading reviewer attack trace...")
    reviewer_attack = load_text(args.reviewer_attack)

    # Load optional screening stats
    screening_stats = None
    if args.screening_stats and Path(args.screening_stats).exists():
        print("Loading screening statistics...")
        screening_stats = load_json(args.screening_stats)

    # Build report
    print("Building final report...")
    report = build_report(
        knowledge_graph=knowledge_graph,
        evaluations=evaluations,
        top_ideas=top_ideas,
        reviewer_attack=reviewer_attack,
        screening_stats=screening_stats
    )

    # Save output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")

    print(f"\nReport saved to: {output_path}")
    print(f"Total ideas evaluated: {len(evaluations)}")
    print(f"Top ideas (score >= 8.0): {len(top_ideas)}")


if __name__ == "__main__":
    main()
