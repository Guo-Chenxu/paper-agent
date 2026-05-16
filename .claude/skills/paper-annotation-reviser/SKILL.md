---
name: paper-annotation-reviser
description: Use when the user provides an annotated academic paper PDF and asks to revise LaTeX/TeX source, address PDF comments, apply similar fixes across the paper, or preserve reviewer/reader annotation issues for future ai-detector checks.
argument-hint: "annotated PDF path; TeX source path; optional annotation markdown/json path"
user-invocable: true
---

# Paper Annotation Reviser

## Overview

Turn an annotated paper PDF into a verifiable TeX revision workflow. Core principle: annotations are not merely local sentence-level TODOs; they are samples that reveal similar issues across the whole paper.

**REQUIRED SUB-SKILL:** Use `pdf-annotation-extractor` to extract or read PDF annotations.

## When To Use

- The user provides an annotated paper PDF and asks to revise `.tex` / LaTeX source files.
- The user asks to "revise the paper according to annotations", "do not only fix annotated locations", or "check the whole paper for similar issues".
- The user wants to preserve writing issues identified in annotations for later reuse by `ai-detector`.

Do not use this for plain text polishing without PDF annotations. For those tasks, prefer normal editing or `ai-detector`.

## Workflow

### 1. Extract or read annotations

1. If no annotation file already exists, invoke `pdf-annotation-extractor` to generate Markdown and, when needed, JSON as well.
2. If `*_annotations.md` or `*_annotations.json` already exists, read the existing file and spot-check whether the PDF/annotation summary matches.
3. Record the annotation count, page numbers, annotation types, source text snippets, and comment content.

### 2. Build an annotation-to-TeX location table

For each actionable annotation, build a table:

| Annotation |    PDF Page | Selected Text                     | TeX Location                           | Action                |
| ---------- | ----------: | --------------------------------- | -------------------------------------- | --------------------- |
| ID         | page number | short excerpt from annotated text | `path/to/file.tex:line` or `unmatched` | revise / ignore / ask |

When locating text, account for differences between PDF and TeX: line breaks, hyphenation, TeX commands, math symbols, citation commands, and escaped characters. If a location cannot be found, do not guess-edit; mark it as `unmatched` and explain why.

### 3. Generalize reusable issue categories

Extract "similar issue checklist items" from annotations instead of only copying individual sentence fixes. Examples:

- Terms or abbreviations appear for the first time without definitions.
- `this/it/they` references are unclear.
- Sentences are too long and make logical relationships unclear.
- Claims are too strong or missing qualifications.
- Figure/table references or experiment descriptions are not specific enough.
- AI-writing traces: vague adjectives, formulaic transitions, overly smooth prose with insufficient technical detail.

Only categorize issues supported by annotation content. Do not expand unsupported personal preferences into paper-wide rules.

### 4. Revise the TeX hit by annotations

When editing TeX, preserve:

- `\label{}`, `\ref{}`, `\cite{}`, math formulas, tables, and figure environments.
- Technical conclusions, experimental results, and numeric values unless there is evidence for the change.
- The original scope; do not expand into unrelated rewrites.
- User confirmation for annotations where the author's intent cannot be inferred.

### 5. Scan the whole paper for similar issues

Run a full-paper scan for the issue categories from step 3. Combine:

- `rg` / `grep` / keyword search: terms, vague references, and phrases repeatedly appearing in annotations.
- TeX structure review: abstract, introduction, method, evaluation, and conclusion.
- Diff review: confirm changes are not concentrated only near annotated locations.

For each issue category, record the scan method, matched locations, revised locations, and unchanged locations with reasons.

### 6. Preserve patterns in rules

After each revision, summarize the writing-style, AI-trace, expression-clarity, or paper-prose issues addressed:

1. Update `.claude/rules/annotation-derived-writing-patterns.md`.
2. Add only reusable patterns: problem, signals, checking method, and revision suggestion.
3. Do not add private project facts, unpublished reviewer identities, one-off task state, or purely technical TODOs.
4. Confirm that `ai-detector`'s `SKILL.md` requires reading this rules file before every analysis.

## Verification

Before finishing, provide evidence instead of only saying "revised":

- Total annotation count, processed count, and unprocessed count.
- Annotation-to-TeX line-location summary.
- Full-paper similar-issue scan categories and match counts.
- `git diff` summary or key changed locations.
- LaTeX compilation/check results. If compilation cannot run, state which command was run, why it failed, and whether the failure is related to these changes.
- Summary of rules file updates, if applicable.

## Output Format

```markdown
## Annotation Revision Report

### Annotation handling

- Total annotations: N
- Revised: N
- Unmatched / skipped: N, with reasons

### TeX changes

- `paper/file.tex:line`: what changed and why

### Similar issues scanned

- Issue category: scan method, matches, changes, no-change reasons

### Rules file updates

- Added / updated patterns
- File path

### Verification

- Commands run
- Results
```

## Common Mistakes

| Mistake                                                   | Fix                                                          |
| --------------------------------------------------------- | ------------------------------------------------------------ |
| Only revising the sentence near the annotated source text | Generalize issue categories first, then scan the whole paper |
| Guess-editing when the TeX source cannot be located       | Mark as `unmatched`, explain why, and ask the user if needed |
| Writing every annotation into ai-detector                 | Preserve only reusable writing / AI-trace patterns           |
| Changing technical meaning for the sake of polishing      | Keep facts, values, and claim boundaries unchanged           |
| Claiming completion without evidence                      | Output line numbers, scan methods, diff/compilation results  |
