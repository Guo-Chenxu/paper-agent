---
name: paper-crawler
description: "Use when reproducible paper collection is needed. Supports multi-provider crawling (OpenAlex, arXiv, Semantic Scholar, USENIX), deduplication, normalized metadata, and optional PDF download."
argument-hint: "Enter research domain, time range, primary providers, and optional USENIX venues"
user-invocable: true
---

# Paper Crawler

## Skill Goal

Automated paper collection from multiple providers:

1. Multi-provider crawling: OpenAlex, arXiv, Semantic Scholar, USENIX proceedings
2. Metadata normalization and cross-provider deduplication
3. Optional PDF download with arXiv title-based fallback

## When To Use

- Need candidate papers from multiple public metadata sources
- Want normalized metadata, deduplication, and CCF A/B venue preference
- Starting a literature review or research survey workflow

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
- Legacy OpenAlex wrappers: `./scripts/ieee_crawler.py`, `./scripts/acm_crawler.py`

## References

- CCF recommended venues: `./references/ccf_venues_all.json`
- Source: 中国计算机学会推荐国际学术会议和期刊目录(第七版, 2026年)

## Collection Workflow

### Step 1: Define External Crawl Inputs

All research-topic queries must come from command-line input. Do not rely on preset query strings in crawler code.

Recommended input parameters:

- Query: pass through `--query`.
- Time range: default `3` years.
- Primary providers: default `openalex arxiv semanticscholar usenix`.
- Maximum papers per provider: default `120`.
- USENIX venues: default `osdi`; configurable with `--usenix-venues osdi nsdi atc`.
- CCF A/B preference: prioritize candidates from CCF A/B venues during collection when venue metadata is available.

### Step 2: Run Multi-Provider Crawl

Run from the repository root:

```bash
python .claude/skills/paper-crawler/scripts/multi_source_crawler.py \
  --query "your research domain keywords" \
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

PDF can be downloaded by `--download-pdf`, the script follows this logic:

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

## Output Requirements

All outputs should be saved to the project working directory, NOT back to `.claude/skills/`:

- Crawler outputs: `./papers/` directory
- Paper metadata: `./papers/metadata/papers_*.json`
- Paper abstracts: `./papers/abstracts/*.txt`
- PDF files (if `--download-pdf` enabled): `./papers/pdfs/*.pdf`
- Summary statistics: `./papers/metadata/summary_*.json`
