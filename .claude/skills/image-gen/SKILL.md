---
name: image-gen
description: "Use when creating academic paper figures, architecture diagrams, flowcharts, method illustrations, or supplemental figures. The model writes the figure directly as SVG, renders it with headless Chromium (or rsvg-convert), inspects the PNG plus automatic layout checks, and revises the SVG until it passes a visual checklist, then exports a vector PDF for LaTeX."
argument-hint: "Enter the figure purpose, paper context, and output filename, for example fig_architecture"
user-invocable: true
---

# Image Generation Skill

## When To Use

Use this skill when a paper or report needs a hand-designed figure:

1. Architecture diagrams, flowcharts, pipelines, and method illustrations.
2. Figures added or redrawn based on writing, reviewer, or human feedback.

Do not use this skill for experiment plots. Plots must be produced from measured data by the experiment/visualization code.

## Renderers

No API key or external image model is needed. Two renderers are supported, and both produce a vector PDF with embedded fonts and a page size equal to the SVG canvas.

| | Chromium (`render_svg.py`, default) | `rsvg-convert` (librsvg) |
|---|---|---|
| SVG features | Full, including `<foreignObject>` with HTML/CSS, filters, masks, web fonts | Filters, markers, gradients, masks, CSS; `<foreignObject>` content is silently dropped |
| Automatic layout report | Yes | No, visual inspection only |
| Footprint | Python package plus a ~110 MB browser | One small CLI binary, starts instantly |

Use Chromium by default. Use `rsvg-convert` when Chromium is unavailable or for fast previews of figures that contain no `<foreignObject>`.

Install Chromium inside the project conda environment:

```bash
conda run -n <PYTHON_ENV> python -m pip install playwright==1.58.0
conda run -n <PYTHON_ENV> python -m playwright install --with-deps chromium
```

Install `rsvg-convert`:

```bash
sudo apt install librsvg2-bin   # Debian/Ubuntu
brew install librsvg            # macOS
```

Both renderers resolve font families through fontconfig, so a font that is not installed falls back silently (for example, Helvetica becomes DejaVu Sans). Check the actual font with `fc-match "<family>"` and confirm it in the PNG preview.

## Outputs

- `figures/<name>.svg`: editable source, written by the model.
- `figures/<name>.pdf`: vector PDF sized to the SVG, inserted into LaTeX.
- `figures/.preview/<name>.png`: raster preview used only for inspection. Delete it once the figure is final.

## Script

`scripts/render_svg.py` loads the SVG in Chromium, writes the PNG and/or PDF, and prints a JSON report:

```json
{"size_pt": [504.0, 220.0], "png": "...", "pdf": "...", "issues": ["overflows box: text #lbl-cache \"Shared KV cache\""]}
```

`issues` lists layout problems detected from rendered geometry: text off the canvas, text overflowing its enclosing `<rect>`, overlapping text, and clipped `<foreignObject>` content. The checks are heuristic, so an empty list does not replace visual inspection, and a reported issue may occasionally be intentional.

## Figure Requirements

Every figure must meet these six requirements. They take priority over layout convenience.

1. **One panel per figure.** Each generated image contains exactly one figure. When the paper needs several subfigures, generate one SVG and one PDF per subfigure, then arrange them in LaTeX (for example with `subfigure`/`subcaption`). Drawing several subfigures as panels inside a single image is forbidden.
2. **Minimal text.** Do not put paragraphs or full sentences inside the figure. Use short labels (names or short noun phrases). When an element needs explanation, add at most one brief phrase. Longer explanations belong in the caption and body text.
3. **Every connector lands on its target.** Each line, arrow, and polyline terminates at a defined anchor: the border of the source shape and the border of the target shape, or a labeled node, bracket, or tick. No segment ends in empty space, and no segment stops short of or passes through the shape it connects. Elbow connectors stay orthogonal and turn at coordinates computed from box geometry, so that moving a box keeps the connector attached to it.
4. **Lines never touch text.** No connector, border, or guide line runs through, over, or under a label. Keep clear of the label's bounding box on all four sides, and route the line around the text or move the text off the lane. When a label must sit near a line, leave visible clearance and, if needed, break the line into two segments with a gap for the label.
5. **Clear and unambiguous.** A reader must interpret the figure in exactly one way. Each color, shape, line style, and arrow type carries one meaning throughout the figure, with a legend when several encodings are used. Every arrow has an obvious source, target, and direction. Avoid tangled crossings and icons or symbols open to multiple readings.
6. **Information-rich.** The figure must express the actual content precisely. A figure made of a few labeled boxes joined by arrows is not acceptable. Show the concrete structure instead: internal sub-components, what flows along each arrow (data, messages, key variables, or shapes), inputs and outputs, step order, and the key mechanism that distinguishes the method. A small concrete example instance often helps. Convey this information through layout, grouping, visual encoding, and compact symbols, not through added text.

## Workflow

### 1. Plan

Before writing SVG, state in a few lines:

- The single message the figure must convey and the paper section it supports.
- Components, their grouping, and the flow direction.
- The concrete details beyond component names that make the figure information-rich: sub-components, what each arrow carries, the key mechanism, and any example instance.
- The visual encoding: what each color, shape, and line style means.
- Connector routing: which shape borders each line attaches to, and where the text lanes sit so that no line crosses a label.
- Exact labels, taken verbatim from the paper's terminology and kept short.
- Target width: single column (`240pt`) or full width (`504pt`), unless the template differs.

### 2. Write the SVG

Write `figures/<name>.svg` directly with the Write tool. Any SVG or embedded HTML/CSS feature that Chromium renders is allowed. These conventions keep the output predictable:

- Size the canvas at final print size: `width="504pt" height="220pt" viewBox="0 0 504 220"`. Then `font-size` values equal printed point sizes. Use at least 7 for any text and 8–10 for main labels.
- Match the paper's font when it is available (e.g., Times/Libertine for body-matched labels), otherwise use a clean sans-serif stack such as `Helvetica, Arial, sans-serif`. Web fonts via `@font-face` are fine; they are embedded into the PDF.
- Draw a white background covering the full canvas.
- For two-line or rich labels, either break lines with `<tspan>` or use `<foreignObject>` with an HTML `<div>` for automatic wrapping or inline math-like formatting. Labels stay short either way; never use `<foreignObject>` to place paragraphs. A figure that uses `<foreignObject>` must be rendered with Chromium.
- Give important elements an `id` so the issue report points to them.
- Define arrowheads once in `<defs>` with `<marker>` and make arrows end on box edges.
- Anchor every connector to explicit geometry. Compute the start and end points from the source and target box coordinates, so that each endpoint sits on a box border or on a labeled node. Pull the arrowhead back by a few points so the marker tip touches the border instead of crossing it. No connector may end in open space or stop short of the shape it points to.
- Route lines clear of text. Reserve a lane for each connector and keep label bounding boxes outside it. When a label must sit on an edge, place it in a gap between two segments or offset it perpendicular to the line, and keep at least 3 pt of clearance from the stroke. Adjust label lengths and box sizes early, because a longer label can push a line into neighboring text.
- Use a small, colorblind-safe palette. Elements must stay distinguishable in grayscale; add stroke style, patterns, or labels in addition to color.
- Keep coordinates on a regular grid (multiples of 4) so alignment edits stay easy.
- Embedded raster images (icons, screenshots) are allowed; reference them by a path relative to the SVG or as data URIs, and keep their resolution high enough for print.
- Do not draw numbers that look like experimental results unless they come from actual experiment outputs.

### 3. Render and Inspect

Render a 3× PNG preview from the repository root:

```bash
conda run -n <PYTHON_ENV> python .claude/skills/image-gen/scripts/render_svg.py \
  figures/<name>.svg --png figures/.preview/<name>.png
```

With `rsvg-convert` (no layout report; `-z 3` gives the same 3× scale):

```bash
mkdir -p figures/.preview
rsvg-convert -z 3 -b white -o figures/.preview/<name>.png figures/<name>.svg
```

Read the JSON report (Chromium only), then open `figures/.preview/<name>.png` with the Read tool and check every item below. Write down each failing item with the element it concerns.

- [ ] Every reported `issues` entry is fixed or confirmed intentional.
- [ ] No text is clipped, overflows its box, or runs off the canvas.
- [ ] No unintended overlap between text, boxes, and arrows.
- [ ] Every connector has an anchor at both ends: it starts on the source shape or node and ends on the target border, with no endpoint floating in empty space.
- [ ] No connector crosses, touches, or passes under any text. Labels on edges sit in a gap or in clear offset space, and every label keeps visible clearance from all strokes.
- [ ] Every arrow starts and ends at the intended element, and the direction matches the described flow.
- [ ] Boxes at the same level are aligned and evenly spaced. Margins are balanced with no large empty regions.
- [ ] Text is readable at print size (the preview is 3× scale, so text should look large and clear).
- [ ] Visual hierarchy is clear: the main path or component stands out from auxiliary elements.
- [ ] Labels and component names match the paper text exactly.
- [ ] No paragraphs or full sentences appear in the figure. Labels are short, and annotations are brief phrases.
- [ ] The figure reads in only one way. Each color, shape, line style, and arrow type has one consistent meaning, and a legend explains them when needed.
- [ ] The figure is information-rich. It shows internal structure, what flows between components, and the key mechanism, not just a few labeled boxes.
- [ ] The image contains exactly one figure. No multi-panel or subfigure layout is drawn inside a single canvas.
- [ ] Colors remain distinguishable in grayscale.
- [ ] The figure contains no fabricated data.

### 4. Revise

Fix every failing item by editing the SVG (prefer targeted Edit calls on coordinates, sizes, and labels), re-render, and re-inspect. Repeat steps 3–4 until all items pass, up to 5 rounds. If items still fail after 5 rounds, record them in the stage report and continue.

For key figures such as the system overview, after the checklist passes, spawn one independent sub-agent that reads only the PNG and the figure's caption and paragraph, describes what it understands the figure to show, and reports blocking issues against the same checklist. Any mismatch between that description and the intended message counts as a blocking ambiguity. Fix blocking issues, then re-render once more.

### 5. Export and Insert

Export the final vector PDF and remove the preview:

```bash
conda run -n <PYTHON_ENV> python .claude/skills/image-gen/scripts/render_svg.py \
  figures/<name>.svg --pdf figures/<name>.pdf
rm figures/.preview/<name>.png
```

With `rsvg-convert`:

```bash
rsvg-convert -f pdf -o figures/<name>.pdf figures/<name>.svg
rm figures/.preview/<name>.png
```

The PDF page equals the SVG canvas, so insert it with `\includegraphics[width=\linewidth]{figures/<name>.pdf}` (or `\textwidth` for full-width figures), and write a caption that explains what the figure shows.

## Quality Checks

Before considering the figure complete:

1. All checklist items in step 3 pass, or remaining failures are recorded.
2. `figures/<name>.pdf` exists and the compiled paper shows it correctly, with text selectable (vector, not rasterized).
3. The caption and surrounding text describe the figure accurately.
4. The SVG source is kept next to the PDF so later revisions edit the source, not the PDF.
