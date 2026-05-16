#!/usr/bin/env python3
"""Export local Claude Code subagent prompt packs for traditional scheduling ideas."""

from __future__ import annotations

import argparse
import datetime
from pathlib import Path


SCHEDULING_KEYWORDS = [
    "schedul",
    "gang",
    "job",
    "queue",
    "fairness",
    "preempt",
    "backfill",
    "placement",
    "allocation",
    "cluster",
    "workload",
    "deadline",
    "priority",
    "coflow",
    "makespan",
    "throughput",
    "latency",
    "resource",
    "bin pack",
    "work steal",
    "load balanc",
    "heterogeneous",
    "multi-resource",
]

SERVER_CONTEXT = """Available experiment environment:
- Single multi-core server with 16-64 CPU cores
- 64-256 GB RAM
- Standard Linux OS
- Python, C++, and Java available
- Simulation through threads, processes, or containers
- Public workload traces such as Google cluster trace and Alibaba cluster trace
- No access to a large production cluster
"""


def load_summaries(summaries_dir: str, max_papers: int = 60) -> str:
    files = sorted(Path(summaries_dir).glob("*_summary.md"))
    if not files:
        files = sorted(Path(summaries_dir).glob("*.md"))
    if not files:
        raise SystemExit(f"No summary markdown files found in {summaries_dir}")

    scored_files: list[tuple[int, Path]] = []
    for file_path in files:
        text = file_path.read_text(encoding="utf-8").lower()
        score = sum(1 for keyword in SCHEDULING_KEYWORDS if keyword in text)
        scored_files.append((score, file_path))
    scored_files.sort(key=lambda item: (item[0], item[1].name), reverse=True)

    summaries: list[str] = []
    for _, file_path in scored_files[:max_papers]:
        content = file_path.read_text(encoding="utf-8")
        lines = content.splitlines()
        title = lines[0].replace("# ", "").strip() if lines else file_path.stem
        score_line = next((line for line in lines if "Score" in line or "score" in line), "")
        body = "\n".join(lines[1:])[:1000]
        summaries.append(f"**{title}**\n{score_line}\n{body}")
    return "\n\n---\n\n".join(summaries)


def build_prompt_pack(context: str) -> str:
    generated_at = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    return f"""# Local Traditional Scheduling Idea Prompt Pack

**Generated:** {generated_at}

Use `.claude/skills/paper-crawler/references/idea-generation.md` with local Claude Code subagents. Focus on traditional distributed scheduling rather than LLM-specific systems. Do not send this prompt pack to an external service.

## Feasibility Context

{SERVER_CONTEXT}

## Paper Context

{context}

## Landscape Analysis Prompt

Analyze the recent scheduling-related papers above. Identify well-solved scheduling problems, open gaps, recurring evaluation limitations, and practical opportunities that can be validated on a single server.

## Independent Agent Prompts

### Agent 1: Distributed Job Scheduling Researcher

Generate exactly 5 ideas about gang scheduling, fair scheduling, job queues, preemption, backfilling, coflow scheduling, and multi-resource allocation. Each idea must be feasible with simulation or small-scale experiments on one server.

### Agent 2: HPC and Cloud Scheduling Researcher

Generate exactly 5 ideas about heterogeneous clusters, deadline-aware scheduling, fairness mechanisms, resource fragmentation, and production workload traces. Each idea must name baselines and measurable metrics.

### Agent 3: Distributed Task Scheduling Researcher

Generate exactly 5 ideas about work stealing, load balancing, topology-aware placement, interference-aware co-scheduling, spot instances, checkpoint-based preemption, and multi-tenant scheduling.

## Required Idea Fields

For each idea include title, problem, gap, innovation, approach, experiment, baselines, expected result, and feasibility risks.

## Evaluation Prompt

Score every idea with innovation 1-4, feasibility 1-3, and impact 1-3. Penalize ideas that need a large real cluster without a simulation alternative. Select the top three ideas and explain the selection.

## Elaboration Prompt

For each selected idea, write a detailed proposal with research background, precise problem statement, core algorithm or system design, trace-driven experimental design, expected contributions, and mitigation for feasibility risks.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Export local subagent prompt packs for traditional scheduling ideas.")
    parser.add_argument("--summaries-dir", default="./paper_summaries")
    parser.add_argument("--reports-dir", default="./reports")
    parser.add_argument("--max-papers", type=int, default=60)
    args = parser.parse_args()

    context = load_summaries(args.summaries_dir, args.max_papers)
    reports_dir = Path(args.reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)
    output = reports_dir / f"{Path(__file__).stem}.md"
    output.write_text(build_prompt_pack(context), encoding="utf-8")
    print(f"Prompt pack saved to {output}")


if __name__ == "__main__":
    main()
