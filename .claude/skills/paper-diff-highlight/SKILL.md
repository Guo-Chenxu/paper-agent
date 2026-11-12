---
name: paper-diff-highlight
description: Use only when the user explicitly asks for a highlighted or change-marked version of a revised LaTeX paper, such as "生成高亮版", "高亮修改", "标出修改的地方", "highlight the changes", or a marked-up PDF for a rebuttal or resubmission. Never invoke it automatically after revising a paper.
argument-hint: "main .tex path; optional base git revision (default HEAD); optional style hl/color"
user-invocable: true
---

# Paper Diff Highlight

## Overview

`scripts/highlight_diff.py` compares the main `.tex` file against a git revision and writes `<name>_highlighted.tex` next to it. Only the copy gets marked up, and the original file stays untouched. Changes are located with `git diff`, then refined to the word level (character level for CJK). The new copy compiles into a PDF in which every changed span stands out. Changed `\input`/`\include` files get their own `_highlighted` copies, and the root copy is rewired to load them.

## Workflow

1. **Pick the old version.** If the revision is still uncommitted, use the default `--base HEAD`. If the revision is already committed, find the pre-revision commit with `git log --oneline -- <tex>` and pass `--base <commit>`. Add `--to <commit>` only to compare two commits while ignoring the working tree. If it is unclear which version counts as "before", ask the user.
2. **Run the script.**
   ```bash
   conda run -n <PYTHON_ENV> python .claude/skills/paper-diff-highlight/scripts/highlight_diff.py paper/paper.tex --base HEAD
   ```
3. **Read the report.** It lists every highlighted region with its line number, plus two sets of lines that do not appear highlighted in the PDF:
   - `deleted text`: removed text, which cannot be shown in the new PDF.
   - `changed but not highlighted`: preamble edits, labels, figure files and widths, verbatim, and similar structural content.
   Pass both lists on to the user.
4. **Compile the copy** with the paper's usual sequence (`<PDFLATEX_CMD>` + `bibtex`, or `xelatex` for CJK, which the CJK background needs). Use `paper_highlighted` as the job name. Check the log for errors.
5. **Spot-check** a page that contains changes (`pdftoppm -r 110 -png -f N -l N paper_highlighted.pdf /tmp/check`) to confirm the highlights land where the report says.

## Quick Reference

| Need | Option |
| --- | --- |
| Yellow background (default) | `--style hl --hl-color yellow` |
| Colored text only (most robust) | `--style color --color blue` |
| Diff two commits | `--base A --to B` |
| Custom output path (must stay in the source directory) | `-o paper/paper_marked.tex` |
| A custom command whose argument is prose | `--text-cmd revised` |
| Do not follow `\input` files | `--no-follow-inputs` |
| Avoid highlighting short unchanged runs between edits | `--merge-gap 0` |

In `hl` mode, ulem draws a background band that breaks across lines. It covers text, CJK, inline math, citations, references, and macros. Short units that ulem cannot process (siunitx commands, and citations with a space in an optional argument) get an unbreakable colored box. Display math and `\url`/`\href` fall back to `--color` text.

## What Gets Marked

- Marked: body text, section titles, captions, footnotes, list items, table cells, inline math, `\cite`/`\ref`, text macros defined in the preamble (e.g., a system-name macro), and whole display-math environments when anything inside changes.
- Not marked: deleted text, the preamble, `\label`, figure graphics, verbatim, and TikZ. These appear in the report so they can be named for the user.

## Common Mistakes

- **Wrong base.** "no highlightable change found" usually means the revision is already committed. Pass `--base <pre-revision commit>`.
- **Moving the output.** The copy relies on relative paths for figures, `.bib` files, and `\input` files, so keep it in the source directory.
- **Hand-editing `_highlighted.tex`.** Edit the real paper and regenerate the copy.
- **`hl` compile failure.** If ulem fails on an unusual construct, rerun with `--style color`.
- **CJK under LuaLaTeX.** The CJK background works only under xelatex with xeCJK (e.g., `ctexart`). Under LuaLaTeX, use `--style color`.
- **Committing the artifacts.** `*_highlighted.*` files are generated outputs. Do not stage them unless the user asks.
