# Related Work Writing Guide

## Goal

Position your work against the most relevant lines of research, and make your novelty easy to verify.

## Workflow

1. List the closest prior work or comparison points first.
2. Group literature by research line, concept, system class, technique, theoretical result, user-study theme, measurement method, or other intellectually meaningful topic; do not group by publication year alone.
3. For each topic: summarize the common framing or contribution pattern, then the limitation or open question relevant to your work.
4. Compare mechanisms, assumptions, evidence type, scope, and failure modes where they matter.
5. End each topic by clarifying your distinction.

Do not assume every CS paper has direct baselines. Theory papers, systems papers, measurement papers, security papers, HCI studies, programming-language papers, datasets, and position/analysis papers may need comparison points rather than head-to-head baselines.

## Topic Design

Use 2-4 focused topics, for example:

1. Closest prior work addressing the same problem, concept, or research line.
2. Systems, methods, theories, artifacts, studies, or measurements closest to your core contribution.
3. Techniques, assumptions, models, tools, datasets, study designs, or analytical frameworks your work builds on.

## Paragraph Template

1. Topic sentence: define the scope of this research line/concept/system class/technique/theoretical result/user-study theme/measurement method.
2. Representative work: one compact summary of what this group contributes.
3. Comparison: explain relevant differences in mechanism, assumption, evidence type, scope, or failure mode.
4. Gap or limitation tied to your target challenge.
5. Transition sentence that leads to your contribution.

## Do and Don't

1. Do compare mechanisms, assumptions, evidence type, scope, and failure modes.
2. Do emphasize the exact gap your contribution fills.
3. Do explain whether your work improves on, complements, generalizes, reinterprets, or challenges prior work.
4. Do not make Related Work a citation dump.
5. Do not hide the closest prior work or strongest comparison points.
6. Do not force SOTA, benchmark, dataset, or ablation language onto papers where those concepts are not the right comparison frame.

## Checklist

1. Are all closest prior work and strongest/recent comparison points covered?
2. Is each topic connected to your problem setting, assumptions, contribution type, and evidence type?
3. Is your difference explained in technical, theoretical, empirical, methodological, or design terms rather than marketing terms?
4. Are scope differences explicit: setting, threat model, formal model, workload, population, deployment context, or measurement context?
5. Is citation coverage complete for all core claims?
