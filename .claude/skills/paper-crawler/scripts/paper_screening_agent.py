#!/usr/bin/env python3
"""
Multi-agent paper screening for Phase 1.
3 independent agents score each paper on innovation, impact, relevance.
Papers with avg score >= 7 pass to next stage.
"""

import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional
from urllib import error, request

# API config from .env
def load_env(env_file=".env"):
    env = {}
    p = Path(env_file)
    if p.exists():
        for line in p.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env

ENV = load_env()
API_KEY = ENV.get("PAPER_CRAWLER_API_KEY") or os.getenv("PAPER_CRAWLER_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
BASE_URL = ENV.get("PAPER_CRAWLER_BASE_URL") or os.getenv("PAPER_CRAWLER_BASE_URL") or "https://api.anthropic.com"
MODEL = ENV.get("PAPER_CRAWLER_MODEL") or os.getenv("PAPER_CRAWLER_MODEL") or "claude-haiku-4-5-20251001"


def build_endpoint(base_url: str) -> str:
    normalized = base_url.rstrip("/")
    if normalized.endswith("/v1/messages"):
        return normalized
    if normalized.endswith("/v1"):
        return f"{normalized}/messages"
    return f"{normalized}/v1/messages"


def call_api(prompt: str, system: str, max_tokens: int = 512) -> str:
    endpoint = build_endpoint(BASE_URL)
    payload = {
        "model": MODEL,
        "max_tokens": max_tokens,
        "temperature": 0.3,
        "system": system,
        "messages": [{"role": "user", "content": prompt}],
    }
    req = request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "content-type": "application/json",
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    for attempt in range(3):
        try:
            with request.urlopen(req, timeout=60) as resp:
                raw = resp.read().decode("utf-8")
            data = json.loads(raw)
            for item in data.get("content", []):
                if item.get("type") == "text":
                    return item["text"].strip()
            return ""
        except error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            print(f"[WARN] API HTTP {e.code}: {body[:200]}", file=sys.stderr)
            if attempt < 2:
                time.sleep(5 * (attempt + 1))
        except Exception as e:
            print(f"[WARN] API error: {e}", file=sys.stderr)
            if attempt < 2:
                time.sleep(5 * (attempt + 1))
    return ""


AGENT_SYSTEMS = [
    """You are Agent-1, a senior systems researcher specializing in distributed systems and resource scheduling.
Score papers strictly on academic merit. Focus on technical novelty and systems contribution.
Always respond with ONLY a JSON object in this exact format:
{"innovation": <1-4>, "impact": <1-3>, "relevance": <1-3>, "total": <3-10>, "reason": "<one sentence>"}""",

    """You are Agent-2, a distributed systems professor evaluating papers for top venues.
Be critical and objective. Focus on practical impact and experimental rigor.
Always respond with ONLY a JSON object in this exact format:
{"innovation": <1-4>, "impact": <1-3>, "relevance": <1-3>, "total": <3-10>, "reason": "<one sentence>"}""",

    """You are Agent-3, an industry researcher in cloud computing and resource management.
Evaluate papers from both academic and practical perspectives.
Always respond with ONLY a JSON object in this exact format:
{"innovation": <1-4>, "impact": <1-3>, "relevance": <1-3>, "total": <3-10>, "reason": "<one sentence>"}""",
]


def score_paper_single_agent(paper: Dict, agent_idx: int) -> Dict:
    title = paper.get("title", "")
    abstract = paper.get("abstract", "")[:1500]
    venue = paper.get("venue", "arXiv")
    year = paper.get("year", "")

    prompt = f"""Score this paper for a distributed systems & resource scheduling research survey.

Title: {title}
Venue: {venue} ({year})
Abstract: {abstract}

Scoring criteria:
- innovation (1-4): novelty of method/problem/finding
- impact (1-3): venue prestige, potential citations, author team
- relevance (1-3): fit with distributed systems & resource scheduling

Respond with ONLY the JSON object."""

    response = call_api(prompt, AGENT_SYSTEMS[agent_idx])

    # Parse JSON from response
    try:
        # Find JSON in response
        start = response.find("{")
        end = response.rfind("}") + 1
        if start >= 0 and end > start:
            scores = json.loads(response[start:end])
            return {
                "innovation": min(4, max(1, int(scores.get("innovation", 2)))),
                "impact": min(3, max(1, int(scores.get("impact", 2)))),
                "relevance": min(3, max(1, int(scores.get("relevance", 2)))),
                "total": min(10, max(1, int(scores.get("total", 5)))),
                "reason": scores.get("reason", ""),
                "agent": agent_idx + 1,
            }
    except Exception as e:
        print(f"[WARN] Parse error for agent {agent_idx+1}: {e}, response: {response[:100]}", file=sys.stderr)

    # Fallback: compute total from parts
    return {"innovation": 2, "impact": 2, "relevance": 2, "total": 6, "reason": "parse_error", "agent": agent_idx + 1}


def score_paper(paper: Dict) -> Dict:
    """Score paper with 3 agents in parallel, return averaged result."""
    scores = []
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = {pool.submit(score_paper_single_agent, paper, i): i for i in range(3)}
        for future in as_completed(futures):
            try:
                scores.append(future.result())
            except Exception as e:
                print(f"[WARN] Agent scoring failed: {e}", file=sys.stderr)

    if not scores:
        return {"avg_total": 0, "scores": [], "passed": False}

    avg_innovation = sum(s["innovation"] for s in scores) / len(scores)
    avg_impact = sum(s["impact"] for s in scores) / len(scores)
    avg_relevance = sum(s["relevance"] for s in scores) / len(scores)
    avg_total = sum(s["total"] for s in scores) / len(scores)

    # Check if agents disagree too much (>3 points diff) - add arbiter
    totals = [s["total"] for s in scores]
    if len(totals) >= 2 and (max(totals) - min(totals)) > 3:
        print(f"[INFO] High variance ({max(totals)-min(totals)}) for '{paper.get('title','')[:50]}', adding arbiter...")
        arbiter = score_paper_single_agent(paper, 0)  # reuse agent 1 as arbiter
        scores.append(arbiter)
        avg_total = sum(s["total"] for s in scores) / len(scores)

    return {
        "avg_innovation": round(avg_innovation, 2),
        "avg_impact": round(avg_impact, 2),
        "avg_relevance": round(avg_relevance, 2),
        "avg_total": round(avg_total, 2),
        "scores": scores,
        "passed": avg_total >= 7.0,
    }


def generate_summary(paper: Dict) -> str:
    """Generate structured summary for a high-scoring paper."""
    title = paper.get("title", "")
    abstract = paper.get("abstract", "")[:2000]
    venue = paper.get("venue", "")
    year = paper.get("year", "")

    prompt = f"""Write a structured research summary for this paper.

Title: {title}
Venue: {venue} ({year})
Abstract: {abstract}

Output a structured summary with these exact sections:
## Research Background & Problem
[2-3 sentences]

## Core Innovations
[2-3 bullet points]

## Key Methods & Results
[2-3 sentences]

## Limitations & Future Work
[1-2 sentences]"""

    return call_api(prompt,
        "You are an expert academic researcher. Write concise, accurate paper summaries.",
        max_tokens=600)


def load_papers_from_abstracts(abstracts_dir: str) -> List[Dict]:
    """Load papers from abstract text files."""
    papers = []
    for txt_file in sorted(Path(abstracts_dir).glob("*.txt")):
        content = txt_file.read_text(encoding="utf-8")
        paper = {"arxiv_id": txt_file.stem}
        for line in content.split("\n"):
            if line.startswith("Title: "):
                paper["title"] = line[7:].strip()
            elif line.startswith("Authors: "):
                paper["authors"] = [a.strip() for a in line[9:].split(",")]
            elif line.startswith("Venue: "):
                paper["venue"] = line[7:].strip()
            elif line.startswith("Date: "):
                paper["publication_date"] = line[6:].strip()
                try:
                    paper["year"] = int(line[6:10])
                except:
                    pass
            elif line.startswith("ArXiv: "):
                paper["source_url"] = line[7:].strip()
        # Extract abstract
        if "Abstract:\n" in content:
            paper["abstract"] = content.split("Abstract:\n", 1)[1].strip()
        if paper.get("title"):
            papers.append(paper)
    return papers


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--abstracts-dir", default="./papers/abstracts")
    parser.add_argument("--metadata-dir", default="./papers/metadata")
    parser.add_argument("--summaries-dir", default="./paper_summaries")
    parser.add_argument("--reports-dir", default="./reports")
    parser.add_argument("--workers", type=int, default=5)
    parser.add_argument("--threshold", type=float, default=7.0)
    args = parser.parse_args()

    Path(args.summaries_dir).mkdir(parents=True, exist_ok=True)
    Path(args.reports_dir).mkdir(parents=True, exist_ok=True)

    # Load papers
    print("[Phase 1] Loading papers from abstracts...")
    papers = load_papers_from_abstracts(args.abstracts_dir)

    # Also try loading from metadata JSON
    metadata_files = sorted(Path(args.metadata_dir).glob("papers_*.json"))
    if metadata_files:
        with open(metadata_files[-1]) as f:
            meta_papers = json.load(f)
        # Merge: use metadata as primary, fill missing abstracts from txt files
        meta_by_id = {p.get("arxiv_id", ""): p for p in meta_papers if p.get("arxiv_id")}
        txt_by_id = {p.get("arxiv_id", ""): p for p in papers}
        merged = []
        for arxiv_id, mp in meta_by_id.items():
            if not mp.get("abstract") and arxiv_id in txt_by_id:
                mp["abstract"] = txt_by_id[arxiv_id].get("abstract", "")
            merged.append(mp)
        # Add any txt-only papers
        for arxiv_id, tp in txt_by_id.items():
            if arxiv_id not in meta_by_id:
                merged.append(tp)
        papers = merged

    print(f"[Phase 1] Loaded {len(papers)} papers for screening")

    # Score papers with multi-agent in parallel
    scored_papers = []
    print(f"[Phase 1] Scoring {len(papers)} papers with 3 agents each (workers={args.workers})...")

    def score_with_progress(paper_idx_tuple):
        idx, paper = paper_idx_tuple
        result = score_paper(paper)
        paper["screening"] = result
        if (idx + 1) % 10 == 0:
            print(f"  Scored {idx+1}/{len(papers)}")
        return paper

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = list(pool.map(score_with_progress, enumerate(papers)))
        scored_papers = futures

    # Filter passed papers
    passed = [p for p in scored_papers if p.get("screening", {}).get("passed", False)]
    passed.sort(key=lambda p: p.get("screening", {}).get("avg_total", 0), reverse=True)

    print(f"[Phase 1] Passed (avg >= {args.threshold}): {len(passed)}/{len(scored_papers)}")

    # Generate structured summaries for passed papers
    print(f"[Phase 1] Generating summaries for {len(passed)} passed papers...")
    for i, paper in enumerate(passed):
        arxiv_id = paper.get("arxiv_id", f"paper_{i}").replace("/", "_").replace(".", "_")
        summary_path = Path(args.summaries_dir) / f"{arxiv_id}_summary.md"
        if summary_path.exists():
            paper["summary_path"] = str(summary_path)
            continue
        summary = generate_summary(paper)
        if summary:
            full_summary = f"# {paper.get('title', 'Unknown')}\n\n"
            full_summary += f"**Venue**: {paper.get('venue', 'arXiv')} | **Year**: {paper.get('year', '')} | **Score**: {paper.get('screening', {}).get('avg_total', 0)}\n\n"
            full_summary += f"**ArXiv**: {paper.get('source_url', '')}\n\n"
            full_summary += summary
            summary_path.write_text(full_summary, encoding="utf-8")
            paper["summary_path"] = str(summary_path)
        if (i + 1) % 5 == 0:
            print(f"  Summarized {i+1}/{len(passed)}")
        time.sleep(0.5)

    # Save scored metadata
    import datetime
    ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    scored_path = Path(args.metadata_dir) / f"scored_papers_{ts}.json"
    with open(scored_path, "w", encoding="utf-8") as f:
        json.dump(scored_papers, f, ensure_ascii=False, indent=2)

    passed_path = Path(args.metadata_dir) / f"passed_papers_{ts}.json"
    with open(passed_path, "w", encoding="utf-8") as f:
        json.dump(passed, f, ensure_ascii=False, indent=2)

    # Generate screening report
    report_lines = [
        "# 论文筛选报告 (Paper Screening Report)",
        "",
        f"**生成时间**: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
        f"**研究领域**: 分布式系统与资源调度",
        f"**时间范围**: 近3年 (2023-2026)",
        "",
        "## 统计摘要",
        "",
        f"- 总下载论文数: **{len(scored_papers)}**",
        f"- 筛选通过论文数 (avg≥{args.threshold}): **{len(passed)}**",
        f"- 筛选通过率: **{len(passed)/max(1,len(scored_papers))*100:.1f}%**",
        "",
        "## 场馆分布 (Venue Distribution)",
        "",
    ]

    venue_counts = {}
    for p in scored_papers:
        v = p.get("venue", "arXiv")
        venue_counts[v] = venue_counts.get(v, 0) + 1
    for v, c in sorted(venue_counts.items(), key=lambda x: -x[1]):
        report_lines.append(f"- {v}: {c}")

    report_lines += [
        "",
        "## Top 30 论文排名 (by avg score)",
        "",
        "| Rank | Score | Title | Venue | Year |",
        "|------|-------|-------|-------|------|",
    ]

    for i, p in enumerate(passed[:30]):
        score = p.get("screening", {}).get("avg_total", 0)
        title = p.get("title", "")[:70]
        venue = p.get("venue", "")
        year = p.get("year", "")
        report_lines.append(f"| {i+1} | {score:.1f} | {title} | {venue} | {year} |")

    report_lines += [
        "",
        "## 所有通过论文的结构化总结",
        "",
    ]

    for i, p in enumerate(passed):
        score = p.get("screening", {}).get("avg_total", 0)
        title = p.get("title", "Unknown")
        venue = p.get("venue", "arXiv")
        year = p.get("year", "")
        url = p.get("source_url", "")
        reasons = [s.get("reason", "") for s in p.get("screening", {}).get("scores", []) if s.get("reason")]

        report_lines += [
            f"### {i+1}. {title}",
            f"**Score**: {score:.1f} | **Venue**: {venue} | **Year**: {year}",
            f"**URL**: {url}",
            "",
        ]
        if reasons:
            report_lines.append(f"**Agent评价**: {' | '.join(reasons[:2])}")
            report_lines.append("")

        summary_path = p.get("summary_path")
        if summary_path and Path(summary_path).exists():
            summary_content = Path(summary_path).read_text(encoding="utf-8")
            # Extract just the structured part
            if "## Research Background" in summary_content:
                report_lines.append(summary_content.split("# ")[0] if "# " in summary_content else summary_content)
        report_lines.append("---")
        report_lines.append("")

    report_path = Path(args.reports_dir) / "paper_screening_report.md"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    print(f"[Phase 1] Screening report saved to {report_path}")
    print(f"[Phase 1] Total: {len(scored_papers)}, Passed: {len(passed)}")
    print(f"[Phase 1] Scored metadata: {scored_path}")
    print(f"[Phase 1] Passed metadata: {passed_path}")

    return str(passed_path)


if __name__ == "__main__":
    main()
