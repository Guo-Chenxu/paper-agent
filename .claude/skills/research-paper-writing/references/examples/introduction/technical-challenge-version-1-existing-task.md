# Technical Challenge Version 1: Established Problem, Existing Approaches

`Use when prior work already addresses the problem and the introduction must show why a remaining challenge is technically unresolved.`

```latex
% State the broad challenge.
This problem is challenging because [reason 1], [reason 2], and [reason 3].

% Prior approach class 1.
Traditional approaches [mechanism], which [benefit].
However, they [limitation] because [technical reason].

% Prior approach class 2.
Recent approaches [mechanism], which [benefit].
However, they still [remaining limitation] because [technical reason].

% Lead to our contribution.
This leaves a gap: [precise gap your paper addresses].
```

## Concrete example

`Detecting misconfigurations in distributed services is challenging because configuration values are spread across repositories, interpreted by different runtimes, and changed by teams with different ownership boundaries. Rule-based checkers catch local errors and enforce naming conventions, which makes them useful during review. However, they miss cross-service violations because they do not reconstruct the dependency relationships among configuration keys. Recent runtime monitors observe deployed behavior and can detect some violations after rollout. However, they still provide late feedback because the invalid configuration has already reached production. This leaves a gap: developers need review-time checks that reason about cross-service dependencies without requiring a full production replay.`
