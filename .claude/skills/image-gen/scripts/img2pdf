#!/usr/bin/env python3
"""Convert a raster image into a same-name PDF wrapper."""

from __future__ import annotations

import argparse
from pathlib import Path


def convert_image(image_path: Path, output_path: Path | None = None) -> Path:
    try:
        import img2pdf
    except ImportError as exc:
        raise RuntimeError("Missing dependency: install img2pdf") from exc

    image_path = image_path.expanduser().resolve()
    pdf_path = (output_path or image_path.with_suffix(".pdf")).expanduser().resolve()
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    with open(pdf_path, "wb") as handle:
        handle.write(img2pdf.convert(image_path))
    return pdf_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert an image file to PDF.")
    parser.add_argument("image", type=Path, help="Input image path")
    parser.add_argument("--output", "-o", type=Path, help="Output PDF path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    pdf_path = convert_image(args.image, args.output)
    print(f"Wrote {pdf_path}")


if __name__ == "__main__":
    main()
