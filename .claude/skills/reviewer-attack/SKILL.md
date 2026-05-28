---
name: reviewer-attack
description: "Use when simulating adversarial academic peer review, preparing rebuttals, stress-testing a paper draft, or attacking a research idea with strict, constructive, and newcomer reviewer perspectives. Reads REVIEWER_ATTACK_* settings from .env and supports GPT/OpenAI-compatible and Gemini APIs."
argument-hint: "Enter the paper path, target conference/journal, supplemental context, and output simulated review report"
user-invocable: true
---

# Reviewer Attack Skill

## When To Use

Use this skill when a paper draft or research idea needs adversarial review:

1. Simulate reviewers with different styles and perform adversarial review of a LaTeX paper draft.
2. Generate a simulated review report that provides an issue list for subsequent paper revisions and rebuttal writing.
3. During idea refinement, first-draft writing, or revision, identify weaknesses that could lead to rejection before submission.

## Configuration

The script reads model configuration from repository `.env`:

- `REVIEWER_ATTACK_API_KEY`
- `REVIEWER_ATTACK_BASE_URL` (optional for official OpenAI/Gemini endpoints)
- `REVIEWER_ATTACK_MODEL`
- `REVIEWER_ATTACK_VENDOR` or `REVIEWER_ATTACK_API_VENDOR`

Supported vendor values:

- `openai`, `gpt`, or `openai-compatible`: calls `/v1/chat/completions`.
- `gemini` or `google`: calls Gemini `generateContent`.

If reviewer-specific variables are absent, the script also accepts `REVIEW_*` fallbacks for reviewer workflows.

## Workflow

1. Read the target LaTeX paper and any extra context files.
2. Run three independent reviewer personas:
   - strict reviewer: method rigor, theory, experiments, reproducibility.
   - constructive reviewer: novelty, positioning, improvement path.
   - newcomer reviewer: readability, clarity, missing definitions.
3. Save each review under `reviews/`.
4. Save the aggregate report to `reports/simulated_review_report.md`.
5. Use the generated issues to revise `paper/paper.tex`, then write `paper/rebuttal.tex` when a rebuttal is needed.

Example:

```bash
python .claude/skills/reviewer-attack/scripts/reviewer_attack.py \
  --paper paper/paper.tex \
  --bib paper/ref.bib \
  --target-venue "top-tier systems conference" \
  --output reports/simulated_review_report.md \
  --reviews-dir reviews
```

Dry-run validation without calling an API:

```bash
python .claude/skills/reviewer-attack/scripts/reviewer_attack.py \
  --paper paper/paper.tex \
  --dry-run \
  --output reports/reviewer_attack_dry_run.md
```

## Script

- `scripts/reviewer_attack.py`: loads `.env`, builds reviewer prompts, calls GPT/OpenAI-compatible or Gemini text APIs, writes individual reviews and an aggregate Markdown report.

## Output Requirements

Each review should include:

1. Overall assessment: `Accept` / `Weak Accept` / `Weak Reject` / `Reject`.
2. Summary of paper contributions and strongest strengths.
3. Major issues that may affect acceptance, with citations to specific sections, tables, figures, equations, or missing evidence in the paper.
4. Minor issues and writing-clarity problems.
5. Actionable revision suggestions and key questions that must be addressed in the rebuttal.

Do not fabricate missing experiments, citations, or paper claims. If evidence is absent, mark it as a missing-evidence attack point.
