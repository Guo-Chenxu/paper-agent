# Annotated Approach Example

This file converts the contribution-unit triad into reusable writing notes for general CS papers.

## Purpose

Use this mapping to separate:

1. Motivation
2. Mechanism or representation
3. Execution process
4. Evidence-facing advantage

## Block-by-Block Mapping

### Example 1: Systems Scheduling Unit

1. **Motivation**
- The paragraph states the remaining problem: a scheduler can see current load but not whether delaying a request risks a deadline violation.
- It explains why existing priority queues are insufficient under bursty arrivals.

2. **Mechanism**
- The paragraph defines a slack score for each request from arrival time, estimated service time, and deadline.
- It specifies the state maintained by the scheduler: queue entries, recent service-time summaries, and per-class deadline targets.

3. **Execution process**
- The paragraph explains the order: compute slack for the new request, update queued slack values, choose the request with least safe slack, and record the scheduling reason.

4. **Evidence-facing advantage**
- The paragraph links the design to evaluation: if deadline misses decrease without excessive starvation, the slack mechanism supports the paper's claim.

### Example 2: Security Analysis Unit

1. **Motivation**
- The paragraph states the remaining problem: broad access rules are easy to identify but hard to repair safely.

2. **Mechanism**
- The paragraph defines a candidate-rule generator that intersects observed accesses with policy constraints.

3. **Execution process**
- The paragraph explains the order: collect relevant access events, remove events outside the repair window, generate candidate narrower rules, and rank candidates by preserved workflows.

4. **Evidence-facing advantage**
- The paragraph links the design to evidence: repairs should reduce unnecessary privileges while preserving legitimate operations in historical replay.

## Reusable Writing Pattern

For each contribution-unit subsection, follow this order:

1. `Motivation`: state unresolved challenge and technical reason.
2. `Mechanism`: define the state, artifact, rule, interface, or mathematical object.
3. `Process`: describe the operation in input -> steps -> output order.
4. `Advantage`: explain why this unit supports the claim that later evidence tests.

## Suggested Paragraph Starters

1. Motivation: `A remaining challenge is ...`
2. Mechanism: `We represent ... as ...` or `We maintain ... to ...`
3. Process: `Given [input], the unit first ... then ... finally ...`
4. Advantage: `This design supports [claim] because ...`
