import json
from pathlib import Path


def load_json(path: str):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def idea_table(evaluations):
    rows = ["| Rank | Score | Innovation | Feasibility | Impact | Source | Title |", "|---:|---:|---:|---:|---:|---:|---|"]
    ranked = sorted(evaluations, key=lambda item: (-item["total_score"], item["title"]))
    for index, item in enumerate(ranked, start=1):
        title = item["title"].replace("|", "/")
        rows.append(f"| {index} | {item['total_score']} | {item['innovation_score']} | {item['feasibility_score']} | {item['impact_score']} | {item['source_agent']} | {title} |")
    return "\n".join(rows)


def top3_section(evaluation, attack):
    sections = []
    for item in evaluation["top3"]:
        sections.append("\n".join([
            f"### Top {item['rank']}: {item['title']}",
            "",
            f"- 来源 agent：{item['source_agent']}",
            f"- 总分：{item['total_score']}",
            f"- 入选原因：{item['why_selected']}",
            f"- 必要验证：{item['required_validation']}",
        ]))
    sections.append("## Reviewer-Attack 压测与修订结果")
    sections.append(attack)
    return "\n\n".join(sections)


def main():
    evaluation = load_json("reports/idea_evaluation.json")
    attack = Path("reports/top3_idea_reviewer_attack.md").read_text(encoding="utf-8")
    report = "\n".join([
        "# 研究方向与 Idea 报告",
        "",
        "## 研究领域现状分析与空白总结",
        "",
        "阶段1共下载 232 篇 PDF，三位筛选 agent 对 311 篇去重论文的标题与摘要进行独立评分，筛选出 10 篇平均分 ≥ 7 的高相关论文。高分论文集中在云/数据中心资源分配、集群任务调度、serverless 调度、分布式训练与推理调度、异构资源管理等方向。",
        "",
        "当前研究显示四类明显空白。第一，生产集群中的负载突发、预测误差和资源异构会共同放大调度器的错误决策，但许多方法默认预测可信或只在静态负载上评估。第二，GPU/AI 多租户混部越来越常见，但干扰建模、负载迁移和公平性往往被分开处理。第三，gang scheduling 和多资源队列仍受到碎片化影响，现有 backfilling 或 reservation 方法对弹性与启动就绪度的联合建模不足。第四，许多新方法依赖大型真实集群验证，缺少可由公开 trace 和单机仿真复现的实验闭环。",
        "",
        "## 全部生成 Idea 与打分",
        "",
        idea_table(evaluation["evaluations"]),
        "",
        "## Top 3 Idea 详细说明",
        "",
        top3_section(evaluation, attack),
        "",
        "## 阶段2结论",
        "",
        "TraceSplit 的复现链条最清晰，适合作为稳健实验主线；InterfereSched 的系统问题最重要，但必须通过敏感性分析处理外推风险；Elastic Shadow Gang Scheduling 的调度问题最经典，但需要突出 shadow reservation 的理论或机制差异，避免被视为 backfilling 增量。建议人工审计阶段优先比较这三者的目标会议定位、实验资源需求和期望贡献强度。",
        "",
    ])
    Path("reports/research_directions_and_ideas.md").write_text(report, encoding="utf-8")
    print("reports/research_directions_and_ideas.md")


if __name__ == "__main__":
    main()
