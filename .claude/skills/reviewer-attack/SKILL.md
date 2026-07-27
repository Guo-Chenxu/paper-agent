---
name: reviewer-attack
description: "Use for adversarial review of any research artifact — papers, experimental designs, or research ideas. Launches three independent, context-free reviewers (strict, constructive, newcomer) with a 0–5 scoring rubric. Each reviewer produces detailed scores and actionable feedback."
user-invocable: true
---

# Reviewer Attack Skill

## When To Use

This skill is the adversarial review engine for the entire pipeline. Use it on:

- **Papers**: LaTeX drafts, PDFs, or any written manuscript
- **Experiments**: Experimental designs, results reports, ablation studies
- **Ideas**: Research proposals, innovation claims, technical approaches

Whenever an artifact needs a skeptical, multi-perspective evaluation, invoke this skill.

## Review Approach

This skill launches three **independent, context-free reviewer agents**. Each agent is a fresh instance with no prior knowledge — they see the target artifact exactly as a real reviewer would when encountering it for the first time. No shared context, no mutual influence.

## Reviewer Personas

All three agents run in parallel:

| Agent | Focus | Default Bias |
|-------|-------|-------------|
| **Strict Reviewer** | Rigor, correctness, reproducibility | Skeptical, looks for flaws |
| **Constructive Reviewer** | Novelty, significance, improvement potential | Wants to find value |
| **Newcomer Reviewer** | Clarity, readability, accessibility | Admits confusion, asks "naive" questions |

## 0–5 Scoring System

Each reviewer scores the target across five dimensions, each rated **0 (worst) to 5 (best)**:

| Dimension | 0 | 1–2 | 3 | 4 | 5 |
|-----------|------|-------|------|------|------|
| **Novelty** | No new ideas | Minor tweak | Incremental advance | Significant novelty | Groundbreaking |
| **Rigor** | Fatal flaws | Major gaps | Adequate | Solid, minor gaps | Watertight |
| **Clarity** | Unreadable | Hard to follow | Understandable with effort | Clear and well-structured | Crystal clear |
| **Significance** | Trivial | Niche interest | Moderate impact | Important contribution | Field-changing |
| **Feasibility** | Impossible | Unlikely to work | Plausible | Well-justified | Demonstrated |

For **papers**, all five dimensions apply. For **experiments**, prioritize Rigor, Clarity, Feasibility. For **ideas**, prioritize Novelty, Significance, Feasibility.

The **total score** is the sum across all five dimensions (0–25):
- **20–25**: Strong Accept
- **15–19**: Weak Accept
- **10–14**: Weak Reject
- **0–9**: Reject

## Workflow

1. Identify the target (paper / experiment / idea) and read its content.
2. Launch three reviewer agents **independently and in parallel**, each with only the artifact content.
3. Each agent scores all applicable dimensions and produces a complete review.
4. Save individual reviews under `reviews/`.
5. Aggregate into the final report at `reports/simulated_review_report.md`.
6. If score disagreement across agents exceeds 8 points (total), launch a 4th agent for arbitration.

## Agent Prompt Template

Each agent receives this prompt, adapted to its persona:

```
You are a {persona} reviewer evaluating a {target_type}. 
You have no prior knowledge of this work. Read it as if seeing it for the first time.

{persona_specific_instructions}

For each applicable dimension, give a score from 0 to 5 using this rubric:

Novelty (0-5): ...
Rigor (0-5): ...
Clarity (0-5): ...
Significance (0-5): ...
Feasibility (0-5): ...

Then provide:
- Scores (per dimension)
- Total score and verdict (see score-to-verdict mapping)
- Summary: one paragraph restating what was reviewed
- Strengths: what works well (at least 3 items)
- Major issues: problems that significantly lower scores, with specific evidence
- Minor issues: presentation or clarity improvements
- Actionable suggestions: ranked by priority

Base all criticism on what is ACTUALLY present in the artifact. Do not assume missing content exists.
```

## Output Format

The final `reports/simulated_review_report.md` contains:

1. **Per-reviewer scores table**: All three reviewers, all dimensions side-by-side
2. **Consensus verdict**: Averaged scores + final recommendation
3. **Consolidated issues**: Merged issue list, deduplicated and ranked by severity
4. **Disagreement analysis**: Where reviewers diverged significantly and why
