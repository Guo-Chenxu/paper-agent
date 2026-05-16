# Paper Review

## Goal

Use an adversarial, reviewer-style checklist to detect reject risks early and revise the paper before submission.

## Core Principle

Assume reviewers will probe every weak point: contribution, claim support, assumptions, scope, organization, reproducibility, and relationship to prior work.

## Critical Rule (Do Not Violate)

Every major claim, especially in Abstract and Introduction, must be:

1. technically correct, and
2. explicitly supported by evidence appropriate for the contribution type.

Evidence may include proof, formal analysis, empirical study, user study, measurement, case study, system artifact, implementation detail, performance or reliability result, qualitative analysis, design rationale, or comparison to prior work. If a claim is not supported, either add suitable evidence or weaken/remove the claim.

## What Usually Gets a Paper Accepted

1. Clear contribution: the paper states what new knowledge, artifact, theorem, system, analysis, dataset, study, technique, or perspective it gives readers.
2. Appropriate evidence for the contribution type: the support matches the claim, whether proof, experiment, study, artifact evaluation, measurement, analysis, or careful argument.
3. Honest assumptions, scope, limitations, validity threats, and reproducibility/verifiability details.
4. Clear prior-work positioning: readers can see how the contribution differs from and improves on, complements, generalizes, or challenges existing work.

## Common Rejection Dimensions

| Rejection Dimension | Typical Failure Signals |
| --- | --- |
| 1. Unclear contribution | 1.1 The paper does not state what is new or useful.<br />1.2 The claimed contribution is too broad, too incremental, or indistinguishable from prior work.<br />1.3 The novelty type is ambiguous: result, system, study, theory, method, analysis, dataset, tool, or insight. |
| 2. Unsupported or overstated claims | 2.1 Abstract/Introduction claims go beyond the evidence.<br />2.2 The paper implies generality, causality, practicality, security, correctness, usability, or performance without support.<br />2.3 Negative claims about prior work are not substantiated. |
| 3. Weak or mismatched evidence | 3.1 Evidence does not match the contribution type.<br />3.2 Proof, experiment, study, artifact, measurement, analysis, or comparison is too narrow to support the claim.<br />3.3 Important alternative explanations or comparison points are missing. |
| 4. Missing assumptions, scope, or validity | 4.1 Assumptions are implicit or unrealistic.<br />4.2 Threat model, proof scope, study population, workload, deployment setting, or measurement context is unclear.<br />4.3 Limitations and validity threats are hidden or only mentioned superficially. |
| 5. Poor reproducibility or verifiability | 5.1 Key definitions, algorithms, protocols, proofs, study instruments, implementation details, or analysis procedures are missing.<br />5.2 A knowledgeable reader cannot verify the reasoning or reproduce the artifact/study/evaluation from the paper and released materials.<br />5.3 Data, code, scripts, formal statements, or experimental/study protocols are unavailable without explanation. |
| 6. Unclear organization | 6.1 The paper buries the main contribution or evidence.<br />6.2 Section order does not match the reader's reasoning path.<br />6.3 Terms, notation, claims, and evaluation criteria are inconsistent across sections. |
| 7. Inadequate positioning | 7.1 Closest prior work or comparison points are omitted.<br />7.2 Differences are described in marketing terms rather than technical, theoretical, empirical, or methodological terms.<br />7.3 The paper does not explain whether it improves on, complements, generalizes, or contradicts related work. |

## Revision Self-Review Question List

Use this checklist as an internal revision tool, not as text to include in the submitted paper unless the venue explicitly asks for a checklist, ethics statement, or reproducibility statement.
Use each question to trigger concrete edits before submission.

### 1. Contribution and Novelty

1. What new knowledge, artifact, theorem, system, dataset, study, measurement, technique, analysis, or insight does this paper give readers?
2. Is the contribution stated in one or two precise sentences?
3. Is the novelty non-obvious relative to the closest prior work or comparison points?
4. Is the contribution meaningful for the target research community or application context?
5. Do we distinguish contribution from implementation details, background, and routine engineering choices?

### 2. Writing Clarity

1. Can a knowledgeable reader understand the problem, contribution, evidence, and scope without guessing?
2. Did we define all key terms, notation, assumptions, protocols, and evaluation criteria before using them?
3. Is each section organized around a clear reader question?
4. Are terms, notation, claims, and evidence consistent across sections?
5. Does each paragraph carry one clear message with smooth transitions?

### 3. Evidence Strength

1. Does each major claim have evidence appropriate to its type: proof, analysis, study, artifact, measurement, comparison, or experiment?
2. Is the evidence strong enough for the claimed scope and target venue?
3. Are comparison points, alternative explanations, or counterexamples handled fairly when relevant?
4. Do we report both strengths and failure cases honestly?
5. Are evidence-generation procedures documented clearly enough to assess reliability?

### 4. Validity, Scope, and Reproducibility

1. Are assumptions, threat model, proof scope, study population, deployment setting, workloads, and measurement context explicit where relevant?
2. Are limitations and validity threats concrete rather than generic disclaimers?
3. Can readers verify the reasoning, reproduce the artifact/study/evaluation, or audit the analysis from the paper and available materials?
4. Are dependencies on data, hardware, participants, formal models, environments, or implementation choices disclosed?
5. Have we avoided overgeneralizing beyond the demonstrated scope?

### 5. Technical, Study, and Proof Soundness

1. Are algorithms, systems, proofs, measurements, study designs, analyses, or methods technically sound?
2. Are definitions, invariants, protocols, statistics, qualitative coding, or formal arguments valid for the claim being made?
3. Are edge cases, failure modes, and alternative explanations addressed?
4. Do benefits outweigh added complexity, assumptions, costs, and limitations?
5. Could reviewers reasonably argue that the net contribution is negative or unverifiable?

## Adversarial Writing Workflow

1. Read the paper as a skeptical reviewer.
2. Answer every question above with explicit evidence from the paper.
3. Mark each item as `pass`, `needs revision`, or `needs stronger evidence`.
4. Revise claims, organization, evidence, proof, study, artifact, analysis, method, assumptions, or scope accordingly.
5. Repeat until no major rejection risk remains.
