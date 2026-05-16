# Introduction New-Problem Challenge Decomposition

`For new problem framings without direct comparisons, decompose the challenge into clear requirements.`

```latex
% Goal.
To achieve [goal], an approach must satisfy three requirements.

% Requirement 1.
First, it must [requirement] because [technical/practical reason].

% Requirement 2.
Second, it must [requirement] because [technical/practical reason].

% Requirement 3.
Third, it must [requirement] because [technical/practical reason].
```

## Concrete examples

Systems: `To support safe automated rollback in a microservice fleet, an approach must satisfy three requirements. First, it must identify the affected dependency path because a local change may surface as latency in another service. Second, it must make decisions from partial observations because waiting for complete telemetry delays mitigation. Third, it must expose the reason for rollback because operators need to distinguish true regressions from correlated background events.`

HCI: `To design a useful explanation interface for code-review assistants, an approach must satisfy three requirements. First, it must show what evidence the assistant used because developers need to judge whether relevant context was omitted. Second, it must preserve the developer's editing flow because explanation panels that demand a separate workflow are ignored. Third, it must support team discussion because many code-review decisions are social as well as technical.`

Measurement: `To measure dependency abandonment in package ecosystems, an approach must satisfy three requirements. First, it must distinguish inactivity from stability because mature packages may change rarely. Second, it must handle package renames and transfers because repository identity is not stable over time. Third, it must report sensitivity to sampling rules because ecosystem conclusions can change when generated packages or mirrors are included.`
