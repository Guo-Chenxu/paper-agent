---
name: research-idea-generator
description: "Use when generating research ideas from paper summaries. Analyzes research gaps, generates ideas via multi-agent brainstorming, evaluates and ranks ideas, performs adversarial review, and produces detailed research proposals."
argument-hint: "Provide paper summaries directory or research domain context"
user-invocable: true
---

# Research Idea Generator

## Skill Goal

Systematic research idea generation and evaluation workflow:

1. Analyze paper summaries to build research knowledge graph
2. Identify research gaps and opportunities
3. Multi-agent parallel idea generation (3+ agents, 5+ ideas each)
4. Idea evaluation and ranking by innovation, feasibility, and impact
5. Adversarial review and refinement of top ideas
6. Detailed research proposal generation

## When To Use

- Have completed paper collection and screening (e.g., via paper-crawler skill)
- Need to generate novel research ideas from literature review
- Want systematic gap analysis and idea evaluation
- Require detailed research proposals with background, hypothesis, and methodology

## Environment

Run from the repository root with active Python interpreter.

Required packages:

```bash
python -m pip install requests tqdm
```

## Scripts

- Export idea generation prompt pack: `./scripts/export_idea_prompts.py`
- Build final research ideas report: `./scripts/build_research_ideas_report.py`

The `export_idea_prompts.py` script is domain-agnostic and accepts:
- `--research-domain`: Your research field (e.g., "machine learning", "computer vision", "natural language processing")
- `--summaries-dir`: Directory with paper summaries
- `--num-agents`: Number of idea generation agents (default: 3)
- `--ideas-per-agent`: Ideas per agent (default: 5)
- `--experiment-constraints`: Optional constraints (e.g., "Single server only")

## References

- Idea generation workflow and prompts: `./references/idea-generation.md`

## Workflow

### Step 1: Load Paper Summaries

Load structured paper summaries from previous screening workflow:

```bash
# Summaries should be in ./paper_summaries/ directory
ls ./paper_summaries/*.md
```

### Step 2: Build Research Knowledge Graph

Analyze all paper summaries to construct knowledge graph covering:

- **Solved problems**: What has been thoroughly addressed
- **Open problems**: What remains unsolved or partially solved
- **Common limitations**: Shared weaknesses across existing methods
- **Cross-domain opportunities**: Potential for technique transfer
- **Emerging trends**: Recent breakthroughs applicable to the domain

Generate `./reports/research_knowledge_graph.md` with structured analysis.

### Step 3: Multi-Agent Idea Generation

Spawn 3+ independent "Idea Generation Agents" in parallel. Each agent:

- Reads all paper summaries and knowledge graph
- Generates **at least 5 distinct research ideas**
- Uses different creative perspectives (e.g., problem-driven, method-driven, application-driven)

**Agent Personas:**

- **Agent 1 - Problem Explorer**: Focus on unsolved problems and pain points
- **Agent 2 - Method Innovator**: Focus on novel techniques and algorithmic improvements
- **Agent 3 - Application Architect**: Focus on practical applications and system design

Each idea should include:
- Brief title (1 line)
- Core innovation (2-3 sentences)
- Research gap it addresses
- Preliminary approach

Save all raw ideas to `./reports/raw_research_ideas.md`.

### Step 4: Idea Evaluation

Spawn 1 "Idea Evaluation Agent" to score all generated ideas on:

- **Innovation** (1-4): Novelty, uniqueness, unexplored territory
- **Feasibility** (1-3): Implementation difficulty, resource requirements, time cost
- **Impact** (1-3): Potential contribution, publication prospects, real-world value
- **Total** (3-10): Sum of above scores

Generate evaluation matrix in `./reports/idea_evaluation_scores.json`:

```json
{
  "ideas": [
    {
      "id": 1,
      "title": "...",
      "innovation": 4,
      "feasibility": 2,
      "impact": 3,
      "total": 9,
      "reason": "..."
    }
  ]
}
```

### Step 5: Select and Refine Top Ideas

Filter ideas with **average score >= 8.0** and select top 3.

For each top idea, perform deep refinement:

**Optional**: Use `superpowers:brainstorming` skill to explore different angles and refine the idea before detailed elaboration.

1. **Expand background story**: Why this problem matters, historical context
2. **Formulate research question**: Clear, specific, answerable question
3. **Define hypothesis**: Testable claim about expected outcomes
4. **Detail innovation**: What makes this different from prior work
5. **Outline technical approach**: High-level methodology and key steps
6. **Sketch experimental plan**: Datasets, baselines, metrics, validation strategy

### Step 6: Adversarial Review

For each refined idea, use `reviewer-attack` skill to simulate critical review:

- Spawn 3 reviewer agents (strict, constructive, newcomer)
- Each reviewer attacks the idea from their perspective
- Identify fatal flaws, unsupported claims, missing baselines
- Generate rebuttal and revise idea accordingly

Save attack trace to `./reports/idea_reviewer_attack_trace.md`.

### Step 7: Generate Final Report

Create comprehensive report in `./reports/research_directions_and_ideas.md`:

**Report Structure:**

```markdown
# Research Directions and Ideas

## Research Domain Overview
[Brief summary of the field and current state]

## Knowledge Graph Summary
[Key findings from gap analysis]

## Research Gaps and Opportunities
- Unsolved problems
- Common limitations
- Cross-domain opportunities
- Emerging trends

## All Generated Ideas
[Table with all ideas and scores]

## Top 3 Research Proposals

### Idea 1: [Title]

#### Background and Motivation
[2-3 paragraphs]

#### Research Question
[Clear, specific question]

#### Hypothesis
[Testable claim]

#### Core Innovation
[What's new and why it matters]

#### Technical Approach
[High-level methodology]

#### Experimental Plan
- Datasets
- Baselines
- Metrics
- Validation strategy

#### Adversarial Review Summary
[Key concerns raised and how addressed]

[Repeat for Ideas 2 and 3]
```

## Output Requirements

All outputs saved to project working directory:

- Knowledge graph: `./reports/research_knowledge_graph.md`
- Raw ideas: `./reports/raw_research_ideas.md`
- Evaluation scores: `./reports/idea_evaluation_scores.json`
- Reviewer attack trace: `./reports/idea_reviewer_attack_trace.md`
- Final report: `./reports/research_directions_and_ideas.md`

## Quality Checks

Before completing, verify:

1. At least 15 raw ideas generated (3 agents × 5 ideas minimum)
2. All ideas have evaluation scores
3. Top 3 ideas have detailed proposals with all required sections
4. Adversarial review performed on all top ideas
5. Final report is comprehensive and well-structured
6. All intermediate artifacts preserved for traceability

## Best Practices

- **Preserve reasoning**: Keep all intermediate outputs (knowledge graph, raw ideas, scores, attack traces)
- **Independent agents**: Ensure idea generation agents work independently without cross-contamination
- **Concrete proposals**: Top ideas should be detailed enough to start implementation
- **Honest evaluation**: Don't inflate scores; be critical and realistic
- **Iterative refinement**: Use reviewer feedback to genuinely improve ideas, not just defend them
