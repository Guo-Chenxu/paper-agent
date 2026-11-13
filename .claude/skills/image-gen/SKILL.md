---
name: image-gen
description: "Use when creating, redrawing, or revising any figure for an academic paper or report: experiment result plots drawn with Python or matplotlib from measured data, and architecture diagrams, flowcharts, pipelines, workflows, method illustrations, worked examples, or other non-data figures, including subfigures and figure changes requested by reviewers or humans."
argument-hint: "Enter the figure purpose, paper context, and output filename, for example fig_architecture or fig_throughput"
user-invocable: true
---

# Image Generation Skill

Every figure in a paper or report follows this skill. Experiment result figures are plotted with Python from measured data. Every other figure is written by hand as SVG. Both kinds must meet the same figure requirements.

## Choose the Figure Type

One question decides the type: does the figure plot values that the experiment code measured?

| | Experiment plot | SVG figure |
|---|---|---|
| Content | Values read from experiment outputs: line, bar, scatter, CDF, box, heatmap, or breakdown charts, including measurements that motivate the problem | Architecture diagrams, flowcharts, pipelines, workflows, method illustrations, worked examples, timelines, and schematic sketches |
| Tool | Python plotting code (matplotlib) | SVG written directly by the model |
| Source | A plot script under `experiments/` that reads `experiment_data/` | `figures/<name>.svg` |
| Workflow | [Experiment Plot Workflow](#experiment-plot-workflow) | [SVG Figure Workflow](#svg-figure-workflow) |

- Every figure that is not an experiment plot is a handwritten SVG. TikZ/PGF, matplotlib, Graphviz, Mermaid, draw.io, slide software, and AI image generators are never used to draw it.
- A schematic curve or chart that illustrates an idea without measured data is an SVG figure. It carries no numeric tick values, so a reader cannot mistake it for a result.
- An experiment plot is regenerated from its script after every change. Its PDF or PNG is never edited by hand.
- Tables and pseudocode stay in LaTeX and are outside this skill.

## Figure Requirements

Every figure of either type must meet these requirements. They take priority over layout convenience.

1. **One panel per figure.** Each generated image contains exactly one figure. When the paper needs several subfigures, generate one source and one PDF per subfigure, then arrange them in LaTeX (for example with `subfigure`/`subcaption`). Drawing several subfigures as panels inside a single image is forbidden, and this includes `plt.subplots(nrows, ncols)` grids. Subfigures that the reader compares use the same size and, for plots, the same axis ranges.
2. **Minimal text.** Do not put paragraphs or full sentences inside the figure. Use short labels (names or short noun phrases). When an element needs explanation, add at most one brief phrase. Longer explanations belong in the caption and body text.
3. **No overlaps.** Text never overlaps other text, boxes, icons, embedded images, lines, or data marks. Boxes, icons, and images never overlap each other. The only allowed overlap is nesting: a label fully inside its own box, or a box fully inside its container. No connector, border, guide line, or grid line runs through, over, or under a label. Every label keeps visible clearance from all strokes and marks around it. In plots, the legend and annotations sit in an empty region or outside the axes and never cover lines, markers, bars, error bars, or shaded bands, and tick labels never collide.
4. **Clear and unambiguous.** A reader must interpret the figure in exactly one way. Each color, shape, line style, and arrow type carries one meaning throughout the figure, with a legend when several encodings are used. Every arrow has an obvious source, target, and direction. Avoid tangled crossings and icons or symbols open to multiple readings. Across the whole paper, each method keeps the same color, marker, and line style.
5. **Print size and one font.** Draw every figure at its final printed width, so LaTeX inserts it without scaling. Text is at least 7 pt, and main labels use 8–10 pt. All figures of a paper use one installed font family, preferably the paper's body font (ACM: `Linux Libertine O`; IEEE: a Times-like font). When the body font is unavailable or does not embed cleanly in plots (see the plot font convention), all figures use one other installed family instead.
6. **Readable in grayscale.** Use a small, colorblind-safe palette, and add a second cue to every color: stroke style, marker, hatch, pattern, or label.
7. **Real data only.** Every number in a figure comes from actual experiment outputs. SVG figures never show numbers that look like experimental results unless they are taken from those outputs.

SVG figures must also meet these two requirements:

8. **Every connector lands on its target.** Each line, arrow, and polyline terminates at a defined anchor: the border of the source shape and the border of the target shape, or a labeled node, bracket, or tick. No segment ends in empty space, and no segment stops short of or passes through the shape it connects. Elbow connectors stay orthogonal and turn at coordinates computed from box geometry, so that moving a box keeps the connector attached to it.
9. **Information-rich.** The figure must express the actual content precisely. A figure made of a few labeled boxes joined by arrows is not acceptable. Show the concrete structure instead: internal sub-components, what flows along each arrow (data, messages, key variables, or shapes), inputs and outputs, step order, and the key mechanism that distinguishes the method. A small concrete example instance often helps. Convey this information through layout, grouping, visual encoding, and compact symbols, not through added text.

Experiment plots must also meet these five requirements:

10. **Traceable data.** The plot script reads every plotted value from files in `experiment_data/` that the experiment code wrote. No value is typed into the script or edited by hand, and rerunning the script reproduces the figure.
11. **Labeled axes, no title.** Each axis label names the quantity and its unit, such as `Latency (ms)`. A unitless count names only the quantity, such as `Batch size`. The plot has no title, because the LaTeX caption carries it.
12. **Spread shown.** When an experiment has repeated runs or seeds, plot the mean with error bars or a shaded band for the standard deviation or a 95% confidence interval. The caption states which one and over how many runs, and says so when the error bars are smaller than the markers.
13. **Honest axes.** Bar charts start at zero. Values that span orders of magnitude use a log scale whose tick labels show the base (such as 10² or 2⁴), and the caption mentions it. Comparable subfigures share axis ranges.
14. **Visible message.** The comparison that the text claims can be read directly from the plot, and the proposed method stands out through color and line weight.

## SVG Figure Workflow

### Renderers

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

### Outputs

- `figures/<name>.svg`: editable source, written by the model.
- `figures/<name>.pdf`: vector PDF sized to the SVG, inserted into LaTeX.
- `figures/.preview/<name>.png`: raster preview used only for inspection. Delete it once the figure is final.

### Script

`scripts/render_svg.py` loads the SVG in Chromium, writes the PNG and/or PDF, and prints a JSON report:

```json
{"size_pt": [504.0, 220.0], "png": "...", "pdf": "...", "issues": ["stroke touches text: #arrow-kv and #lbl-cache \"Shared KV cache\""]}
```

`size_pt` is in SVG points (1/72 in). `issues` lists layout problems detected from rendered geometry: text off the canvas, text overflowing its enclosing `<rect>`, overlapping text, strokes that touch a label, text over an `<image>`, text partially covering a shape, shapes or images that partially overlap, and clipped `<foreignObject>` content. The checks are heuristic, so an empty list does not replace visual inspection, and a reported issue may occasionally be intentional.

### 1. Plan

Before writing SVG, state in a few lines:

- The single message the figure must convey and the paper section it supports.
- Components, their grouping, and the flow direction.
- The concrete details beyond component names that make the figure information-rich: sub-components, what each arrow carries, the key mechanism, and any example instance.
- The visual encoding: what each color, shape, and line style means.
- Connector routing: which shape borders each line attaches to, and where the text lanes sit so that no line crosses a label.
- Exact labels, taken verbatim from the paper's terminology and kept short.
- Target width: single column (`240pt`) or full width (`504pt`) for the ACM `sigconf` template. An SVG point is 1/72 in, slightly larger than a TeX point, so these match the template's 241 and 506 TeX points. For another template, print `\the\columnwidth` and `\the\textwidth` and multiply by 72/72.27.

### 2. Write the SVG

Write `figures/<name>.svg` directly with the Write tool. Any SVG or embedded HTML/CSS feature that Chromium renders is allowed. These conventions keep the output predictable:

- Size the canvas at final print size: `width="504pt" height="220pt" viewBox="0 0 504 220"`. Then `font-size` values equal printed point sizes.
- Use the font family chosen under requirement 5, the same family as the experiment plots. Web fonts via `@font-face` are fine; they are embedded into the PDF.
- Draw a white background covering the full canvas.
- For two-line or rich labels, either break lines with `<tspan>` or use `<foreignObject>` with an HTML `<div>` for automatic wrapping or inline math-like formatting. Labels stay short either way; never use `<foreignObject>` to place paragraphs. A figure that uses `<foreignObject>` must be rendered with Chromium.
- Give important elements an `id` so the issue report points to them.
- Define arrowheads once in `<defs>` with `<marker>` and make arrows end on box edges.
- Anchor every connector to explicit geometry. Compute the start and end points from the source and target box coordinates, so that each endpoint sits on a box border or on a labeled node. Pull the arrowhead back by a few points so the marker tip touches the border instead of crossing it. No connector may end in open space or stop short of the shape it points to.
- Route lines clear of text. Reserve a lane for each connector and keep label bounding boxes outside it. When a label must sit on an edge, place it in a gap between two segments or offset it perpendicular to the line, and keep at least 3 pt of clearance from the stroke. Adjust label lengths and box sizes early, because a longer label can push a line into neighboring text.
- Reserve space for every label, icon, and image before placing neighbors. Keep at least 3 pt between a label and any box border it does not sit inside, and at least 4 pt between sibling boxes, icons, and images.
- Keep coordinates on a regular grid (multiples of 4) so alignment edits stay easy.
- Embedded raster images (icons, screenshots) are allowed; reference them by a path relative to the SVG or as data URIs, and keep their resolution high enough for print.

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
- [ ] No text overlaps other text, boxes, icons, images, or lines. No boxes, icons, or images overlap each other, except a shape nested fully inside its container.
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

For key figures such as the system overview, run an independent check after the checklist passes. Draft the caption first. Then spawn one sub-agent that reads only the PNG preview, the draft caption, and the paragraph that cites the figure. It describes what it understands the figure to show and reports blocking issues against the checklist in step 3. Any mismatch between that description and the intended message counts as a blocking ambiguity. Fix blocking issues and re-render. Run the sub-agent again only when the fixes change what the figure shows.

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

## Experiment Plot Workflow

Experiment plots are drawn by ordinary plotting code that belongs to the experiment code base. This workflow fixes what that code must produce and how the result is checked.

### Outputs

- A plot script under `experiments/` that reads `experiment_data/` and writes the figure. It is the figure's only source.
- `figures/<name>.pdf`: vector PDF at print size, inserted into LaTeX.
- `figures/.preview/<name>.png`: raster preview used only for inspection. Delete it once the figure is final.

### 1. Plan

Before writing code, state in a few lines:

- The single claim the plot must support and the paper section that makes it.
- The data files and columns the plot reads, and how repeated runs are aggregated.
- The chart form: lines for trends over a numeric x-axis, grouped bars for categorical comparisons, a CDF or box plot for distributions, stacked bars for breakdowns.
- The encoding of each method (color, marker, line style or hatch), kept identical to the paper's other plots.
- The legend position: an empty region of the axes, or outside the axes.
- Target width: `\columnwidth`, `\textwidth`, or the subfigure fraction of it.

### 2. Write the Plot Code

Follow these conventions in addition to the figure requirements:

- **Shared style.** When a paper has several plots, keep the font settings, widths, and the color, marker, and line style of every method in one module that all plot scripts import. A plot script does not define its own styles.
- **Print size.** Set `figsize` to the final printed width in inches, which is the LaTeX width in TeX points divided by 72.27 (ACM `sigconf`: 241.15 pt column, 506.30 pt text). Create the figure with `layout="constrained"` so labels fit inside it. Save without `bbox_inches="tight"`, because it changes the page size.
- **Fonts.** Set `font.family` to the family chosen under requirement 5, with 7 pt tick and legend labels and 8–9 pt axis labels. Set `pdf.fonttype` and `ps.fonttype` to 42 so fonts embed as TrueType; the default Type 3 fonts are rejected by many submission systems. matplotlib cannot embed a CFF-based `.otf` font correctly (`Linux Libertine O` and `TeX Gyre Termes` are often installed only this way), and `pdffonts` then prints "Mismatch between font type and embedded font file". In that case choose a TrueType (`.ttf`) family, such as `STIX Two Text` for a Times-like look, and use it in the SVG figures too. A `findfont: Font family ... not found` warning means the font fell back and must be fixed.
- **Colors and marks.** Use a colorblind-safe palette such as Okabe–Ito (`#D55E00`, `#0072B2`, `#009E73`, `#E69F00`, `#CC79A7`, `#56B4E9`). Pair each color with a marker and a line style, or with a hatch for bars. Give the proposed method the most salient color and a thicker line.
- **Legend and annotations.** Place the legend with an explicit `loc` in an empty region, or outside the axes with `fig.legend(loc="outside upper center", ncols=...)`. A legend inside the axes gets an opaque background without a border (`framealpha=1`, `edgecolor="none"`), and an in-axes annotation gets `bbox={"facecolor": "white", "edgecolor": "none"}`, so grid lines never show under their text. Subfigures that share a legend either carry it each, or the legend is saved as its own legend-only figure (a figure with no axes and one `fig.legend(...)`) placed above them.
- **Dense data.** Set `rasterized=True` on artists with more than about 10,000 marks, so the PDF stays small while text and axes stay vector.

### 3. Render and Inspect

Save the 3× PNG preview from the same figure object as the PDF:

```python
fig.savefig(f"figures/{name}.pdf")
fig.savefig(f"figures/.preview/{name}.png", dpi=216)  # 216 dpi = 3 px per pt, the scale of the SVG previews
```

Run `pdffonts figures/<name>.pdf`. Every font must be embedded (`emb` is `yes`), none may be `Type 3`, the names must be the intended family, and no warning may be printed. Then open the preview with the Read tool and check every item below. Thin grid lines under text are easy to miss, so look closely at the legend and annotation regions. Write down each failing item with the element it concerns.

- [ ] `figsize` equals the target LaTeX width, and `pdffonts` passes as described above.
- [ ] No text overlaps other text. The legend and annotations cover no lines, markers, bars, error bars, or shaded bands, no grid line runs under their text, and tick labels do not collide.
- [ ] Text is readable at print size, and tick labels are neither crowded nor needlessly rotated.
- [ ] Each axis label names the quantity and its unit, and the plot has no title.
- [ ] Each method has the same color, marker, and line style as in the other plots, and legend names match the paper text.
- [ ] Repeated runs show their spread, and the caption says what the spread represents.
- [ ] Bar charts start at zero, wide value ranges use a log scale that the ticks and caption make evident, and comparable subfigures share axis ranges.
- [ ] The comparison claimed in the text is visible at a glance, and the proposed method stands out.
- [ ] Colors remain distinguishable in grayscale.
- [ ] The figure holds one axes, and every plotted value comes from files in `experiment_data/`.

### 4. Revise

Fix every failing item by editing the plot code, rerun it, and re-inspect. Never edit the PDF or the preview. Repeat steps 3–4 until all items pass, up to 5 rounds. If items still fail after 5 rounds, record them in the stage report and continue.

For the plot that carries the paper's main result, run the independent sub-agent check described in step 4 of the SVG workflow, using the checklist in step 3 above.

### 5. Insert

The PDF is already at print width, so insert it with `\includegraphics[width=\linewidth]{figures/<name>.pdf}`. Write a caption that states what the plot shows and what the error bars represent. Delete the preview. Record which script and data files produce each figure in the experiment report.

## Quality Checks

Before considering any figure complete:

1. All checklist items of its workflow pass, or remaining failures are recorded.
2. `figures/<name>.pdf` exists and the compiled paper shows it correctly, with text selectable (vector, not rasterized).
3. The caption and surrounding text describe the figure accurately.
4. The source stays in place for later revisions: the SVG next to the PDF, or the plot script under `experiments/`. Revisions edit the source, never the PDF.
