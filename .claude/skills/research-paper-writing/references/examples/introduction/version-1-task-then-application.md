# Introduction Version 1: Problem First, Then Use Context

`Use when the paper's problem is specialized and readers need a definition before they can appreciate why it matters.`

```latex
% Define the technical problem without assuming the audience knows it.
[Problem] concerns [what artifact, behavior, property, or interaction] under [setting or constraint].

% Explain why the problem matters across CS areas.
This problem matters for [systems/security/PL/theory/HCI/measurement context] because [practical or scientific consequence].
```

## Concrete examples

Systems: `Tail-latency attribution concerns identifying which component change causes a service-level slowdown during a deployment window. This problem matters for large distributed systems because engineers must decide whether to roll back, mitigate, or continue a deployment while user-visible latency is still changing.`

Security: `Least-privilege repair concerns rewriting overly broad access-control rules into narrower rules that preserve intended workflows. This problem matters for security operations because permissive rules accumulate during incidents and often remain after the incident ends.`

PL: `Effect-bound inference concerns deriving where a program may perform externally visible actions, such as I/O or shared-state mutation. This problem matters for language tooling because accurate bounds help compilers and reviewers separate pure computation from operations that require auditing.`
