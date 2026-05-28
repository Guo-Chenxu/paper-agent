---
name: paper-crawler
description: "Use when reproducible paper collection is needed from multiple public providers. Supports OpenAlex, arXiv, Semantic Scholar, and configurable USENIX proceedings with normalized metadata, deduplication, provider counts, optional PDF download, CCF A/B preference, and arXiv fallback."
argument-hint: "Enter external research query, time range, primary providers, and optional USENIX venues"
user-invocable: true
---

# Paper Crawler

## Skill Goal

This skill collects and normalizes candidate academic papers from multiple public providers:

1. OpenAlex metadata search.
2. arXiv metadata and PDF search.
3. Semantic Scholar metadata search.
4. USENIX public proceedings crawling, with configurable venues such as `osdi`, `nsdi`, and `atc`.

arXiv is a primary query provider. It is also used as a title-based PDF fallback when another provider has metadata but no downloadable PDF.

IEEE Xplore and ACM Digital Library direct adapters are not implemented yet. The legacy `ieee_crawler.py`, `acm_crawler.py`, and `osdi_crawler.py` scripts are OpenAlex-based compatibility wrappers, not independent IEEE/ACM/USENIX provider APIs.

## When To Use

- A workflow needs a candidate paper pool from multiple public metadata sources, with CCF A/B venues recommended during screening rather than treated as the only crawl source.
- The workflow needs normalized metadata, provider provenance, deduplication, and batch-processable outputs.
- USENIX proceedings should be queried directly without authentication.

## Environment

Run crawler commands from the repository root with the active Python interpreter.

Required packages:

```bash
python -m pip install requests arxiv tqdm pytest
```

Optional Semantic Scholar API key:

```bash
export SEMANTIC_SCHOLAR_API_KEY=...
```

## Scripts

- Unified multi-provider crawler: `./scripts/multi_source_crawler.py`
- Shared record normalization and deduplication helpers: `./scripts/paper_record.py`
- OpenAlex provider: `./scripts/openalex_crawler.py`
- arXiv provider and title fallback: `./scripts/arxiv_crawler.py`
- Semantic Scholar provider: `./scripts/semantic_scholar_crawler.py`
- USENIX proceedings provider: `./scripts/usenix_crawler.py`
- Legacy OpenAlex wrappers: `./scripts/ieee_crawler.py`, `./scripts/acm_crawler.py`, `./scripts/osdi_crawler.py`
- Local idea prompt export: `./scripts/export_idea_prompts.py`
- Local traditional scheduling prompt export: `./scripts/export_idea_prompts_traditional_scheduling.py`

## References

- Local idea generation workflow and prompts: `./references/idea-generation.md`

## Collection Workflow

### Step 1: Define External Crawl Inputs

All research-topic queries must come from command-line input. Do not rely on preset query strings in crawler code.

Recommended input parameters:

- Query: pass through `--query`.
- Time range: default `3` years.
- Primary providers: default `openalex arxiv semanticscholar usenix`.
- Maximum papers per provider: default `120`.
- USENIX venues: default `osdi`; configurable with `--usenix-venues osdi nsdi atc`.
- CCF A/B preference: prioritize candidates from CCF A/B venues during scoring and reporting when venue metadata is available.

### Step 2: Run Multi-Provider Crawl

Run from the repository root:

```bash
python .claude/skills/paper-crawler/scripts/multi_source_crawler.py \
  --query "distributed systems resource scheduling" \
  --providers openalex arxiv semanticscholar usenix \
  --years 3 \
  --max-results-per-provider 120 \
  --usenix-venues osdi \
  --workers 4 \
  --output-dir ./papers
```

Optional: provide an email address for OpenAlex to improve stability.

```bash
--mailto your_email@example.com
```

### Step 3: Understand PDF and Fallback Behavior

PDF download is opt-in through `--download-pdf`.

When PDF download is enabled, the script follows this logic:

1. Try the normalized `pdf_url` from the primary provider record.
2. Treat authentication failures, rate limits, HTTP errors, and non-PDF responses as unavailable PDFs.
3. Search arXiv by title as a fallback.
4. Download the fallback PDF only when title similarity reaches the arXiv fallback threshold.
5. Write a `fallback` field into the metadata.

### Step 4: Verify Outputs

Default output directory: `./papers/`

- PDF files, only with `--download-pdf`: `./papers/pdfs/*.pdf`
- Abstract text: `./papers/abstracts/*.txt`
- Metadata: `./papers/metadata/papers_*.json`
- Summary statistics: `./papers/metadata/summary_*.json`

Key fields in `summary_*.json`:

- `raw_provider_counts`: raw result counts before deduplication.
- `provider_counts`: final merged record counts by provider provenance.
- `provider_errors`: provider failures that did not stop the whole run.
- `raw_count`: total raw count.
- `deduped_count`: count after deduplication.
- `final_count`: final usable paper count.
- `download_stats`: PDF download and fallback statistics.

## Normalized Metadata

Each final metadata record should contain:

- `record_id`
- `title`
- `authors`
- `abstract`
- `year` or `publication_date`
- `venue`
- `providers`
- `provider_records`
- `source_url`
- `pdf_url` when available
- IDs such as `doi`, `arxiv_id`, `openalex_id`, and `semantic_scholar_id` when available

## Quality Checks

Before completing a crawl, check at least:

1. `final_count > 0`, or each provider has a clear error in `provider_errors`.
2. `raw_provider_counts` includes each requested provider.
3. arXiv appears as a primary requested provider when `arxiv` is enabled.
4. Metadata contains `record_id`, `title`, `providers`, and `provider_records`.
5. Abstract text files exist even when `--download-pdf` is not used.
6. If fallback is used, `fallback.title_similarity` is reasonable.

## Suggested Tests

```bash
python -m pytest tests/paper_crawler -v
```

Optional live smoke test:

```bash
python .claude/skills/paper-crawler/scripts/multi_source_crawler.py \
  --query "resource scheduling" \
  --providers openalex arxiv semanticscholar usenix \
  --years 1 \
  --max-results-per-provider 3 \
  --usenix-venues osdi \
  --workers 2 \
  --output-dir ./papers_smoke
```

## Suggested Follow-up Screening

After this skill produces outputs, a screening workflow can:

1. Have multiple agents score titles and abstracts.
2. Average the scores and select papers with scores `>=7`.
3. Generate structured paper summaries and a screening report.

## Local Idea Generation

When moving from paper summaries to research ideas, do not use external API scripts. Run one of the prompt-export helpers to prepare local context, then read `./references/idea-generation.md` and launch multiple Claude Code subagents in parallel. Each subagent should use a different persona, generate candidate ideas locally, and return structured Markdown or JSON-compatible content for the main session to rank and expand.
