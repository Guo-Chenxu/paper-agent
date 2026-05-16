# Example of the Three Elements

This example uses `%` comments as annotations. Each `% ...` annotation explains the paragraph(s) immediately below it.

```latex
\begin{quote}
\textbf{Annotation rule.} In this example, each line starting with \% labels the role of the paragraph(s) directly below it.
\end{quote}

\begin{itemize}
\item Motivation of the contribution unit
\item Mechanism design: representation or state
\item Mechanism design: execution process
\item Evidence-facing advantage
\end{itemize}

\subsection{3.1. Policy Dependency Graph}

% Motivation of the contribution unit
Access-control policies are often reviewed file by file, but the effect of a rule depends on group membership, inherited roles, and service-specific defaults defined elsewhere. A local checker can therefore approve a change that grants access through an indirect dependency. To reason about these effects during review, we need a representation that makes cross-file dependencies explicit.

% Mechanism design: representation or state
We represent the policy repository as a typed dependency graph. Vertices correspond to identities, groups, policy rules, services, and protected resources. Edges encode membership, grants, inheritance, and default privileges. Each edge stores its source location and condition, allowing the checker to map graph-level findings back to repository text.

% Mechanism design: execution process
Given a proposed policy edit, the checker updates vertices and edges touched by the edit, computes the affected dependency region, and reevaluates safety constraints only in that region. When a constraint fails, the checker returns the shortest dependency path from the changed rule to the affected resource, together with the source locations for each path element.

% Evidence-facing advantage
This design supports review-time auditing because it combines global reasoning with incremental updates. The dependency path also makes warnings actionable: a reviewer can inspect why the edit changes effective access rather than receiving only a pass/fail result.

\subsection{3.2. Repair Candidate Ranking}

% Motivation of the contribution unit
After a violation is found, simply deleting the broad rule may break legitimate workflows. The repair step must therefore narrow privileges while preserving accesses that are still needed.

% Mechanism design: representation or state
For each violation, the repair unit constructs candidate rules from three sources: observed accesses during a configurable window, declared service ownership, and constraints already present in neighboring policies. Each candidate records the privileges it removes and the historical accesses it preserves.

% Mechanism design: execution process
The unit first filters observations to those involving the affected identity and resource family. It then generates candidate narrower rules, discards candidates that violate mandatory constraints, and ranks the remaining candidates by preserved workflow coverage and privilege reduction. The top candidates are presented with a summary of changed privileges.

% Evidence-facing advantage
This design makes repair suggestions auditable because each candidate is tied to both security impact and workflow evidence. Later evaluation can test whether candidates reduce unnecessary privileges while avoiding breakage in historical replay.
```
