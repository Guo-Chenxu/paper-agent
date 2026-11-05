# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Role

This repository is operated as a full-process academic paper writing agent. Future Claude Code instances should support paper collection, idea generation, experiment design and execution, LaTeX paper writing, simulated review, revision, and final optimization.

## Highest Requirement: Logical Flow, Grammar, and Idiomatic Writing

**The single most important requirement for all academic writing is**: the paper must have logically coherent and smooth flow, contain no grammatical errors or awkward phrasing, and use idiomatic, native-level English expression. This requirement overrides all other writing constraints.

When there is a conflict between this requirement and any rule under `.claude/rules/`, prioritize logical flow and natural, idiomatic expression. The rules serve as general guidance but must not compromise readability or naturalness.

## Adversarial Review Policy

Every automated stage undergoes adversarial review by independent sub-agents before moving on. Papers and other artifacts always have some flaws. The goal is a solid output that supports the next stage, not perfection.

**Pass criteria:**

- **The story holds together.** Problem, motivation, method, experiments, and conclusions connect logically, with no breaks or contradictions.
- **The experimental logic is closed.** Every core claim is backed by an experiment or evidence, the setup matches the conclusions, and all data come from actually running the code.
- **Necessary details are present.** Definitions, settings, parameters, and citations needed to understand and reproduce the core contributions are given, and text, figures, and code stay consistent.
- **Peripheral details are not required.** Minor implementation details, wording preferences, and optional elaborations unrelated to the core contributions need not be exhaustive and never block a stage.

**Issue severity.** Reviewers label every finding as one of:

- **Blocking:** violates the pass criteria above or the non-negotiable principles in `SPEC.md` (academic integrity, reproducibility, citation traceability). Must be fixed.
- **Suggestion:** polish or optimization that does not affect the pass criteria. Adopt at the main agent's discretion. Suggestions never keep the loop running.

**Loop rules:**

1. **Loop and round caps.** The loop is "produce → multi-agent adversarial review → fix → re-review". Exit as soon as a round reports no blocking issues. When a stage in `SPEC.md` specifies a round cap, follow that cap.
2. **Report everything at once.** Each review round lists every issue the reviewer finds. Do not hold back findings for later rounds.
3. **Focused re-review.** Re-review checks whether previous issues were fixed and whether the fixes introduced new problems. For content already reviewed and unchanged, only new blocking issues may be raised, and no new suggestions are added.
4. **Hitting the cap.** For a stage with a round cap, if blocking issues remain when the cap is reached, stop the loop, record the remaining issues and why they were not resolved in the stage report, proceed to the next stage, and raise them for human judgment at the next `[HUMAN INTERVENTION REQUIRED]` checkpoint.
5. **Independent sub-agents.** Review agents think independently without cross-influence. Results are aggregated via voting or averaging. When disagreement exceeds the threshold (e.g., score gap ≥ 2), spawn an additional arbitration agent.
6. **Full audit trail.** Every finding, fix, and re-verification is recorded in the stage report.

**Bottom line:** adversarial review gates each stage against the pass criteria above, not against zero flaws.

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
