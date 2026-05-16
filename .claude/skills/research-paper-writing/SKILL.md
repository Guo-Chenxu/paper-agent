---
name: research-paper-writing
description: Use when drafting, revising, polishing, or reviewing computer science research papers, including Abstract, Introduction, Related Work, Technical Core, Evaluation, Conclusion, figures, tables, claim-evidence alignment, or submission self-review.
---
# Research Paper Writing

## Overview

Use this skill to turn a computer science research paper into a reviewer-friendly, high-clarity draft. Prioritize a clear research story, one-message paragraphs, evidence-backed claims, readable figures/tables, and skeptical self-review before submission.

## Core Workflow

1. Clarify the paper story before sentence-level edits.
2. Load only the section-specific guide needed from `references/`.
3. Draft or revise paragraph-by-paragraph with one message per paragraph.
4. Run reverse outlining after each section: section thesis -> paragraph messages -> evidence/explanation.
5. Align every major claim in Abstract and Introduction with explicit support from experiments, proofs, measurements, case studies, user studies, analyses, artifacts, or other appropriate evidence.
6. Run adversarial review with `references/paper-review.md` before finalizing.

## Global Principles

1. Keep one paragraph for one message only.
2. State the paragraph message in the first sentence.
3. Make nouns self-contained; define new terms before reusing them.
4. Maintain sentence-to-sentence flow through cause, contrast, consequence, refinement, or example.
5. Use a story-first structure: context -> problem/question -> gap -> contribution -> evidence -> scope/impact.
6. Treat claim-evidence alignment as a hard constraint; weaken or remove unsupported claims.
7. Read as a skeptical reviewer and resolve likely objections explicitly.
8. Treat visual quality as core content, not decoration.
9. Use clear overview, architecture, proof-roadmap, workflow, measurement, or design figures when applicable.
10. Use readable, minimal-ink tables with captions that explain setting, units, and takeaway.

## Paragraph Clarity Check

Use this quick test whenever the user asks whether a paragraph flows or is clear.

1. Read as an external reader:
   - Does this paragraph have one explicit message?
   - Does the first sentence state what this paragraph will do?
   - Are all key nouns/terms readable without hidden context?
   - Does each sentence connect to the previous one with a clear relation?
2. Run reverse outlining for the current section:
   - Write down the section thesis or main claim.
   - Write down each paragraph topic sentence.
   - Write down the evidence, explanation, or reasoning under each paragraph.
   - Check mapping: topic sentence -> thesis, and evidence/reasoning -> topic sentence.
   - Revise or remove any paragraph that cannot be mapped cleanly.
3. If flow is still weak, add temporary section headers and explicit transition phrases during revision, then remove unnecessary scaffolding before finalizing.

Source reference for this check:

- `references/does-my-writing-flow-source.md`

## Section Guides

Load only the needed section file:

- Introduction: `references/introduction.md`
- Abstract: `references/abstract.md`
- Related Work: `references/related-work.md`
- Technical Core / Method: `references/method.md`
- Evaluation and Evidence: `references/experiments.md`
- Conclusion: `references/conclusion.md`
- Paper review: `references/paper-review.md`
- Paragraph clarity source: `references/does-my-writing-flow-source.md`
- Example bank index: `references/examples/index.md`

## Paper Review Core Points

Use `references/paper-review.md` for the full checklist and workflow.

1. Add an end-of-draft self-review question list in five dimensions:
   - contribution,
   - writing clarity,
   - evidence strength,
   - evaluation completeness,
   - technical soundness.
2. Treat claim-evidence alignment as mandatory for Abstract and Introduction.
3. Perform adversarial review as a skeptical reviewer and resolve every high-risk question.
4. Revise until major rejection risks are explicitly addressed.

## Execution Rules

1. Build a mini-outline before drafting prose.
2. For each subsection, include motivation, design/argument, and advantage when applicable.
3. Do not frame the paper as a small patch over a naive baseline; frame the real research question and contribution.
4. Keep terminology stable across the full paper.
5. If a claim cannot be supported by appropriate evidence, weaken or remove the claim.
6. Before finalizing, append and answer a five-dimension self-review question list, then revise based on unresolved items.
7. Do not load all section references at once; load only the guide needed for the current edit target.

## Output Contract

When asked to rewrite or draft sections, return:

1. A compact section outline with 3-7 bullets.
2. Revised paragraphs with explicit paragraph roles, such as context, problem, gap, contribution, technical core, evidence, limitation, or impact.
3. A short self-review checklist covering clarity, flow, terminology consistency, unsupported claims, and missing evidence.
4. A claim-evidence map for each major claim using `Claim: ... | Evidence: ... | Status: supported/needs evidence`.
