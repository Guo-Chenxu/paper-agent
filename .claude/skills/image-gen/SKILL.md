---
name: image-gen
description: "Use when creating academic paper figures, architecture diagrams, flowcharts, method illustrations, supplemental figures, or converting generated images to same-name PDFs. Reads IMAGE_GEN_* model settings from .env and supports gpt-image-compatible providers."
argument-hint: "Enter the image purpose, paper context, prompt, and output filename, for example fig_architecture"
user-invocable: true
---

# Image Generation Skill

## When To Use

Use this skill when a paper or report needs generated visual material:

1. Generate architecture diagrams, flowcharts, method illustrations, and other figures that need to be inserted into a paper.
2. Add or redraw figures based on writing, reviewer, or human feedback.
3. Save a generated image to `figures/` and provide a same-name PDF.

Do not use this skill for experiment plots that should be produced from measured data. Those belong in the experiment/visualization code.

## Configuration

The script reads model configuration from repository `.env`:

- `IMAGE_GEN_API_KEY`
- `IMAGE_GEN_BASE_URL`
- `IMAGE_GEN_MODEL`
- `IMAGE_GEN_VENDOR`

Supported vendor values:

- `gemini`: calls Gemini-style `generateContent` image output.
- `openai` or `gpt-image`: calls OpenAI-compatible `/v1/images/generations`.

For gpt-image, set for example:

```bash
IMAGE_GEN_VENDOR=gpt-image
IMAGE_GEN_MODEL=gpt-image-1
```

## Workflow

1. Write a precise prompt that includes the figure purpose, desired layout, labels, and academic style.
2. Run the generator from the repository root.
3. Verify both image and PDF outputs exist in `figures/`.
4. Insert the PDF in LaTeX unless the template specifically requires raster images.

Example:

```bash
python .claude/skills/image-gen/scripts/generate_image.py \
  --name fig_architecture \
  --prompt "Create a clean academic architecture diagram for ... Use white background, vector-like style, and readable labels."
```

Expected outputs:

- `figures/fig_architecture.png` or `figures/fig_architecture.jpg`
- `figures/fig_architecture.pdf`

## Script

- `scripts/generate_image.py`: loads `.env`, calls the configured image model, saves the generated image under `figures/`, then converts it to PDF.
- `scripts/img2pdf`: converts an existing generated image into a same-name PDF vector wrapper.

Required PDF conversion dependency:

```bash
python -m pip install img2pdf
```

## Quality Checks

Before considering the figure complete:

1. The image matches the surrounding paper text and all labels are readable.
2. The generated PDF opens correctly.
3. The LaTeX source references the figure and its caption accurately describes the content.
4. No experimental result is fabricated in the image.
