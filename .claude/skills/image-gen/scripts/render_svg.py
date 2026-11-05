"""Render an SVG with headless Chromium to a PNG preview and/or a vector PDF, and report layout issues."""

import argparse
import json
import math
import sys
from pathlib import Path

from playwright.sync_api import Browser, Page, sync_playwright

# Returns the SVG size in CSS px; width/height attributes take precedence over the viewBox.
SIZE_JS = """() => {
  const svg = document.documentElement;
  if (!(svg instanceof SVGSVGElement)) throw new Error("root element is not <svg>");
  if (svg.hasAttribute("width") && svg.hasAttribute("height")) {
    const r = svg.getBoundingClientRect();
    return [r.width, r.height];
  }
  const vb = svg.viewBox.baseVal;
  if (vb && vb.width > 0 && vb.height > 0) return [vb.width, vb.height];
  throw new Error("SVG needs width/height attributes or a viewBox");
}"""

# Heuristic layout checks on rendered geometry; visual inspection is still required.
CHECK_JS = """() => {
  const tol = 1;
  const root = document.documentElement.getBoundingClientRect();
  const label = el => (el.id ? "#" + el.id + " " : "") +
    JSON.stringify((el.textContent || "").trim().replace(/\\s+/g, " ").slice(0, 40));
  const inside = (a, b) => a.left >= b.left - tol && a.top >= b.top - tol &&
    a.right <= b.right + tol && a.bottom <= b.bottom + tol;
  const overlap = (a, b) => Math.min(a.right, b.right) - Math.max(a.left, b.left) > tol &&
    Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top) > tol;
  const issues = [];

  const texts = [...document.querySelectorAll("text")]
    .filter(el => el.textContent.trim())
    .map(el => ({ el, r: el.getBoundingClientRect() }));
  // Full-canvas rects are backgrounds, not containers.
  const boxes = [...document.querySelectorAll("rect")]
    .map(el => el.getBoundingClientRect())
    .filter(r => r.width < root.width - tol || r.height < root.height - tol);

  for (const t of texts) {
    if (!inside(t.r, root)) issues.push("off-canvas: text " + label(t.el));
    const cx = (t.r.left + t.r.right) / 2, cy = (t.r.top + t.r.bottom) / 2;
    const holder = boxes
      .filter(b => cx >= b.left && cx <= b.right && cy >= b.top && cy <= b.bottom)
      .sort((a, b) => a.width * a.height - b.width * b.height)[0];
    if (holder && !inside(t.r, holder)) issues.push("overflows box: text " + label(t.el));
  }
  for (let i = 0; i < texts.length; i++)
    for (let j = i + 1; j < texts.length; j++)
      if (overlap(texts[i].r, texts[j].r))
        issues.push("text overlap: " + label(texts[i].el) + " and " + label(texts[j].el));

  for (const fo of document.querySelectorAll("foreignObject")) {
    const c = fo.firstElementChild;
    if (!c) continue;
    if (c.scrollWidth > fo.width.baseVal.value + tol || c.scrollHeight > fo.height.baseVal.value + tol)
      issues.push("clipped foreignObject content: " + label(fo));
    if (!inside(fo.getBoundingClientRect(), root)) issues.push("off-canvas: foreignObject " + label(fo));
  }
  return issues;
}"""


def open_svg(browser: Browser, svg: Path, scale: float) -> tuple[Page, float, float]:
    """Load the SVG in a page whose viewport matches the SVG size; returns the page and size in CSS px."""
    page: Page = browser.new_context(device_scale_factor=scale).new_page()
    page.goto(svg.resolve().as_uri(), wait_until="networkidle")
    page.evaluate("() => document.fonts.ready.then(() => true)")
    width, height = page.evaluate(SIZE_JS)
    page.set_viewport_size({"width": math.ceil(width), "height": math.ceil(height)})
    return page, float(width), float(height)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("svg", type=Path, help="input SVG file")
    parser.add_argument("--png", type=Path, help="PNG preview output path")
    parser.add_argument("--scale", type=float, default=3.0, help="PNG pixel density multiplier")
    parser.add_argument("--pdf", type=Path, help="vector PDF output path, sized to the SVG")
    args = parser.parse_args()

    svg: Path = args.svg
    if not svg.is_file():
        print(f"SVG not found: {svg}", file=sys.stderr)
        return 1

    with sync_playwright() as p:
        browser: Browser = p.chromium.launch()
        try:
            page, width, height = open_svg(browser, svg, args.scale)
            issues: list[str] = page.evaluate(CHECK_JS)
            if args.png:
                args.png.parent.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(args.png), clip={"x": 0, "y": 0, "width": width, "height": height})
            if args.pdf:
                args.pdf.parent.mkdir(parents=True, exist_ok=True)
                page.pdf(
                    path=str(args.pdf),
                    width=f"{width}px",
                    height=f"{height}px",
                    print_background=True,
                    margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
                    page_ranges="1",
                )
        finally:
            browser.close()

    # 1 CSS px = 0.75 pt
    report: dict[str, object] = {
        "size_pt": [round(width * 0.75, 1), round(height * 0.75, 1)],
        "png": str(args.png) if args.png else None,
        "pdf": str(args.pdf) if args.pdf else None,
        "issues": issues,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
