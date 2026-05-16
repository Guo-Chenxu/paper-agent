# Not Recommended: Abstract-Only Contribution Description in Introduction

`Not recommended: do not make a simple contribution appear deeper by hiding how it works. The introduction should still give enough mechanism for readers to judge the claim.`

Expert note:

1. A vague contribution paragraph may sound broad but leaves reviewers unable to assess novelty.
2. The better target is to explain the core mechanism at a high level, then reserve implementation details for Method.
3. Avoid new terms that merely rename ordinary steps.

```latex
% Weak pattern: states an aspiration but hides mechanism.
To address this problem, we propose a new approach that improves reliability and usability.

% Weak pattern: names components without explaining their role.
Our approach contains an analyzer, an optimizer, and a presenter, which together solve the above challenges.

% Better pattern: state mechanism and evidence-facing advantage.
Our approach extracts [artifact], checks [property], and returns [actionable output]. This mechanism improves [claim] because [technical reason that can be evaluated later].
```

## Concrete rewrite

Weak: `We propose a developer-centered repair assistant that makes policy maintenance easier.`

Better: `We propose a repair assistant that converts broad policy rules into candidate narrower rules, ranks candidates by compatibility with observed workflows, and presents the changed privilege set before the developer accepts a repair. This mechanism makes maintenance easier because developers can inspect both the operational evidence and the security consequence of each candidate.`
