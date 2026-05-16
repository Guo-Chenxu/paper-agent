# Abstract Writing Guide

## Goal

Write an abstract that lets a broad computer science reviewer understand the paper's question, gap, contribution, evidence, and scope in one pass.

A strong abstract does not merely advertise novelty. It answers: what is the research question, why does it matter, what was missing before, what does this paper contribute, what evidence supports the claim, and where does the claim apply?

## Core Abstract Logic

Use this order unless the venue or paper type strongly suggests otherwise:

1. **Context / Problem / Research Question**: Name the area, audience need, and concrete problem or question.
2. **Gap**: Explain what current work, practice, theory, tools, systems, or evidence cannot yet provide.
3. **Contribution**: State the paper's main idea, system, theorem, analysis, method, study, dataset, framework, or finding.
4. **Evidence Summary**: Summarize the support, which may be experiments, proofs, measurements, user studies, security analysis, artifact evaluation, case studies, formal reasoning, or deployment experience.
5. **Scope**: State the setting, assumptions, boundaries, or impact so the claim is credible rather than overgeneralized.

## Pre-Writing Questions

Answer these before drafting:

1. What problem or research question does the paper address?
2. Who needs the answer, and what goes wrong without it?
3. What gap remains in prior work, current practice, or existing theory?
4. What is the central contribution, stated as a durable idea rather than a list of implementation details?
5. What evidence supports the contribution, and what kind of evidence is appropriate for this paper type?
6. What is the intended scope: workload, threat model, language, system setting, population, theorem assumptions, dataset, or deployment context when applicable?

## General Template

1. **Opening context**: `[Area/problem] is important because [audience need or consequence].`
2. **Research question**: `This paper asks whether/how [specific question].`
3. **Gap**: `Existing [work/practice/theory/tools] do not yet [missing capability] because [reason].`
4. **Contribution**: `We present [contribution], which [core idea or mechanism].`
5. **Evidence**: `We support this claim through [evidence types], showing [main result/finding/property].`
6. **Scope**: `The results apply to [setting/assumptions] and suggest [impact], while [boundary if important].`

## Paper-Type Variants

### Systems

- Context: operational need, performance/reliability/scalability constraint, deployment pain.
- Gap: existing systems or practice fail under a specific workload, environment, or constraint.
- Contribution: architecture, abstraction, protocol, scheduler, storage design, runtime, or tool.
- Evidence: implementation, workload evaluation, stress tests, deployment data, resource analysis, artifact availability.
- Scope: hardware, workload, scale, assumptions, integration cost.

### Security

- Context: asset, attacker capability, vulnerability class, or defensive need.
- Gap: current defenses, analyses, or assumptions miss a threat or impose unacceptable cost.
- Contribution: attack, defense, analysis framework, tool, protocol, proof, or measurement.
- Evidence: threat model, exploit/defense evaluation, formal argument, empirical measurement, false-positive/false-negative analysis.
- Scope: attacker model, platform, assumptions, disclosure or ethical boundary.

### Programming Languages / Software Engineering

- Context: developer need, correctness property, maintainability problem, language/tool limitation.
- Gap: existing tools, type systems, analyses, or practices cannot express/check/scale to the target property.
- Contribution: language construct, type rule, static/dynamic analysis, verification technique, tool, benchmark when applicable.
- Evidence: soundness proof, implementation, corpus study, usability evidence, performance/scalability evaluation.
- Scope: language subset, assumptions, completeness limits, supported properties.

### Theory / Algorithms

- Context: fundamental problem, model, complexity barrier, or mathematical question.
- Gap: prior bounds, algorithms, reductions, or analyses leave a specific regime unresolved.
- Contribution: theorem, algorithm, lower bound, characterization, reduction, or proof technique.
- Evidence: proof outline, bound comparison, tightness, implications, examples.
- Scope: assumptions, model, parameter regime, limitations.

### HCI / Human-Centered Computing

- Context: human need, interaction problem, design setting, stakeholder tension.
- Gap: existing systems, studies, theories, or design practice do not explain or support the target need.
- Contribution: design artifact, empirical study, theory, taxonomy, method, dataset when applicable.
- Evidence: user study, qualitative analysis, field deployment, controlled experiment, design rationale, triangulation.
- Scope: participant population, context, ecological validity, ethical considerations.

### Measurement / Empirical CS

- Context: phenomenon that practitioners or researchers need to understand.
- Gap: prior measurements are outdated, narrow, indirect, or inconsistent.
- Contribution: measurement methodology, dataset when applicable, empirical findings, taxonomy, or causal/associational analysis.
- Evidence: collection method, validation, statistical analysis, robustness checks, case studies.
- Scope: sampling frame, time window, geographic/platform coverage, observational limits.

## Writing Rules

1. Keep the abstract self-contained; avoid undefined acronyms and paper-internal terms.
2. Use one sentence for one message; do not compress context, gap, and contribution into a single overloaded sentence.
3. State evidence in the same strength as the actual support. A proof supports correctness; a user study supports observed human behavior; measurements support the observed population and period.
4. Avoid default claims about being state-of-the-art, broadly general, or universally applicable unless the paper directly supports them.
5. Mention benchmarks, datasets, ablations, or leaderboards only when they are central and applicable.
6. End with scope or implication rather than hype.

## Abstract Quality Checklist

1. Can a reviewer identify context, problem/question, gap, contribution, evidence, and scope in one pass?
2. Is every major claim supported by an appropriate evidence type?
3. Are terms self-contained and readable outside the paper?
4. Does the abstract avoid overclaiming beyond the studied setting or proof assumptions?
5. Does each sentence carry one message only?
