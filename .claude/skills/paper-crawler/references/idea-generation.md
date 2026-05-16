# Local Idea Generation Reference

Use this reference after paper summaries are available. Idea generation runs through local Claude Code subagents, not through external API scripts.

## Workflow

1. Run one prompt-export helper from the repository root:

```bash
python .claude/skills/paper-crawler/scripts/export_idea_prompts.py \
  --summaries-dir ./paper_summaries \
  --reports-dir ./reports \
  --max-papers 50
```

For traditional distributed scheduling, use:

```bash
python .claude/skills/paper-crawler/scripts/export_idea_prompts_traditional_scheduling.py \
  --summaries-dir ./paper_summaries \
  --reports-dir ./reports \
  --max-papers 60
```

2. Read the generated prompt pack under `reports/`.
3. Launch three independent local subagents in parallel. Give each subagent the shared paper context and one persona prompt.
4. Ask each subagent to generate exactly five ideas using the required fields.
5. Merge the ideas in the main session.
6. Evaluate and rank all ideas with the rubric below.
7. Expand the top three ideas into `reports/research_directions_and_ideas.md`.

## Subagent Personas

- **Systems Scheduling Researcher:** scheduling algorithms, resource efficiency, heterogeneous computing, and ML-driven optimization.
- **Cloud Infrastructure Researcher:** Kubernetes, serverless computing, autoscaling, tail latency, energy efficiency, and multi-tenant systems.
- **ML Systems Researcher:** LLM serving, GPU scheduling, memory management, communication optimization, and resource management.

For the traditional scheduling variant, replace the personas with:

- **Distributed Job Scheduling Researcher:** gang scheduling, fair scheduling, job queues, preemption, backfilling, and coflow scheduling.
- **HPC and Cloud Scheduling Researcher:** heterogeneous clusters, deadline-aware scheduling, fairness, fragmentation, and trace-driven evaluation.
- **Distributed Task Scheduling Researcher:** work stealing, load balancing, topology-aware placement, interference-aware co-scheduling, and checkpoint-based preemption.

## Required Idea Fields

Each idea should include:

- `title`
- `problem`
- `gap`
- `innovation`
- `approach`
- `experiment`
- `baselines`
- `expected_result`
- `risks`

## Evaluation Rubric

- **Innovation (1-4):** novelty of the problem, mechanism, algorithm, or system design.
- **Feasibility (1-3):** ability to implement and evaluate the idea within available time and hardware.
- **Impact (1-3):** expected value for systems research and publication potential.

Only ideas with clear technical novelty, realistic baselines, and measurable outcomes should score 8 or above.

## Report Format

Write `reports/research_directions_and_ideas.md` with these sections:

1. Research landscape and open gaps.
2. All generated ideas and scores.
3. Top three detailed ideas.
4. Experimental validation plan.
5. Feasibility risks and mitigations.

Also write `reports/all_ideas.json` when structured downstream processing is useful.
