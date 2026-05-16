# Abstract Template B: Observation/Insight -> Contribution -> Evidence

Use this when the paper is driven by an observation, insight, or measured pattern.

```latex
\section{Abstract}
% Observation or insight
% Why the observation creates an opportunity
% Contribution that operationalizes the insight
% Evidence
```

## Reusable skeleton

1. `We observe that [empirical pattern/formal property/user behavior/workload regularity] holds in [setting].`
2. `This observation reveals an opportunity: [what can be simplified, checked, cached, redesigned, or bounded].`
3. `Based on this insight, we introduce [contribution name], which [core contribution].`
4. `[Contribution name] implements the insight through [mechanism 1] and [mechanism 2].`
5. `We provide evidence through [proof/prototype/deployment/study/measurement] showing [main finding].`
6. `The approach is intended for [scope] and does not assume [unwanted overclaim].`

## Concrete examples

Systems: `We observe that most recurring performance regressions in large service fleets arise from a small set of dependency changes rather than from steady-state load. This observation reveals an opportunity: regression diagnosis can focus on change provenance before exploring the full execution trace. Based on this insight, we introduce TraceDelta, a diagnosis tool that links latency changes to dependency updates and ranks candidate causes by temporal alignment and call-path impact. A prototype integrated with production traces reduces the number of traces engineers inspect during incident triage while preserving the root cause in the candidate set for most studied incidents.`

Theory/PL: `We observe that a broad class of incremental dataflow programs uses update functions that are monotone over a finite-height lattice. This property permits convergence guarantees without requiring program-specific termination arguments. Based on this insight, we present a type-directed checker that verifies monotonicity obligations and derives a bound on stabilization rounds. We prove soundness for the core calculus and validate the checker on representative incremental analyses, showing that the derived obligations match the invariants developers already document informally.`
