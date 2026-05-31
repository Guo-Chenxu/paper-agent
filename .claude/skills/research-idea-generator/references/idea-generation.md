# Research Idea Generation Reference

Use this reference after paper summaries are available from the paper-crawler skill. Idea generation runs through local Claude Code subagents, not through external API scripts.

## Workflow

### Step 1: Export Prompt Pack

Run the prompt export script from the repository root:

```bash
python .claude/skills/research-idea-generator/scripts/export_idea_prompts.py \
  --research-domain "your research field" \
  --summaries-dir ./paper_summaries \
  --num-agents 3 \
  --ideas-per-agent 5 \
  --output ./reports/idea_generation_prompt_pack.md
```

Optional parameters:
- `--max-papers N`: Limit to N most relevant papers
- `--experiment-constraints "text"`: Specify environment constraints

### Step 2: Build Knowledge Graph

Read all paper summaries and analyze the research landscape:

1. **Well-solved problems**: What has been thoroughly addressed
2. **Open research gaps**: What remains unsolved or partially solved
3. **Common limitations**: Shared weaknesses across existing methods
4. **Cross-domain opportunities**: Potential for technique transfer
5. **Emerging trends**: Recent breakthroughs applicable to this domain

Save to `./reports/research_knowledge_graph.md`.

### Step 3: Launch Parallel Subagents

Launch 3 independent local subagents in parallel. Each subagent receives:
- The paper summaries context
- The knowledge graph
- One agent persona prompt from the prompt pack

Agent personas (generic):
- **Agent 1 - Problem-Driven Researcher**: Focus on unsolved problems and pain points
- **Agent 2 - Method-Driven Researcher**: Focus on novel techniques and algorithmic improvements
- **Agent 3 - Application-Driven Researcher**: Focus on practical applications and system design

Each agent generates exactly 5 ideas independently.

### Step 4: Collect Raw Ideas

Merge all generated ideas (3 agents × 5 ideas = 15 total) in the main session.

Save to `./reports/raw_research_ideas.md`.

### Step 5: Evaluate and Rank

Evaluate all ideas using the rubric:

- **Innovation (1-4)**: Novelty of problem, mechanism, algorithm, or system design
- **Feasibility (1-3)**: Implementation difficulty, resource requirements, time cost
- **Impact (1-3)**: Potential contribution, publication prospects, real-world value
- **Total (3-10)**: Sum of above scores

Save evaluation results to `./reports/idea_evaluation_scores.json`:

```json
{
  "ideas": [
    {
      "id": 1,
      "agent": "Agent 1",
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

### Step 6: Select Top Ideas

Filter ideas with **total >= 8.0** as top candidates.

### Step 7: Elaborate Top Ideas

For each top idea, perform deep refinement:

**Optional**: Use `superpowers:brainstorming` skill to explore different angles and refine the idea before detailed elaboration.

1. **Background story**: Why this problem matters, historical context (2-3 paragraphs)
2. **Research question**: Clear, specific, answerable question
3. **Hypothesis**: Testable claim about expected outcomes
4. **Innovation details**: What makes this different from prior work (2-3 paragraphs)
5. **Technical approach**: High-level methodology and key steps
6. **Experimental plan**:
   - Datasets to use
   - Baseline methods to compare against
   - Evaluation metrics
   - Validation strategy

### Step 8: Adversarial Review

Use the `reviewer-attack` skill to simulate critical review of each top idea:

- Spawn 3 reviewer agents (strict, constructive, newcomer)
- Each reviewer attacks the idea from their perspective
- Identify fatal flaws, unsupported claims, missing baselines
- Generate rebuttal and revise idea accordingly

Save to `./reports/idea_reviewer_attack_trace.md`.

### Step 9: Build Final Report

Run the report builder:

```bash
python .claude/skills/research-idea-generator/scripts/build_research_ideas_report.py \
  --knowledge-graph ./reports/research_knowledge_graph.md \
  --evaluations ./reports/idea_evaluation_scores.json \
  --reviewer-attack ./reports/idea_reviewer_attack_trace.md \
  --output ./reports/research_directions_and_ideas.md
```

## Required Idea Fields

Each idea should include:

- **title**: Brief, descriptive (1 line)
- **problem**: What specific problem does this address?
- **gap**: What research gap does this fill?
- **innovation**: What makes this different from prior work?
- **approach**: High-level methodology (2-3 sentences)
- **experiment**: How would you validate this?
- **baselines**: What existing methods to compare against?
- **expected_result**: What outcomes do you expect?
- **risks**: What could go wrong?

## Evaluation Guidelines

**Innovation (1-4):**
- 1: Incremental improvement
- 2: Solid contribution with some novelty
- 3: Significant novelty in approach or problem
- 4: Groundbreaking, unexplored territory

**Feasibility (1-3):**
- 1: Very difficult, requires extensive resources
- 2: Moderate difficulty, standard resources
- 3: Straightforward, readily implementable

**Impact (1-3):**
- 1: Limited scope, niche contribution
- 2: Solid contribution, publishable at good venues
- 3: High impact, potential for top-tier publication

**Threshold**: Only ideas with **total >= 8.0** should be selected for elaboration.

## Final Report Structure

The final `reports/research_directions_and_ideas.md` should contain:

1. **Research Domain Overview and Gap Analysis**
   - Screening statistics (if available)
   - Knowledge graph summary

2. **All Generated Ideas (Ranked by Score)**
   - Table with all ideas and scores

3. **Top Ideas - Detailed Proposals**
   - Full elaboration for each top idea (score >= 8.0)

4. **Adversarial Review and Refinement**
   - Reviewer attack trace and revisions

## Quality Checks

Before completing, verify:

1. All ideas have been generated (num_agents × ideas_per_agent)
2. All ideas have evaluation scores
3. Top ideas (score >= 8.0) have detailed elaborations
4. All ideas are grounded in paper context (cite specific papers)
5. All ideas are feasible within stated constraints
6. Adversarial review performed on all top ideas
7. All intermediate artifacts preserved for traceability

## Best Practices

- **Independent agents**: Ensure agents work independently without cross-contamination
- **Concrete proposals**: Top ideas should be detailed enough to start implementation
- **Honest evaluation**: Don't inflate scores; be critical and realistic
- **Iterative refinement**: Use reviewer feedback to genuinely improve ideas
- **Preserve reasoning**: Keep all intermediate outputs (knowledge graph, raw ideas, scores, attack traces)
