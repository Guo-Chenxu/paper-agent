# Method Writing Common Issues (Reference Note)

Use this reference as a troubleshooting checklist after drafting Method or Approach.

## Checklist

1. Missing motivation: each contribution unit should state what technical difficulty it resolves.
2. Vague mechanism: avoid naming a component without saying what state it keeps, what input it receives, and what output it produces.
3. Broken flow: the output of one unit should either feed another unit or support a later claim.
4. Unsupported advantage: every claimed advantage should be testable by evaluation, proof, user study, deployment evidence, or measurement validation.
5. Inconsistent terms: use the same name for the same artifact across figures, equations, algorithms, and prose.
6. Hidden assumptions: state environment, adversary, workload, user population, formal model, or sampling assumptions before relying on them.
7. Over-specific implementation detail: keep code-level constants only when they affect correctness, cost, usability, or reproducibility.
