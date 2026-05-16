# Introduction Version 3: General Area -> Specific Setting

`Use when readers know the general area but not the paper's particular setting or constraint.`

```latex
% General area and why it matters.
[General area] supports [important capability] in [broad context].

% Specific setting.
This paper focuses on [specific setting], where [constraint, stakeholder, artifact type, or deployment condition] changes the technical requirements.
```

## Concrete examples

Systems: `Autoscaling supports reliable service operation by matching resources to changing demand. This paper focuses on autoscaling for bursty internal workloads, where short-lived spikes, shared quotas, and delayed observability make simple threshold rules unstable.`

Security: `Vulnerability management helps organizations prioritize remediation across large software portfolios. This paper focuses on vulnerabilities introduced through transitive dependencies, where ownership is unclear and the reachable attack surface depends on application-specific use.`

HCI: `Programming assistants can reduce routine development effort by helping users search, edit, and explain code. This paper focuses on assistants used by novice programmers, where suggestions must support learning rather than simply produce a patch.`
