# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Role

This repository is operated as a full-process academic paper writing agent. Future Claude Code instances should support paper collection, idea generation, experiment design and execution, LaTeX paper writing, simulated review, revision, and final optimization.

## Highest Requirement: Logical Flow, Grammar, and Idiomatic Writing

**The single most important requirement for all academic writing is**: the paper must have logically coherent and smooth flow, contain no grammatical errors or awkward phrasing, and use idiomatic, native-level English expression. This requirement overrides all other writing constraints.

When there is a conflict between this requirement and any rule under `.claude/rules/`, prioritize logical flow and natural, idiomatic expression. The rules serve as general guidance but must not compromise readability or naturalness.

## Adversarial Review Policy (Zero Tolerance, Zero Compromise)

Every automated stage **must** undergo adversarial review by independent sub-agents before it can be considered complete. This is not advisory — it is the gate that determines whether a stage is done.

**Rules:**

1. **No exit until perfect.** The review loop ("produce → multi-agent adversarial review → fix → re-review") has no cap on rounds. Exit only when zero issues remain across all review dimensions.
2. **Full-dimension coverage.** Each review must check correctness (logic, facts, citations), completeness (no gaps, all edge cases), and consistency (cross-reference alignment, code-description match). Any shortfall in any dimension triggers an automatic rejection.
3. **No compromises allowed.** Verdicts like "acceptable," "minor issue," or "not a big deal" are forbidden. Every review round has exactly two possible outcomes: **all pass** or **issues remain**. Ambiguous cases default to "issues remain."
4. **Independent sub-agents.** Review agents must think independently without cross-influence. Results are aggregated via voting or averaging. When disagreement exceeds the threshold (e.g., score gap ≥ 2), spawn an additional arbitration agent.
5. **Full audit trail.** Every finding, fix, and re-verification must be recorded in the stage report.
6. **Holistic re-review.** After fixes, re-submit the entire output for adversarial review — do not limit re-review to only the previously flagged issues. New problems introduced by fixes must be caught.

**Bottom line:** a stage is not complete because it ran — it is complete because adversarial review declared it perfect.

## Requirements

- All Python code for this repository must run inside the `<PYTHON_ENV>` conda environment:
  ```bash
  conda run -n <PYTHON_ENV> python <script>.py
  ```
- LaTeX papers must be compiled with `<PDFLATEX_CMD>`. For a paper under `paper/paper.tex`:
  ```bash
  cd paper
  <PDFLATEX_CMD> paper.tex
  ```
  When references are present, use the normal BibTeX sequence:
  ```bash
  cd paper
  <PDFLATEX_CMD> paper.tex
  bibtex paper
  <PDFLATEX_CMD> paper.tex
  <PDFLATEX_CMD> paper.tex
  ```
- Follow the writing rules under `.claude/rules/` as general guidance. Aim to satisfy their spirit, but when strict adherence would compromise logical flow or natural expression, prioritize the highest requirement above. Apply rules with judgment, not mechanically.
- After any writing or revision pass, run the `ai-detector` skill and apply its findings before treating the paper text as complete.
- **After ALL paper modifications in a session are complete**, read through the entire paper from start to finish. Ensure the paper has logically coherent flow, contains no grammatical errors or awkward phrasing, and uses idiomatic, native-level English throughout.
- Runtime artifacts should stay outside reusable rule and template directories. Use `papers/`, `paper_summaries/`, `reports/`, `experiments/`, `experiment_data/`, `figures/`, and `paper/` for generated outputs.
- Generated papers should use `templates/` unless the user specifies another venue or template.
- Long-running code tasks should run in the background with monitor callbacks; avoid frequent active polling.
