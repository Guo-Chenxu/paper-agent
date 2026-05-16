#!/usr/bin/env python3
"""Extract PDF annotations into Markdown or JSON."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import fitz


def annot_info_value(info: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = info.get(key)
        if value:
            return str(value)
    return ""


def format_pdf_date(raw: str) -> str:
    if not raw:
        return ""
    if not raw.startswith("D:"):
        return raw
    value = raw[2:16]
    try:
        return datetime.strptime(value, "%Y%m%d%H%M%S").isoformat(sep=" ")
    except ValueError:
        return raw


def point_xy(point: Any) -> tuple[float, float]:
    if hasattr(point, "x") and hasattr(point, "y"):
        return float(point.x), float(point.y)
    return float(point[0]), float(point[1])


def rects_from_vertices(vertices: list[Any] | None) -> list[fitz.Rect]:
    if not vertices:
        return []
    rects: list[fitz.Rect] = []
    for i in range(0, len(vertices), 4):
        quad = vertices[i : i + 4]
        if len(quad) != 4:
            continue
        points = [point_xy(p) for p in quad]
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        rects.append(fitz.Rect(min(xs), min(ys), max(xs), max(ys)))
    return rects


def expanded_rect(rect: fitz.Rect, margin: float = 1.5) -> fitz.Rect:
    expanded = fitz.Rect(rect)
    expanded.x0 -= margin
    expanded.y0 -= margin
    expanded.x1 += margin
    expanded.y1 += margin
    return expanded


def word_matches_rect(word_rect: fitz.Rect, rect: fitz.Rect) -> bool:
    rect = expanded_rect(rect)
    center = fitz.Point((word_rect.x0 + word_rect.x1) / 2, (word_rect.y0 + word_rect.y1) / 2)
    if center in rect:
        return True
    intersection = word_rect & rect
    if intersection.is_empty or word_rect.get_area() == 0:
        return False
    return intersection.get_area() / word_rect.get_area() >= 0.35


def normalize_whitespace(text: str) -> str:
    return " ".join(text.split())


def annotation_rects(annot: fitz.Annot) -> list[fitz.Rect]:
    rects = rects_from_vertices(annot.vertices)
    if rects:
        return rects
    return [annot.rect]


def page_words(page: fitz.Page) -> list[tuple[tuple[int, int, int], str, fitz.Rect]]:
    words: list[tuple[tuple[int, int, int], str, fitz.Rect]] = []
    for index, word in enumerate(page.get_text("words")):
        block_no = int(word[5]) if len(word) > 5 else 0
        line_no = int(word[6]) if len(word) > 6 else 0
        word_no = int(word[7]) if len(word) > 7 else index
        words.append(((block_no, line_no, word_no), str(word[4]), fitz.Rect(word[:4])))
    return sorted(words, key=lambda item: item[0])


def selected_page_words(page: fitz.Page, annot: fitz.Annot) -> list[tuple[tuple[int, int, int], str, fitz.Rect]]:
    rects = annotation_rects(annot)
    selected: dict[tuple[int, int, int], tuple[tuple[int, int, int], str, fitz.Rect]] = {}
    for word in page_words(page):
        if any(word_matches_rect(word[2], rect) for rect in rects):
            selected[word[0]] = word
    return sorted(selected.values(), key=lambda item: item[0])


def words_to_text(words: list[tuple[tuple[int, int, int], str, fitz.Rect]]) -> str:
    lines: list[str] = []
    current_line: tuple[int, int] | None = None
    current_words: list[str] = []
    for key, text, _rect in words:
        line_key = (key[0], key[1])
        if current_line is not None and line_key != current_line:
            lines.append(" ".join(current_words))
            current_words = []
        current_line = line_key
        current_words.append(text)
    if current_words:
        lines.append(" ".join(current_words))
    return " ".join(lines).strip()


def extract_selected_text(page: fitz.Page, annot: fitz.Annot) -> str:
    selected = selected_page_words(page, annot)
    if selected:
        return words_to_text(selected)

    return "\n".join(page.get_text("text", clip=rect).strip() for rect in annotation_rects(annot)).strip()


def ends_sentence(text: str) -> bool:
    return text.rstrip().endswith((".", "。"))


def sentence_context_from_words(
    words: list[tuple[tuple[int, int, int], str, fitz.Rect]],
    selected: list[tuple[tuple[int, int, int], str, fitz.Rect]],
) -> str:
    selected_keys = {word[0] for word in selected}
    selected_indices = [index for index, word in enumerate(words) if word[0] in selected_keys]
    if not selected_indices:
        return ""

    first_selected = min(selected_indices)
    last_selected = max(selected_indices)

    start = 0
    for index in range(first_selected - 1, -1, -1):
        if ends_sentence(words[index][1]):
            start = index + 1
            break

    end = len(words) - 1
    for index in range(last_selected, len(words)):
        if ends_sentence(words[index][1]):
            end = index
            break

    return normalize_whitespace(words_to_text(words[start : end + 1]))


def extract_context(page: fitz.Page, annot: fitz.Annot) -> str:
    selected = selected_page_words(page, annot)
    if selected:
        return sentence_context_from_words(page_words(page), selected)

    rects = annotation_rects(annot)
    context_parts: list[str] = []
    for rect in rects:
        context_rect = fitz.Rect(rect)
        context_rect.x0 -= 40
        context_rect.y0 -= 80
        context_rect.x1 += 40
        context_rect.y1 += 80
        context_parts.append(page.get_text("text", clip=context_rect))
    return normalize_whitespace(" ".join(context_parts))


def extract_pdf(pdf_path: Path) -> dict[str, Any]:
    doc = fitz.open(pdf_path)
    annotations: list[dict[str, Any]] = []

    for page_index, page in enumerate(doc, start=1):
        annot = page.first_annot
        while annot:
            info = annot.info or {}
            selected_text = extract_selected_text(page, annot)
            annotation = {
                "page": page_index,
                "type": annot.type[1] if annot.type else "Unknown",
                "author": annot_info_value(info, "title", "subject"),
                "created": format_pdf_date(annot_info_value(info, "creationDate")),
                "modified": format_pdf_date(annot_info_value(info, "modDate")),
                "comment": annot_info_value(info, "content"),
                "selected_text": selected_text,
                "context": extract_context(page, annot),
            }
            annotations.append(annotation)
            annot = annot.next

    return {
        "source_pdf": str(pdf_path),
        "page_count": doc.page_count,
        "annotation_count": len(annotations),
        "annotations": annotations,
    }


def markdown_escape(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n").strip()


def write_markdown(data: dict[str, Any], output_path: Path) -> None:
    lines: list[str] = []
    lines.append(f"# PDF 批注提取\n")
    lines.append(f"- Source PDF: `{data['source_pdf']}`")
    lines.append(f"- Pages: {data['page_count']}")
    lines.append(f"- Annotations: {data['annotation_count']}\n")

    lines.append("## 批注汇总\n")
    if data["annotations"]:
        for index, item in enumerate(data["annotations"], start=1):
            lines.append(f"### 批注 {index} — Page {item['page']} ({item['type']})")
            if item.get("author"):
                lines.append(f"- Author: {item['author']}")
            if item.get("created"):
                lines.append(f"- Created: {item['created']}")
            if item.get("modified"):
                lines.append(f"- Modified: {item['modified']}")
            if item.get("selected_text"):
                lines.append("\n**原文片段：**\n")
                lines.append(f"> {markdown_escape(item['selected_text']).replace(chr(10), chr(10) + '> ')}")
            lines.append("\n**上下文：**\n")
            context = item.get("context") or "未找到可提取的上下文。"
            lines.append(f"> {markdown_escape(context).replace(chr(10), chr(10) + '> ')}")
            if item.get("comment"):
                lines.append("\n**批注内容：**\n")
                lines.append(markdown_escape(item["comment"]))
            lines.append("")
    else:
        lines.append("未发现 PDF 批注。\n")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract PDF annotations into Markdown or JSON.")
    parser.add_argument("pdf", type=Path, help="Input PDF path")
    parser.add_argument("--output", "-o", type=Path, help="Output file path")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output format")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    pdf_path = args.pdf.expanduser().resolve()
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    suffix = ".json" if args.format == "json" else ".md"
    output_path = args.output or pdf_path.with_name(f"{pdf_path.stem}_annotations{suffix}")
    output_path = output_path.expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = extract_pdf(pdf_path)
    if args.format == "json":
        output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        write_markdown(data, output_path)

    print(f"Wrote {output_path}")
    print(f"Pages: {data['page_count']}; annotations: {data['annotation_count']}")


if __name__ == "__main__":
    main()
