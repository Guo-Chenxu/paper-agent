# Contribution Version 3: New Mechanism Added to an Existing Approach

`Use when the paper builds on a known approach but adds one mechanism that changes its capability or reliability.`

```latex
% Prior approach.
Existing approaches commonly [baseline mechanism].

% New mechanism.
Our contribution adds [new mechanism], which [what it computes, checks, proves, or presents].

% Insight or reason.
The mechanism is based on [technical insight], allowing [new capability].

% How it works.
Given [input/artifact], it [step 1], [step 2], and [output].

% Evidence-facing advantage.
Compared with the baseline, this mechanism [advantage] because [reason supported later by evidence].
```

## Concrete examples

PL: `Existing type checkers commonly validate each module against an interface and report violations at the point where a constraint fails. Our contribution adds blame slicing, which computes the smallest set of interface assumptions needed to reproduce an error. The mechanism is based on dependency tracking through constraint generation, allowing the checker to explain errors in terms of user-written interfaces rather than internal constraints. Given a failed check, it traces the contributing assumptions, removes irrelevant constraints, and returns a compact explanation. Compared with the baseline checker, blame slicing improves debuggability because the reported slice matches the abstractions that programmers control.`

Systems: `Existing schedulers commonly assign requests using current load estimates and fixed priority classes. Our contribution adds deadline slack accounting, which computes how much delay each request can tolerate before violating a service objective. The mechanism is based on separating queueing delay from execution time, allowing the scheduler to trade short-term fairness for deadline preservation. Given an incoming request, it estimates slack, updates the queue order, and records why the request was delayed or promoted. Compared with the baseline scheduler, this mechanism improves operator trust because scheduling decisions become inspectable during incidents.`
