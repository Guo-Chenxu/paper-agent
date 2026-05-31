#!/usr/bin/env python3
"""
Export research idea generation prompt pack from paper summaries.
Dynamically generates agent prompts based on research domain context.
"""

from __future__ import annotations

import argparse
import datetime
import json
from pathlib import Path


def load_summaries(summaries_dir: str, max_papers: int | None = None) -> list[dict]:
    """Load all paper summaries from directory."""
    files = sorted(Path(summaries_dir).glob("*_summary.md"))
    if not files:
        files = sorted(Path(summaries_dir).glob("*.md"))
    if not files:
        raise SystemExit(f"No summary markdown files found in {summaries_dir}")

    summaries = []
    for file_path in files[:max_papers] if max_papers else files:
        content = file_path.read_text(encoding="utf-8")
        lines = content.splitlines()
        title = lines[0].replace("# ", "").strip() if lines else file_path.stem

        # Extract score if available
        score_line = next((line for line in lines if "Score" in line or "score" in line), "")

        # Extract body (limit to first 1000 chars to keep context manageable)
        body = "\n".join(lines[1:])[:1000]

        summaries.append({
            "title": title,
            "score_line": score_line,
            "body": body,
            "file": str(file_path)
        })

    return summaries


def format_summaries_context(summaries: list[dict]) -> str:
    """Format summaries into context string."""
    formatted = []
    for s in summaries:
        formatted.append(f"**{s['title']}**\n{s['score_line']}\n{s['body']}")
    return "\n\n---\n\n".join(formatted)


def build_prompt_pack(
    research_domain: str,
    summaries_context: str,
    num_agents: int = 3,
    ideas_per_agent: int = 5,
    experiment_constraints: str | None = None
) -> str:
    """Build a generic prompt pack for idea generation."""

    generated_at = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    constraints_section = ""
    if experiment_constraints:
        constraints_section = f"""
## Experiment Environment Constraints

{experiment_constraints}

All proposed ideas must be feasible within these constraints.
"""

    return f"""# Research Idea Generation Prompt Pack

**Generated:** {generated_at}
**Research Domain:** {research_domain}

Use this prompt pack with local Claude Code subagents. Do not send to external services.

## Paper Context

The following papers have been collected and screened for the research domain: **{research_domain}**

{summaries_context}
{constraints_section}

## Landscape Analysis Prompt

Analyze the papers above in the context of **{research_domain}**. Identify:

1. **Well-solved problems**: What has been thoroughly addressed
2. **Open research gaps**: What remains unsolved or partially solved
3. **Common limitations**: Shared weaknesses across existing methods
4. **Cross-domain opportunities**: Potential for technique transfer from other fields
5. **Emerging trends**: Recent breakthroughs applicable to this domain

Output a structured knowledge graph covering these dimensions.

## Independent Agent Prompts

You will spawn {num_agents} independent agents. Each agent should:
- Read all paper summaries and the knowledge graph
- Generate exactly {ideas_per_agent} distinct research ideas
- Use a different creative perspective

### Agent 1: Problem-Driven Researcher

Focus on **unsolved problems and pain points** in {research_domain}.

Generate exactly {ideas_per_agent} research ideas that address critical gaps or limitations identified in the papers. For each idea include:

- **Title**: Brief, descriptive (1 line)
- **Problem**: What specific problem does this address?
- **Innovation**: What makes this different from prior work?
- **Approach**: High-level methodology (2-3 sentences)
- **Experiment**: How would you validate this? (datasets, baselines, metrics)
- **Expected Contribution**: What impact would this have?

### Agent 2: Method-Driven Researcher

Focus on **novel techniques and algorithmic improvements** in {research_domain}.

Generate exactly {ideas_per_agent} research ideas that introduce new methods or significantly improve existing ones. For each idea include:

- **Title**: Brief, descriptive (1 line)
- **Problem**: What specific problem does this address?
- **Innovation**: What makes this different from prior work?
- **Approach**: High-level methodology (2-3 sentences)
- **Experiment**: How would you validate this? (datasets, baselines, metrics)
- **Expected Contribution**: What impact would this have?

### Agent 3: Application-Driven Researcher

Focus on **practical applications and system design** in {research_domain}.

Generate exactly {ideas_per_agent} research ideas that bridge theory and practice, or apply techniques to real-world systems. For each idea include:

- **Title**: Brief, descriptive (1 line)
- **Problem**: What specific problem does this address?
- **Innovation**: What makes this different from prior work?
- **Approach**: High-level methodology (2-3 sentences)
- **Experiment**: How would you validate this? (datasets, baselines, metrics)
- **Expected Contribution**: What impact would this have?

## Evaluation Prompt

Evaluate every generated idea ({num_agents} agents × {ideas_per_agent} ideas = {num_agents * ideas_per_agent} total) using this rubric:

- **Innovation** (1-4): Novelty, uniqueness, unexplored territory
- **Feasibility** (1-3): Implementation difficulty, resource requirements, time cost
- **Impact** (1-3): Potential contribution, publication prospects, real-world value
- **Total** (3-10): Sum of above scores

Output format:

```json
{{
  "ideas": [
    {{
      "id": 1,
      "agent": "Agent 1",
      "title": "...",
      "innovation": 4,
      "feasibility": 2,
      "impact": 3,
      "total": 9,
      "reason": "One sentence justification"
    }}
  ]
}}
```

Return a ranked table and select ideas with **total >= 8.0** as top candidates.

## Elaboration Prompt

For each top candidate (score >= 8.0), perform deep refinement:

1. **Expand background story**: Why this problem matters, historical context (2-3 paragraphs)
2. **Formulate research question**: Clear, specific, answerable question
3. **Define hypothesis**: Testable claim about expected outcomes
4. **Detail innovation**: What makes this different from prior work (2-3 paragraphs)
5. **Outline technical approach**: High-level methodology and key steps
6. **Sketch experimental plan**:
   - Datasets to use
   - Baseline methods to compare against
   - Evaluation metrics
   - Validation strategy

Output each elaborated idea as a structured markdown document.

## Quality Checks

Before completing, verify:

1. All {num_agents * ideas_per_agent} ideas have been generated
2. All ideas have evaluation scores
3. Top ideas (score >= 8.0) have detailed elaborations
4. All ideas are grounded in the paper context (cite specific papers when relevant)
5. All ideas are feasible within stated constraints (if any)
"""


def main():
    parser = argparse.ArgumentParser(
        description="Export research idea generation prompt pack"
    )
    parser.add_argument(
        "--summaries-dir",
        default="./paper_summaries",
        help="Directory containing paper summary markdown files"
    )
    parser.add_argument(
        "--research-domain",
        required=True,
        help="Research domain/field (e.g., 'machine learning', 'computer vision', 'natural language processing')"
    )
    parser.add_argument(
        "--max-papers",
        type=int,
        help="Maximum number of papers to include (default: all)"
    )
    parser.add_argument(
        "--num-agents",
        type=int,
        default=3,
        help="Number of idea generation agents (default: 3)"
    )
    parser.add_argument(
        "--ideas-per-agent",
        type=int,
        default=5,
        help="Number of ideas each agent should generate (default: 5)"
    )
    parser.add_argument(
        "--experiment-constraints",
        help="Optional experiment environment constraints (e.g., 'Single server, public traces only')"
    )
    parser.add_argument(
        "--output",
        default="./reports/idea_generation_prompt_pack.md",
        help="Output file path"
    )
    args = parser.parse_args()

    # Load summaries
    print(f"Loading paper summaries from {args.summaries_dir}...")
    summaries = load_summaries(args.summaries_dir, args.max_papers)
    print(f"Loaded {len(summaries)} paper summaries")

    # Format context
    summaries_context = format_summaries_context(summaries)

    # Build prompt pack
    print(f"Building prompt pack for research domain: {args.research_domain}")
    prompt_pack = build_prompt_pack(
        research_domain=args.research_domain,
        summaries_context=summaries_context,
        num_agents=args.num_agents,
        ideas_per_agent=args.ideas_per_agent,
        experiment_constraints=args.experiment_constraints
    )

    # Save output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(prompt_pack, encoding="utf-8")

    print(f"\nPrompt pack saved to: {output_path}")
    print(f"Total ideas to generate: {args.num_agents * args.ideas_per_agent}")
    print(f"\nNext steps:")
    print(f"1. Read the prompt pack: {output_path}")
    print(f"2. Spawn {args.num_agents} parallel subagents with the agent prompts")
    print(f"3. Collect and evaluate all generated ideas")
    print(f"4. Elaborate top ideas (score >= 8.0)")


if __name__ == "__main__":
    main()
