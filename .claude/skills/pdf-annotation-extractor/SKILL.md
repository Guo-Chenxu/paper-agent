---
name: pdf-annotation-extractor
description: "Use when the user asks to read PDF annotations, export highlights, organize paper comments, convert PDF notes/comments/annotations to Markdown or JSON, or extract annotated text and surrounding context from an academic-paper PDF."
argument-hint: "PDF file path; optional output path and output format markdown/json"
user-invocable: true
---

# PDF Annotation Extractor

## Goal

Read a PDF and extract:

1. The PDF annotation list, including highlight, underline, strikeout, sticky note, text comment, and similar annotations.
2. The source text snippet corresponding to each annotation.
3. A surrounding context excerpt for every annotation.
4. The annotation author, creation/modification time, and comment content.

Every annotation entry must include `context`: the sentence-level page text located by the annotation coordinates, starting after the previous period (`.` or `。`) and ending at the next period. Markdown must show a Context section for every annotation even when no extractable context is found. Markdown is the default output because it is easy to read manually. Use JSON when downstream programmatic processing is needed.

## When To Use

- The user asks to "extract PDF annotations", "export highlights", "organize paper comments", or read comments/notes/annotations.
- The user provides an academic-paper PDF and wants a new file containing annotations plus their corresponding source text snippets.
- The user needs to convert highlights/comments from a PDF reader into Markdown or JSON.

## Requirements

The script depends on PyMuPDF (`fitz`). If the dependency is missing, install it first:

```bash
python -m pip install pymupdf
```

## Quick Reference

| Need | Use |
| --- | --- |
| Human review | Markdown output |
| Programmatic processing | JSON output |
| Per-annotation sentence context | `context` field / `**Context:**` section, located by annotation coordinates |
| Highlighted or underlined text | `selected_text` field / source text snippet |

## Basic Workflow

### Step 1: Choose output format

Prefer Markdown when the output is for reading, review, and copying.

```bash
python .claude/skills/pdf-annotation-extractor/scripts/extract_pdf_annotations.py \
  ./paper-annotation.pdf \
  --output ./paper-annotation_annotations.md
```

Use JSON when structured data is needed:

```bash
python .claude/skills/pdf-annotation-extractor/scripts/extract_pdf_annotations.py \
  ./paper-annotation.pdf \
  --format json \
  --output ./paper-annotation_annotations.json
```

### Step 2: Check extraction summary

After completion, the script prints:

- Output file path
- PDF page count
- Annotation count

If `annotations: 0`, the script did not find embedded annotations in the PDF. Common causes:

- Highlights are not PDF annotations but graphics "baked" into the page content.
- Annotations exist in an external reader database and were not written back into the PDF file.
- The file is scanned, so the page has no extractable text.

### Step 3: Review output

Markdown output structure:

```markdown
# PDF Annotation Extraction

## Annotation Summary

### Annotation 1 — Page N (Highlight)

**Source text snippet:**

> selected annotated text

**Context:**

> sentence before the annotation. selected annotated text. sentence after the annotation.

**Annotation comment:**
...
```

JSON output fields:

- `source_pdf`
- `page_count`
- `annotation_count`
- `annotations[]`: each annotation and its `page`, `type`, `author`, `created`, `modified`, `comment`, `selected_text`, and `context`

## Script

- `scripts/extract_pdf_annotations.py`: uses PyMuPDF to extract PDF annotations, corresponding source text snippets, and coordinate-located sentence context, then outputs Markdown or JSON.

## Quality Checks

Before finishing the task, check:

1. The output file exists and is non-empty.
2. The page count matches the actual PDF page count.
3. If the PDF visibly contains annotations, `annotation_count` is greater than 0.
4. Spot-check 1–2 annotations and confirm that `selected_text` matches the highlighted/annotated location in the PDF.
5. Confirm every item in `annotations[]` has a `context` field and every Markdown annotation has a Context section; if context is empty, the page likely has no extractable surrounding text.
6. If the annotation count is 0, tell the user that annotations may not be embedded in the PDF, rather than treating it as a script failure.

## Common Mistakes

- Do not locate context with plain string search for `selected_text`; repeated text can match the wrong occurrence. Use annotation coordinates.
- Do not treat `selected_text` as context; context must span from the previous period to the next period around the coordinate-located selection.
- Do not add context only for highlights; sticky notes, underlines, strikeouts, and text comments need `context` too.
- Do not omit `context` from JSON because Markdown is the main review format; downstream tools need the same field.
