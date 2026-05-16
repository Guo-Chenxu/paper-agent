---
name: image-gen
description: "Generates academic paper figures with image-capable LLMs and converts each generated image to PDF. Use when SPEC.md requires .claude/skills/image-gen in paper writing or revision phases, when creating architecture diagrams or supplemental figures, or when the user asks to generate images for paper/figures. Reads IMAGE_GEN_* model settings from .env and supports gpt-image-compatible providers."
argument-hint: "Enter the image purpose, paper context, prompt, and output filename, for example fig_architecture"
user-invocable: true
---

# Image Generation Skill

## When To Use

Use this skill for SPEC.md image-generation tasks:

1. Phase 6 paper writing: generate architecture diagrams, flowcharts, method illustrations, and other figures that need to be inserted into the paper.
2. Phase 8 paper revision: add or redraw figures based on feedback.
3. Any scenario that needs to save a generated image to `paper/figures/` and provide a same-name PDF.

Do not use this skill for experiment plots that should be produced from measured data. Those belong in the experiment/visualization code.

## Configuration

The script reads model configuration from repository `.env`:

- `IMAGE_GEN_API_KEY`
- `IMAGE_GEN_BASE_URL`
- `IMAGE_GEN_MODEL`
- `IMAGE_GEN_VENDOR`

Supported vendor values:

- `gemini`: calls Gemini-style `generateContent` image output, or OpenAI-compatible chat image output for OneAPI-style gateways.
- `openai` or `gpt-image`: calls OpenAI-compatible `/v1/images/generations`.

For gpt-image, set for example:

```bash
IMAGE_GEN_VENDOR=gpt-image
IMAGE_GEN_MODEL=gpt-image-1
```

## Workflow

1. Write a precise prompt that includes the figure purpose, desired layout, labels, and academic style.
2. Run the generator from the repository root in the conda environment.
3. Verify both image and PDF outputs exist in `paper/figures/`.
4. Insert the PDF in LaTeX unless the template specifically requires raster images.

Example:

```bash
python .claude/skills/image-gen/scripts/generate_image.py \
  --name fig_architecture \
  --prompt "Create a clean academic architecture diagram for ... Use white background, vector-like style, and readable labels."
```

Expected outputs:

- `paper/figures/fig_architecture.png` or `paper/figures/fig_architecture.jpg`
- `paper/figures/fig_architecture.pdf`

## Script

- `scripts/generate_image.py`: loads `.env`, calls the configured image model, saves the generated image, then converts it to PDF using `img2pdf.convert(...)` as in `image2pdf.py`.

## Quality Checks

Before considering the figure complete:

1. The image matches the surrounding paper text and all labels are readable.
2. The generated PDF opens correctly.
3. The LaTeX source references the figure and its caption accurately describes the content.
4. No experimental result is fabricated in the image.
