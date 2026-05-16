<div align="center">

# Paper Agent

### _"如果一篇论文，他是遵守学术规范的、能够中稿的、满足毕业要求的，那么他就是 best paper！"_

学术研究全流程自动化助手 — 端到端覆盖论文收集、Idea 生成、实验执行、论文撰写、模拟审稿以及批阅后修改。

</div>

## 仓库结构

- `SPEC.md`：执行规范与工作流程说明（主规范）。
- `.claude/skills/`：按功能划分的 skill 目录，每个 skill 带有 `SKILL.md` 说明与可执行脚本。
- `.claude/rules/`: 一些写作规则。
- `templates/`：论文模板。

## 快速开始

1. 克隆项目

```bash
git clone https://github.com/Guo-Chenxu/paper-agent.git
cd paper-agent
```

2. 配置环境

使用 conda 隔离 agent 执行环境

```bash
conda create -n paper-agent python=3.10 -y
conda activate paper-agent
pip install -r requirements.txt
```

安装 [latex](https://www.latex-project.org/get/) 保证后期可以编译 latex 文件

1. 配置环境变量

```bash
cp .env.template .env
```

在 `.env` 中填写必要的环境变量以保证能够正常使用各个 skill

4. 运行

打开 claude code，输入 prompt：

```txt
根据 @SPEC.md 中的流程寻找 idea，撰写论文并审阅和修改，所有代码操作都在 paper-agent 这个 conda 环境下执行
```

5. 修改

```txt
/paper-annotation-reviser 根据批注文件 @paper-pizhu.pdf 修改原论文 @paper/paper.tex
```

## 输出位置

- `./papers/`：爬取的论文与摘要、元数据
- `./paper/`：LaTeX 源、生成的 PDF、`figures/` 存放图片 PDF
- `./reports/`：各阶段生成的报告（筛选报告、实验报告、模拟审稿等）
- ...

## 一些经验

1. 截止至2026年4月12日，实测推荐使用 claude code + claude opus 4.6效果最佳，可以使用国内中转站 [bytecatcode](https://www.bytecatcode.org/register?aff=cXYn)。尝试过 codex + gpt5.5，基本不可用（太绕了，折腾一天不停地fallback，一篇论文都没下下来）。

## 开发与贡献

- 新增或调整技能请在 `./claude/skills/<skill>/` 下维护 `SKILL.md`、`scripts/` 与必要的测试用例。
- 提交前请在本地 conda 环境中运行相关脚本并核验输出结果。

## 致谢

感谢以下项目的贡献：

- [Master-cai/Research-Paper-Writing-Skills](https://github.com/Master-cai/Research-Paper-Writing-Skills)
