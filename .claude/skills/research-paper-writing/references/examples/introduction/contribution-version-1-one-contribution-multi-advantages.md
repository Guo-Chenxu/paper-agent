# Contribution Version 1: One Contribution, Multiple Advantages

`Use when the introduction should present one central contribution and explain two or three technical advantages.`

```latex
% Contribution sentence.
In this paper, we present [contribution name], a [system/tool/analysis/model/study/algorithm] for [problem].

% Optional figure pointer.
Figure [x] illustrates the main idea.

% Mechanism summary.
The key idea is [one-sentence mechanism].

% Concrete operation.
Specifically, [contribution name] [step 1], [step 2], and [step 3].

% Advantage 1.
This design [advantage 1] because [reason].

% Advantage 2.
It also [advantage 2] because [reason].
```

## Concrete example

`In this paper, we present ConfigLens, a review-time analysis tool for service configuration changes. Figure 2 illustrates the main idea. The key idea is to reconstruct a dependency graph from configuration references and check proposed edits against graph-level invariants before deployment. Specifically, ConfigLens parses repository changes, updates only the affected portion of the graph, and produces explanations that point back to the changed files. This design gives developers early feedback because violations are detected during review rather than after rollout. It also keeps feedback actionable because each warning names the dependent service and the invariant that would be broken.`
