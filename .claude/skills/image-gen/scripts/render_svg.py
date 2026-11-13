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
  const partial = (a, b) => overlap(a, b) && !inside(a, b) && !inside(b, a);
  const name = el => el.id ? "#" + el.id : "<" + el.tagName + ">";
  // Elements inside these containers are templates, not drawn in place.
  const drawn = el => !el.closest("defs, marker, symbol, clipPath, mask, pattern");
  const fullCanvas = r => r.width >= root.width - tol && r.height >= root.height - tol;
  const painted = (paint, opacity) => paint !== "none" && !/rgba\\(.*,\\s*0\\)$/.test(paint) && parseFloat(opacity) > 0;
  const issues = [];
  const report = msg => { if (!issues.includes(msg)) issues.push(msg); };

  const texts = [...document.querySelectorAll("text")]
    .filter(el => drawn(el) && el.textContent.trim())
    .map(el => ({ el, r: el.getBoundingClientRect() }));
  // Full-canvas rects are backgrounds, not containers.
  const boxes = [...document.querySelectorAll("rect")]
    .filter(drawn)
    .map(el => ({ el, r: el.getBoundingClientRect() }))
    .filter(b => !fullCanvas(b.r));
  const holderOf = r => {
    const cx = (r.left + r.right) / 2, cy = (r.top + r.bottom) / 2;
    return boxes
      .filter(b => cx >= b.r.left && cx <= b.r.right && cy >= b.r.top && cy <= b.r.bottom)
      .sort((a, b) => a.r.width * a.r.height - b.r.width * b.r.height)[0];
  };

  for (const t of texts) {
    if (!inside(t.r, root)) issues.push("off-canvas: text " + label(t.el));
    const holder = holderOf(t.r);
    if (holder && !inside(t.r, holder.r)) issues.push("overflows box: text " + label(t.el));
  }

  // Labels for the overlap checks: <text> plus the tight text box of each <foreignObject>.
  const labels = [...texts];
  for (const fo of document.querySelectorAll("foreignObject")) {
    if (!drawn(fo) || !fo.textContent.trim()) continue;
    const walker = document.createTreeWalker(fo, NodeFilter.SHOW_TEXT);
    let l = Infinity, t = Infinity, r = -Infinity, b = -Infinity;
    for (let n = walker.nextNode(); n; n = walker.nextNode()) {
      if (!n.textContent.trim()) continue;
      const range = document.createRange();
      range.selectNodeContents(n);
      const box = range.getBoundingClientRect();
      l = Math.min(l, box.left); t = Math.min(t, box.top); r = Math.max(r, box.right); b = Math.max(b, box.bottom);
    }
    if (r > l) labels.push({ el: fo, r: { left: l, top: t, right: r, bottom: b, width: r - l, height: b - t } });
  }
  for (let i = 0; i < labels.length; i++)
    for (let j = i + 1; j < labels.length; j++)
      if (overlap(labels[i].r, labels[j].r))
        issues.push("text overlap: " + label(labels[i].el) + " and " + label(labels[j].el));

  // Strokes (connectors, borders, guides) that touch a label, sampled about every 1 px along the outline.
  const geoms = [...document.querySelectorAll("line, polyline, polygon, path, rect, circle, ellipse")]
    .filter(el => drawn(el) && !fullCanvas(el.getBoundingClientRect()));
  for (const el of geoms) {
    const s = getComputedStyle(el);
    if (!painted(s.stroke, s.strokeOpacity) || !(parseFloat(s.strokeWidth) > 0)) continue;
    const m = el.getScreenCTM();
    if (!m) continue;
    const scale = Math.hypot(m.a, m.b) || 1;
    const half = parseFloat(s.strokeWidth) * scale / 2;
    let len = 0;
    try { len = el.getTotalLength(); } catch (e) { continue; }
    const step = 1 / scale, n = Math.min(Math.ceil(len / step), 20000);
    for (let k = 0; k <= n; k++) {
      const p = el.getPointAtLength(Math.min(k * step, len)), q = new DOMPoint(p.x, p.y).matrixTransform(m);
      for (const lb of labels)
        if (q.x > lb.r.left - half + tol && q.x < lb.r.right + half - tol &&
            q.y > lb.r.top - half + tol && q.y < lb.r.bottom + half - tol)
          report("stroke touches text: " + name(el) + " and " + label(lb.el));
    }
  }

  // Images and compact shapes: nesting is fine, partial overlap is not.
  const images = [...document.querySelectorAll("image")].filter(drawn)
    .map(el => ({ el, r: el.getBoundingClientRect() }));
  for (const im of images)
    for (const lb of labels)
      if (overlap(im.r, lb.r)) report("text over image: " + label(lb.el) + " and " + name(im.el));
  const shapes = [...document.querySelectorAll("rect, circle, ellipse")]
    .filter(el => {
      const s = getComputedStyle(el);
      return drawn(el) && (painted(s.fill, s.fillOpacity) || painted(s.stroke, s.strokeOpacity));
    })
    .map(el => ({ el, r: el.getBoundingClientRect() }))
    .filter(sh => !fullCanvas(sh.r))
    .concat(images);
  for (const lb of labels) {
    const holder = holderOf(lb.r);
    for (const sh of shapes)
      if (sh.el !== (holder && holder.el) && sh.el.tagName !== "image" && partial(lb.r, sh.r))
        report("text partially covers shape: " + label(lb.el) + " and " + name(sh.el));
  }
  // Dots and markers below 8 px are skipped: they often sit on borders on purpose.
  const big = shapes.filter(sh => sh.r.width >= 8 && sh.r.height >= 8);
  for (let i = 0; i < big.length; i++)
    for (let j = i + 1; j < big.length; j++)
      if (partial(big[i].r, big[j].r)) report("shapes overlap: " + name(big[i].el) + " and " + name(big[j].el));

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
