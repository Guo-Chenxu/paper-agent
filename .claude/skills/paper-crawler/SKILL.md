---
name: paper-crawler
description: "Automates high-quality paper crawling for SPEC phase 1 over the most recent 3 years. Use for IEEE/ACM/OSDI conference paper crawling, PDF downloads, and automatic arXiv title-based fallback when authentication fails. Keywords: CCF A/B, conference crawler, arxiv fallback, paper metadata."
argument-hint: "Enter research keywords, time range (default 3 years), and target venue sources (ieee/acm/osdi)"
user-invocable: true
---

# Paper Crawler (Phase-1 Aligned)

## Skill Goal

This skill aligns with the crawling step in [SPEC.md](../../SPEC.md) phase 1, "automated paper collection and screening", and completes the following tasks:

1. Crawl paper metadata from the most recent 3 years by research keywords (default).
2. Support multi-source crawling across IEEE / ACM / OSDI.
3. Automatically download available PDFs to `./papers/pdfs/`.
4. When a conference-site PDF is unavailable because of authentication, rate limits, or non-PDF responses, automatically fall back to arXiv title search and download.
5. Save structured metadata and abstract text for downstream screening agents.

## When To Use

- Phase 1 has just started and a candidate paper pool needs to be built.
- The workflow should cover common CCF A/B conference sources but is constrained by site authentication.
- A reproducible, batch-processable paper crawling workflow is needed.

## Scripts

- Multi-source unified scheduler and fallback: `./scripts/multi_source_crawler.py`
- General OpenAlex crawler: `./scripts/openalex_crawler.py`
- IEEE conference crawler: `./scripts/ieee_crawler.py`
- ACM conference crawler: `./scripts/acm_crawler.py`
- OSDI conference crawler: `./scripts/osdi_crawler.py`
- arXiv crawling and title-search fallback: `./scripts/arxiv_crawler.py`
- Local idea prompt export: `./scripts/export_idea_prompts.py`
- Local traditional scheduling prompt export: `./scripts/export_idea_prompts_traditional_scheduling.py`

## References

- Local idea generation workflow and prompts: `./references/idea-generation.md`

## Required Python Packages

```bash
pip install requests arxiv tqdm
```

## Phase-1 Workflow

### Step 1: Define Crawl Inputs

Recommended input parameters:

- Research keywords: for example `distributed systems OR resource scheduling OR cluster management`
- Time range: default `3` years
- Target venue sources: default `ieee acm osdi`
- Maximum number of papers per source: default `120`

### Step 2: Run Multi-Source Crawl

Run from the repository root:

```bash
python .claude/skills/paper-crawler/scripts/multi_source_crawler.py \
  --query "distributed systems OR resource scheduling OR cluster management" \
  --venues ieee acm osdi \
  --years 3 \
  --max-results-per-venue 120 \
  --workers 3 \
  --download-pdf \
  --output-dir ./papers
```

Optional: provide an email address for OpenAlex to improve stability.

```bash
--mailto your_email@example.com
```

### Step 3: Understand Fallback Behavior

When downloading PDFs, the script follows this logic:

1. First try the primary-source PDF URL.
2. If the response is `401/403/407`, `429`, another `4xx/5xx`, or non-PDF content, treat the primary source as unavailable.
3. Trigger arXiv fallback: search arXiv candidate papers by title.
4. Download the fallback PDF only when the title similarity reaches the threshold.
5. Write a `fallback` field into the metadata to record the fallback reason and matching information.

### Step 4: Verify Outputs

Default output directory: `./papers/`

- PDF files: `./papers/pdfs/*.pdf`
- Abstract text: `./papers/abstracts/*.txt`
- Metadata: `./papers/metadata/papers_*.json`
- Summary statistics: `./papers/metadata/summary_*.json`

Key fields in `summary_*.json`:

- `source_counts`: crawl counts by source
- `raw_count`: total raw count
- `deduped_count`: total count after deduplication
- `final_count`: final usable paper count
- `download_stats`: primary-source success/failure and fallback success/failure statistics

## Quality Checks (Completion Criteria)

Before completing phase-1 crawling, check at least:

1. `final_count > 0`
2. `download_stats.primary_success + download_stats.fallback_success > 0`
3. The metadata contains `venue`, `title`, `abstract`, and `source` fields.
4. Sample-check whether `fallback.title_similarity` is reasonable for fallback papers.

## Decision Points

1. If IEEE/ACM hit rates are low: expand keywords first, then increase `max-results-per-venue`.
2. If fallback hit rate is low: loosen the query expression by removing overly specific phrases.
3. If PDF download failure is high: collect metadata only and move into the abstract-screening workflow, then backfill full texts later.

## Suggested Next Step in SPEC

After this skill produces outputs, continue with the later steps of phase 1:

1. Have multiple agents score titles and abstracts.
2. Average the scores and select papers with scores `>=7`.
3. Generate structured paper summaries and a screening report.

## Local Idea Generation

When moving from paper summaries to research ideas, do not use external API scripts. Run one of the prompt-export helpers to prepare local context, then read `./references/idea-generation.md` and launch multiple Claude Code subagents in parallel. Each subagent should use a different persona, generate candidate ideas locally, and return structured Markdown or JSON-compatible content for the main session to rank and expand.

Example:

```bash
python .claude/skills/paper-crawler/scripts/export_idea_prompts.py \
  --summaries-dir ./paper_summaries \
  --reports-dir ./reports \
  --max-papers 50
```

For traditional distributed scheduling ideas:

```bash
python .claude/skills/paper-crawler/scripts/export_idea_prompts_traditional_scheduling.py \
  --summaries-dir ./paper_summaries \
  --reports-dir ./reports \
  --max-papers 60
```
