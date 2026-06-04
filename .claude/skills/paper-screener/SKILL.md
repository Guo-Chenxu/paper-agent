---
name: paper-screener
description: "Use when screening and summarizing collected academic papers. Supports two-round multi-agent screening (title+abstract pre-screening, full-text deep screening), score aggregation, structured summaries, and screening report generation."
argument-hint: "Path to papers directory, research domain, screening thresholds"
user-invocable: true
---

# Paper Screener

## Skill Goal

Automated two-round paper screening and structured summarization:

1. Round 1: Title+abstract pre-screening with 3 parallel agents for fast coarse filtering
2. Round 2: Full-text deep screening with 3 parallel agents reading complete PDFs
3. Score aggregation with arbitration when agent disagreement exceeds threshold
4. Structured paper summaries for high-scoring papers, generated from full-text reading
5. Comprehensive screening report with statistics, rankings, and traceability

## When To Use

- After paper crawling produces abstracts and metadata
- Need to filter and rank candidate papers by quality and relevance
- Want structured, full-text-based summaries of selected papers
- Preparing input for literature review or research idea generation

## Prerequisites

Required inputs from a prior crawl run:

- `./papers/abstracts/*.txt` — abstract text files
- `./papers/metadata/papers_*.json` — paper metadata records
- `./papers/pdfs/*.pdf` — full-text PDFs (required for Round 2; download if missing)

Required Python packages:

```bash
python -m pip install requests
```

## Scripts

- Load papers for screening: `./scripts/load_papers_for_screening.py`

## Workflow

### Step 1: Load and Prepare Papers

```bash
python .claude/skills/paper-screener/scripts/load_papers_for_screening.py \
  --abstracts-dir ./papers/abstracts \
  --metadata-dir ./papers/metadata \
  --output screening_input.json
```

This produces a JSON file with paper titles, abstracts, venues, years, and authors for agent scoring.

### Step 2: Round 1 — Title+Abstract Pre-Screening

**Purpose**: Fast coarse filtering to reduce the candidate set. Scores from this round are NOT used as final quality judgments.

Spawn 3 parallel subagents, each scoring every paper independently. Each agent receives only the title and abstract.

**Scoring Criteria (1–10 total)**:

| Dimension | Points | Description |
|-----------|--------|-------------|
| Relevance | 5 | Fit with the target research domain |
| Potential Innovation | 3 | Novelty indicated in the abstract |
| Publication Quality | 2 | Venue tier, citation count |

**Agent System Prompts**:

Agent 1 — Senior Researcher:
```
You are a senior researcher evaluating papers for a literature survey.
Score each paper on a scale of 1-10 based on title and abstract only.
Focus on: relevance to the domain (5pts), potential innovation (3pts), publication quality (2pts).
For each paper, return ONLY a JSON object:
{"arxiv_id": "<id>", "scores": {"relevance": <1-5>, "innovation": <1-3>, "quality": <1-2>, "total": <1-10>}, "reason": "<one sentence>"}
Return a JSON array of all scored papers.
```

Agent 2 — Professor:
```
You are a professor screening papers for a top-tier venue submission.
Score each paper on a scale of 1-10 based on title and abstract only.
Be critical and objective. Focus on: domain relevance (5pts), potential novelty (3pts), venue/author quality (2pts).
For each paper, return ONLY a JSON object:
{"arxiv_id": "<id>", "scores": {"relevance": <1-5>, "innovation": <1-3>, "quality": <1-2>, "total": <1-10>}, "reason": "<one sentence>"}
Return a JSON array of all scored papers.
```

Agent 3 — Industry Researcher:
```
You are an industry researcher evaluating papers for practical relevance.
Score each paper on a scale of 1-10 based on title and abstract only.
Balance academic merit with real-world applicability. Focus on: domain relevance (5pts), innovation potential (3pts), publication quality (2pts).
For each paper, return ONLY a JSON object:
{"arxiv_id": "<id>", "scores": {"relevance": <1-5>, "innovation": <1-3>, "quality": <1-2>, "total": <1-10>}, "reason": "<one sentence>"}
Return a JSON array of all scored papers.
```

**User Prompt Template**:
```
Score the following papers for a research survey in the domain of: {research_domain}

Papers (title, abstract, venue, year):
{papers_json}

Score each paper on:
- Relevance to {research_domain} (1-5)
- Potential innovation from abstract (1-3)
- Publication quality: venue tier and citations (1-2)

Return a JSON array with one object per paper.
```

Where `{research_domain}` is derived from the original crawl query, and `{papers_json}` is the loaded screening input.

**Selection**: Papers with average total score >= 5.0 across the 3 agents advance to Round 2.

Save Round 1 results to `./reports/paper_prescreening_results.json`.

### Step 3: Download PDFs for Round 2

For papers passing Round 1, ensure full-text PDFs are available:

1. Check `./papers/pdfs/` for existing PDF files.
2. For missing PDFs, re-run the crawler with `--download-pdf` and the specific paper IDs, or use the `pdf_url` from metadata to download directly.
3. Papers whose full text cannot be obtained are recorded in a "downgraded" list and excluded from Round 2 scoring but still noted in the final report.

### Step 4: Round 2 — Full-Text Deep Screening

**Purpose**: Deep quality evaluation based on complete paper content. Scores from this round are the final quality judgments.

Spawn 3 parallel subagents per batch of papers. Each agent must read the full PDF of each paper before scoring.

**Scoring Criteria (1–10 total)**:

| Dimension | Points | Description |
|-----------|--------|-------------|
| Innovation | 4 | Novel method, problem, or finding (judged from method and experiment sections) |
| Impact | 3 | Venue tier, citation count, author team |
| Relevance | 3 | Fit with domain (judged from introduction, method, and experiments) |

**Agent System Prompts**:

Agent 1 — Senior Researcher:
```
You are a senior researcher conducting a deep paper review.
Read each paper's full PDF carefully before scoring.
Evaluate on: innovation (4pts) — novel method/problem/finding in method and experiment sections; impact (3pts) — venue, citations, author team; relevance (3pts) — fit with the target domain across all sections.
For each paper, return ONLY a JSON object:
{"arxiv_id": "<id>", "scores": {"innovation": <1-4>, "impact": <1-3>, "relevance": <1-3>, "total": <1-10>}, "reason": "<one sentence summarizing key strengths and weaknesses>"}
Return a JSON array of all scored papers.
```

Agent 2 — Professor:
```
You are a professor reviewing papers for a top-tier venue.
Read each paper's full PDF carefully before scoring. Be critical and rigorous.
Evaluate on: innovation (4pts) — genuine novelty in method and findings; impact (3pts) — potential influence, venue quality; relevance (3pts) — domain alignment assessed from introduction through experiments.
For each paper, return ONLY a JSON object:
{"arxiv_id": "<id>", "scores": {"innovation": <1-4>, "impact": <1-3>, "relevance": <1-3>, "total": <1-10>}, "reason": "<one sentence>"}
Return a JSON array of all scored papers.
```

Agent 3 — Industry Researcher:
```
You are an industry researcher evaluating papers for both academic and practical merit.
Read each paper's full PDF carefully before scoring.
Evaluate on: innovation (4pts) — technical novelty and practical applicability; impact (3pts) — real-world potential and venue quality; relevance (3pts) — domain fit across the full paper.
For each paper, return ONLY a JSON object:
{"arxiv_id": "<id>", "scores": {"innovation": <1-4>, "impact": <1-3>, "relevance": <1-3>, "total": <1-10>}, "reason": "<one sentence>"}
Return a JSON array of all scored papers.
```

**User Prompt Template**:
```
Score the following papers for a research survey in the domain of: {research_domain}

Read each paper's full PDF at the given path before scoring.

Papers:
{papers_with_pdf_paths_json}

Score each paper on:
- Innovation (1-4): novel method, problem, or finding — read method and experiment sections
- Impact (1-3): venue prestige, potential citations, author team
- Relevance (1-3): fit with {research_domain} — evaluate from introduction, method, and experiments

Return a JSON array with one object per paper.
```

**Selection**: Papers with average total score >= 7.0 across the 3 agents are selected for summarization.

Save Round 2 results to `./reports/paper_fulltext_screening_results.json`.

### Step 5: Score Aggregation and Arbitration

1. For each paper, compute the average total score across the 3 agents.
2. For each paper, compute the range (max - min) of agent total scores.
3. If the range exceeds 3 points, spawn a 4th arbiter agent using the same scoring criteria. The final score is the average of all 4 agents.
4. Rank all papers by final average score (descending).

Save the aggregation and arbitration results to `./reports/paper_screening_aggregation.json`.

### Step 6: Generate Structured Summaries

For each paper selected in Round 2 (avg >= 7.0), spawn an agent to read the full PDF and generate a structured summary.

**Summary Agent System Prompt**:
```
You are a research assistant creating structured paper summaries.
Read the full PDF carefully, including method, experiment, and limitation sections.
Generate a structured summary with these 4 sections:
1. Research Background & Problem (2-3 sentences): what problem and why important
2. Core Innovations (2-3 bullet points): key novel contributions from the method section
3. Key Methods & Results (2-3 sentences): approach and main experimental findings with specific numbers
4. Limitations & Future Work (1-2 sentences): acknowledged limitations and suggested directions

Write the summary in Markdown format. Be specific and quantitative where possible.
```

**User Prompt Template**:
```
Generate a structured summary for the following paper.

Title: {title}
Authors: {authors}
Venue: {venue} ({year})
PDF Path: {pdf_path}

Read the full PDF and produce a structured summary with:
- Research Background & Problem
- Core Innovations (with details from the method section)
- Key Methods & Results (with specific numbers and baselines)
- Limitations & Future Work
```

Save each summary to `./paper_summaries/{arxiv_id}.md`.

### Step 7: Generate Screening Report

Create a comprehensive Markdown report at `./reports/paper_screening_report.md`.

**Report Structure**:

```markdown
# Paper Screening Report

## Statistics Summary
- Total papers collected: [N]
- Round 1 (title+abstract) scored: [N]
- Round 1 passed (avg >= 5.0): [N]
- Round 2 (full-text) scored: [N]
- Round 2 passed (avg >= 7.0): [N]
- Pass rate: [%]
- Papers downgraded (full text unavailable): [N]
- Number of agents: 3 (4th arbiter used for [N] papers)

## Round 1 Scoring Criteria
- Relevance (5pts) + Potential Innovation (3pts) + Publication Quality (2pts) = 10pts
- Threshold: avg >= 5.0

## Round 2 Scoring Criteria
- Innovation (4pts) + Impact (3pts) + Relevance (3pts) = 10pts
- Threshold: avg >= 7.0

## Venue Distribution
| Venue | Count |
|-------|-------|
| ...   | ...   |

## Papers Downgraded (Full Text Unavailable)
[List any papers excluded from Round 2 due to missing PDFs]

## Top Papers (Ranked by Round 2 Score)
| Rank | Avg Score | Innovation | Impact | Relevance | Title | Venue | Year |
|------|-----------|------------|--------|-----------|-------|-------|------|
| 1    | ...       | ...        | ...    | ...       | ...   | ...   | ...  |

## All Passed Papers with Structured Summaries
[For each paper with avg >= 7.0, include its structured summary]
```

## Output Requirements

All outputs saved to the project working directory, NOT back to `.claude/skills/`:

- Round 1 scores: `./reports/paper_prescreening_results.json`
- Round 2 scores: `./reports/paper_fulltext_screening_results.json`
- Score aggregation: `./reports/paper_screening_aggregation.json`
- Structured summaries: `./paper_summaries/{arxiv_id}.md`
- Screening report: `./reports/paper_screening_report.md`
