# Introduction Version 4: Open with Context and Challenge

`Use when the area is familiar and the first paragraph can expose the paper's central challenge immediately.`

Expert notes:

1. This opening works when the challenge is easy to state without prior taxonomy.
2. Use it only if the next paragraphs can substantiate the challenge with prior work, examples, or evidence.
3. Avoid declaring victory in the first paragraph; reserve claims for the contribution and evidence paragraphs.

```latex
% Context.
[Computing practice] is central to [important setting].

% Immediate challenge.
Yet [central challenge] remains difficult because [technical cause], especially when [constraint].
```

## Concrete examples

PL: `Static analysis is central to finding defects before code reaches production. Yet making an analysis both precise and usable remains difficult because precision often requires path-sensitive reasoning, especially when developers expect feedback while editing.`

Security: `Enterprise identity systems are central to enforcing access across cloud services. Yet auditing effective permissions remains difficult because privileges are assembled from nested groups, exceptions, and service-specific defaults, especially during organizational change.`

Measurement: `Internet measurements are central to understanding reliability and policy compliance. Yet drawing stable conclusions remains difficult because measurements are shaped by vantage-point placement, protocol heterogeneity, and transient routing changes.`
