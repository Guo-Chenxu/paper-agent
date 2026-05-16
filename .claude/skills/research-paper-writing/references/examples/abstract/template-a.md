# Abstract Template A: Problem/Gap -> Contribution -> Evidence

Use this when the abstract should first establish an important gap.

```latex
\section{Abstract}
% Problem context
% Gap in existing practice or technique
% Contribution that addresses the gap
% Mechanism summary in one sentence
% Evidence and scope
```

## Reusable skeleton

1. `[Area] increasingly relies on [capability], but [stakeholders/systems/developers] still face [gap].`
2. `Existing approaches [what they do] but fail to [specific requirement] because [technical reason].`
3. `We present [contribution name], a [system/analysis/tool/algorithm/study] that [core action].`
4. `[Contribution name] works by [mechanism in one sentence: e.g., scheduling, verification, instrumentation, interaction design, proof decomposition].`
5. `We evaluate [contribution name] using [implementation/formal analysis/user study/field measurement/benchmark suite] and show [main evidence].`
6. `These results suggest [scope of claim], while [boundary condition if important].`

## Concrete example

`Large organizations increasingly rely on configuration-as-code to manage production services, but configuration reviews still miss faults that only appear across service boundaries. Existing linters check local syntax and simple invariants, but they fail to reason about cross-file dependencies because the dependency graph is implicit. We present CrossCheck, a static analysis tool that extracts dependency constraints from configuration repositories and checks them incrementally during review. CrossCheck combines a repository-wide dependency index with developer-facing explanations for violated constraints. On three months of changes from a production deployment corpus, CrossCheck identifies previously missed boundary violations with a review-time overhead acceptable for pre-merge use. These results show that cross-file configuration reasoning can be integrated into ordinary review workflows for repositories with stable schema conventions.`
