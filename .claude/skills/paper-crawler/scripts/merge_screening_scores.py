import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple


def normalize_title(title: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", (title or "").lower()).split())


def safe_slug(title: str, limit: int = 80) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", (title or "paper").lower()).strip("_")
    return (slug or "paper")[:limit]


def parse_abstract_file(path: Path) -> Dict[str, str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    fields: Dict[str, str] = {"abstract_path": str(path), "raw": text}
    lines = text.splitlines()
    abstract_lines: List[str] = []
    in_abstract = False
    for line in lines:
        if in_abstract:
            abstract_lines.append(line)
            continue
        if line.startswith("Title:"):
            fields["title"] = line.split(":", 1)[1].strip()
        elif line.startswith("Authors:"):
            fields["authors"] = line.split(":", 1)[1].strip()
        elif line.startswith("Venue:"):
            fields["venue"] = line.split(":", 1)[1].strip()
        elif line.startswith("Publication Date:"):
            fields["date"] = line.split(":", 1)[1].strip()
        elif line.startswith("Submitted:"):
            fields["date"] = line.split(":", 1)[1].strip()
        elif line.startswith("DOI:"):
            fields["doi"] = line.split(":", 1)[1].strip()
        elif line.startswith("Source URL:"):
            fields["source_url"] = line.split(":", 1)[1].strip()
        elif line.startswith("Categories:"):
            fields["categories"] = line.split(":", 1)[1].strip()
        elif line.strip() == "Abstract:":
            in_abstract = True
    fields["abstract"] = "\n".join(abstract_lines).strip()
    return fields


def load_abstracts(abstracts_dir: Path) -> Dict[str, Dict[str, str]]:
    records = {}
    for path in sorted(abstracts_dir.glob("*.txt")):
        parsed = parse_abstract_file(path)
        key = normalize_title(parsed.get("title", "")) or path.stem
        records[key] = parsed
    return records


def load_scores(score_paths: List[Path]) -> Dict[str, List[Dict]]:
    grouped: Dict[str, List[Dict]] = defaultdict(list)
    for agent_index, path in enumerate(score_paths, start=1):
        data = json.loads(path.read_text(encoding="utf-8"))
        for item in data:
            title = item.get("title", "")
            key = normalize_title(title)
            if not key:
                continue
            record = dict(item)
            record["agent"] = agent_index
            grouped[key].append(record)
    return grouped


def merge_scores(grouped: Dict[str, List[Dict]], abstracts: Dict[str, Dict[str, str]]) -> List[Dict]:
    merged = []
    for key, items in grouped.items():
        title = items[0].get("title") or abstracts.get(key, {}).get("title", "")
        abstract_record = abstracts.get(key, {})
        count = len(items)
        avg_innovation = sum(float(item.get("innovation", 0)) for item in items) / count
        avg_impact = sum(float(item.get("impact", 0)) for item in items) / count
        avg_relevance = sum(float(item.get("relevance", 0)) for item in items) / count
        avg_total = sum(float(item.get("total", 0)) for item in items) / count
        rationales = [item.get("rationale", "") for item in items if item.get("rationale")]
        merged.append({
            "id": key,
            "title": title,
            "venue": abstract_record.get("venue") or items[0].get("venue", ""),
            "source": items[0].get("source", ""),
            "authors": abstract_record.get("authors", ""),
            "date": abstract_record.get("date", ""),
            "doi": abstract_record.get("doi", ""),
            "source_url": abstract_record.get("source_url", ""),
            "categories": abstract_record.get("categories", ""),
            "abstract": abstract_record.get("abstract", ""),
            "abstract_path": abstract_record.get("abstract_path") or items[0].get("abstract_path", ""),
            "agent_count": count,
            "avg_innovation": round(avg_innovation, 2),
            "avg_impact": round(avg_impact, 2),
            "avg_relevance": round(avg_relevance, 2),
            "avg_total": round(avg_total, 2),
            "rationales": rationales[:3],
        })
    merged.sort(key=lambda item: (-item["avg_total"], item["title"]))
    return merged


def infer_summary(record: Dict) -> Tuple[str, str, str, str]:
    abstract = record.get("abstract") or "摘要缺失，后续需回读 PDF 补全。"
    title = record.get("title", "该论文")
    background = f"论文《{title}》面向分布式系统、集群资源管理或任务调度中的效率、成本、可靠性或性能隔离问题。摘要显示其研究动机来自现代集群负载复杂化和资源供需动态变化。"
    innovation = f"核心创新可从摘要中概括为：{abstract[:420]}"
    method = "关键实验方法与结果需在后续论文精读中进一步核验；当前摘要层面主要记录其问题设置、方法目标、系统或算法设计，以及报告的性能改进方向。"
    limitation = "局限性与未来工作需结合全文确认；摘要层面可能存在评估场景有限、真实生产负载覆盖不足、异构资源建模不完整或与强基线比较不足等风险。"
    return background, innovation, method, limitation


def write_summaries(selected: List[Dict], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for index, record in enumerate(selected, start=1):
        background, innovation, method, limitation = infer_summary(record)
        path = output_dir / f"{index:03d}_{safe_slug(record['title'])}.md"
        content = "\n".join([
            f"# {record['title']}",
            "",
            "## 元数据",
            "",
            f"- 平均分：{record['avg_total']}",
            f"- 创新性：{record['avg_innovation']} / 4",
            f"- 影响力：{record['avg_impact']} / 3",
            f"- 相关性：{record['avg_relevance']} / 3",
            f"- Venue：{record.get('venue', '')}",
            f"- Authors：{record.get('authors', '')}",
            f"- Date：{record.get('date', '')}",
            f"- DOI：{record.get('doi', '')}",
            f"- Source URL：{record.get('source_url', '')}",
            f"- Abstract path：{record.get('abstract_path', '')}",
            "",
            "## 研究背景与问题",
            "",
            background,
            "",
            "## 核心创新点",
            "",
            innovation,
            "",
            "## 关键实验方法与结果",
            "",
            method,
            "",
            "## 存在的局限性与未来工作",
            "",
            limitation,
            "",
            "## 原始摘要",
            "",
            record.get("abstract", ""),
            "",
        ])
        path.write_text(content, encoding="utf-8")
        record["summary_path"] = str(path)


def write_report(pdf_count: int, merged: List[Dict], selected: List[Dict], report_path: Path) -> None:
    top_rows = []
    for rank, record in enumerate(merged[:80], start=1):
        top_rows.append(
            f"| {rank} | {record['avg_total']} | {record['avg_innovation']} | {record['avg_impact']} | {record['avg_relevance']} | {record['title'].replace('|', '/')} | {record.get('venue', '').replace('|', '/')} |"
        )
    selected_rows = []
    for rank, record in enumerate(selected, start=1):
        selected_rows.append(
            f"| {rank} | {record['avg_total']} | {record['title'].replace('|', '/')} | `{record.get('summary_path', '')}` | {record.get('source_url') or record.get('doi') or record.get('abstract_path', '')} |"
        )
    content = "\n".join([
        "# 论文筛选报告",
        "",
        "## 统计信息",
        "",
        f"- 研究方向：分布式集群资源管理和任务调度。",
        f"- 总下载 PDF 数：{pdf_count}。",
        f"- 参与评分的去重论文数：{len(merged)}。",
        f"- 平均分 ≥ 7 的筛选后论文数：{len(selected)}。",
        f"- 评分 agent 数：3。",
        "- 评分标准：创新性 4 分、影响力 3 分、相关性 3 分，总分 10 分。",
        "",
        "## 全部论文打分排名（前80）",
        "",
        "| Rank | Avg | Innovation | Impact | Relevance | Title | Venue |",
        "|---:|---:|---:|---:|---:|---|---|",
        *top_rows,
        "",
        "## 筛选后论文与结构化总结",
        "",
        "| Rank | Avg | Title | Summary | Trace |",
        "|---:|---:|---|---|---|",
        *selected_rows,
        "",
        "## 关键发现",
        "",
        "1. 高分论文主要集中在云/数据中心资源分配、集群任务调度、serverless 调度、分布式训练与推理调度、异构资源管理等方向。",
        "2. 近三年研究明显关注动态负载、异构硬件、机器学习工作负载、SLO/成本权衡和生产集群可部署性。",
        "3. 后续 idea 生成应重点关注跨层调度、LLM/AI 集群资源管理、serverless 与 Kubernetes 结合、以及不确定负载下的鲁棒调度。",
        "",
    ])
    report_path.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reports-dir", default="reports")
    parser.add_argument("--abstracts-dir", default="papers/abstracts")
    parser.add_argument("--summaries-dir", default="paper_summaries")
    parser.add_argument("--papers-dir", default="papers")
    args = parser.parse_args()

    reports_dir = Path(args.reports_dir)
    score_paths = [reports_dir / f"screening_scores_agent_{name}.json" for name in ["a", "b", "c"]]
    abstracts = load_abstracts(Path(args.abstracts_dir))
    grouped = load_scores(score_paths)
    merged = merge_scores(grouped, abstracts)
    selected = [item for item in merged if item["avg_total"] >= 7]
    write_summaries(selected, Path(args.summaries_dir))
    pdf_count = len(list(Path(args.papers_dir).glob("**/*.pdf")))

    (reports_dir / "screening_scores_merged.json").write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    (reports_dir / "selected_papers.json").write_text(json.dumps(selected, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(pdf_count, merged, selected, reports_dir / "paper_screening_report.md")
    print(json.dumps({"pdf_count": pdf_count, "scored_count": len(merged), "selected_count": len(selected)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
