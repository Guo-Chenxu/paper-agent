# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Role

This repository is operated as a full-process academic paper writing agent. Future Claude Code instances should support paper collection, idea generation, experiment design and execution, LaTeX paper writing, simulated review, revision, and final optimization.

## Requirements

- All Python code for this repository must run inside the `<PYTHON_ENV>` environment. Prefer explicit environment execution when possible:
  ```bash
  conda run -n <PYTHON_ENV> python <script>.py
  ```
- LaTeX papers must be compiled with `<PDFLATEX_CMD>`. For a paper under `paper/paper.tex`, use:
  ```bash
  cd paper
  <PDFLATEX_CMD> paper.tex
  ```
  When references are present, use the normal BibTeX sequence for the template:
  ```bash
  cd paper
  <PDFLATEX_CMD> paper.tex
  bibtex paper
  <PDFLATEX_CMD> paper.tex
  <PDFLATEX_CMD> paper.tex
  ```
- All academic writing, rewriting, polishing, simulated-review revision, and final optimization must follow every rule under `.claude/rules/`.
- After any writing or revision pass, run the `ai-detector` skill and apply its findings before treating the paper text as complete.
- Runtime artifacts should stay outside reusable rule and template directories. Use `papers/`, `paper_summaries/`, `reports/`, `experiments/`, `experiment_data/`, `figures/`, and `paper/` for generated outputs.
- Generated papers should use `templates/` unless the user specifies another venue or template.
