# Contribution Version 2: Two Linked Contributions

`Use when the introduction has two contributions and the second one solves a limitation introduced by the first.`

```latex
% Contribution overview.
We make two linked contributions for [problem].

% Contribution 1.
First, we introduce [contribution 1], which [mechanism] and [benefit].

% Why contribution 1 is insufficient alone.
However, [remaining challenge] arises because [reason].

% Contribution 2.
Second, we introduce [contribution 2], which [mechanism] and [benefit].

% Evidence preview.
Together, these contributions are evaluated through [evidence form] and show [main evidence].
```

## Concrete example

`We make two linked contributions for auditing third-party package risk. First, we introduce a reachability analysis that maps imported packages to the code paths that can invoke them, reducing the number of dependencies that require manual review. However, reachability alone is insufficient because build scripts and optional plugins may execute outside ordinary import paths. Second, we introduce an execution-context classifier that separates install-time, test-time, and runtime dependencies using repository metadata and lightweight dynamic checks. Together, these contributions are evaluated through a replay of historical dependency changes and show that risk reports become both smaller and better aligned with engineer judgment.`
