# Technical Challenge Version 3: New Problem Framing

`Use when there are no directly comparable methods and the introduction must justify the new framing by decomposing requirements.`

```latex
% Goal and why existing categories do not cover it.
In this work, our goal is [goal]. This setting differs from prior formulations because [distinction].

% Requirement 1.
First, the approach must [requirement], since [reason].

% Requirement 2.
Second, it must [requirement], since [reason].

% Requirement 3.
Third, it must [requirement], since [reason].
```

## Concrete example

`In this work, our goal is to help developers review generated code suggestions while preserving their responsibility for the final change. This setting differs from prior formulations that optimize only suggestion acceptance or patch correctness. First, the interface must expose uncertainty, since a fluent suggestion can still violate project conventions. Second, it must support interruption, since developers often inspect suggestions while holding partial context about the surrounding code. Third, it must produce reviewable artifacts, since teams need to discuss why a suggestion was accepted, edited, or rejected.`

See also:
1. `references/examples/introduction/novel-task-challenge-decomposition.md`
