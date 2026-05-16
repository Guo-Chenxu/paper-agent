#!/usr/bin/env python3
"""Export local Claude Code subagent prompt packs for research idea generation."""

from __future__ import annotations

import argparse
import datetime
from pathlib import Path


def load_summaries(summaries_dir: str, max_papers: int = 50) -> str:
    files = sorted(Path(summaries_dir).glob("*_summary.md"))[:max_papers]
    if not files:
        raise SystemExit(f"No *_summary.md files found in {summaries_dir}")

    summaries: list[str] = []
    for file_path in files:
        content = file_path.read_text(encoding="utf-8")
        lines = content.splitlines()
        title = lines[0].replace("# ", "").strip() if lines else file_path.stem
        score_line = next((line for line in lines if "Score" in line or "score" in line), "")
        sections: list[str] = []
        current: list[str] = []
        for line in lines:
            if line.startswith("## "):
                if current:
                    sections.append("\n".join(current))
                current = [line]
            else:
                current.append(line)
        if current:
            sections.append("\n".join(current))

        excerpt = "\n".join(section[:500] for section in sections[:4])
        summaries.append(f"**{title}**\n{score_line}\n{excerpt}")
    return "\n\n---\n\n".join(summaries)


def build_prompt_pack(context: str) -> str:
    generated_at = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    return f"""# Local Idea Generation Prompt Pack

**Generated:** {generated_at}

Use `.claude/skills/paper-crawler/references/idea-generation.md` with local Claude Code subagents. Do not send this prompt pack to an external service.

## Paper Context

{context}

## Landscape Analysis Prompt

Analyze the recent papers above. Identify well-solved problems, open research gaps, recurring limitations, cross-domain opportunities, and emerging trends in distributed systems and resource scheduling.

## Independent Agent Prompts

### Agent 1: Systems Scheduling Researcher

Generate exactly 5 novel research ideas. Focus on scheduling algorithms, resource efficiency, heterogeneous computing, and ML-driven optimization. For each idea include title, problem, innovation, approach, experiment, and expected contribution.

### Agent 2: Cloud Infrastructure Researcher

Generate exactly 5 practical but publishable research ideas. Focus on Kubernetes, serverless computing, autoscaling, tail latency, energy efficiency, and multi-tenant systems. For each idea include title, problem, innovation, approach, experiment, and expected contribution.

### Agent 3: ML Systems Researcher

Generate exactly 5 research ideas at the intersection of ML systems and distributed systems. Focus on LLM serving, GPU cluster scheduling, memory management, communication optimization, and resource management. For each idea include title, problem, innovation, approach, experiment, and expected contribution.

## Evaluation Prompt

Evaluate every generated idea with this rubric:

- Innovation: 1-4
- Feasibility: 1-3
- Impact: 1-3

Return a ranked table and select the top three ideas for elaboration. Be strict about novelty, implementation effort, and evaluation feasibility.

## Elaboration Prompt

For each selected idea, write a detailed proposal with research background, precise problem statement, core technical approach, experimental design, expected contributions, and key risks.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Export local subagent prompt packs for paper ideas.")
    parser.add_argument("--summaries-dir", default="./paper_summaries")
    parser.add_argument("--reports-dir", default="./reports")
    parser.add_argument("--max-papers", type=int, default=50)
    args = parser.parse_args()

    context = load_summaries(args.summaries_dir, args.max_papers)
    reports_dir = Path(args.reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)
    output = reports_dir / f"{Path(__file__).stem}.md"
    output.write_text(build_prompt_pack(context), encoding="utf-8")
    print(f"Prompt pack saved to {output}")


if __name__ == "__main__":
    main()
