# Mechanism Design Example

This example uses `%` comments as annotations. Each annotation explains the paragraph directly below it.

```latex
\begin{quote}
\textbf{Annotation rule.} Each line starting with \% labels the role of the paragraph directly below it.
\end{quote}

\begin{itemize}
\item Motivation of this contribution unit
\item Mechanism design: maintained state
\item Mechanism design: execution process
\item Cost, correctness, or usability trade-off
\end{itemize}

\subsection{Incremental Policy-Graph Checking}

% Motivation of this contribution unit
Review-time policy checking must be fast enough to run on every proposed change, but access-control policies often contain dependencies across teams, services, and exception rules. Rechecking the full policy graph after each edit gives precise feedback but delays review on large repositories. We therefore need an incremental mechanism that preserves cross-rule reasoning while limiting work to the affected region.

% Mechanism design: maintained state
The checker maintains a policy graph \(G=(V,E)\), where vertices represent policy fragments, service identities, and protected resources, and edges represent grants, inheritance, or dependency constraints. For each vertex, the checker stores the normalized rule text, the source file location, and a summary of constraints that depend on the vertex. This state lets the checker connect a proposed edit to the rules and resources that may be affected by the edit.

% Mechanism design: execution process
Given a proposed change, the checker first parses the changed policy fragments and updates the corresponding vertices. It then traverses outgoing and incoming dependency edges until it reaches vertices whose summaries are unchanged. For the affected subgraph, the checker evaluates safety constraints and emits violations with source locations and dependency paths. Unchanged subgraphs reuse their stored summaries.

% Cost, correctness, or usability trade-off
This mechanism trades a small amount of persistent index state for lower review-time latency. The trade-off is appropriate because policy repositories change incrementally, while the dependency structure is reused across many reviews. The emitted dependency path also supports usability: developers can see why a local edit affects a remote resource instead of receiving a detached error message.
```

## Reusable skeleton

1. `Need`: why the direct or full solution is too slow, imprecise, hard to prove, or hard to use.
2. `State`: data structures, invariants, interface state, formal objects, or study artifacts.
3. `Process`: input -> transformation -> output.
4. `Trade-off`: what cost is accepted and why it supports the paper's claim.
