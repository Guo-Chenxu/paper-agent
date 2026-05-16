# Contribution Version 4: Observation-Driven Contribution

`Use when the contribution follows from a crisp observation that readers can understand before seeing the full method.`

```latex
% Observation.
We observe that [pattern/property/behavior] in [setting].

% Opportunity.
This observation suggests that [simplification or new design opportunity].

% Contribution.
Based on this observation, we introduce [contribution name], which [mechanism].

% Why it helps.
The mechanism [advantage] because [technical reason].

% Evidence preview.
Our evaluation tests this claim through [evidence form].
```

## Concrete examples

Measurement: `We observe that many apparent package-abandonment events coincide with repository transfers rather than true maintainer inactivity. This observation suggests that abandonment should be measured over project identity, not over a single repository URL. Based on this observation, we introduce a continuity inference method that links package metadata, release history, and ownership changes. The method reduces false abandonment labels because it treats renames and transfers as identity-preserving events when independent evidence agrees. Our evaluation tests this claim through manual validation of sampled transitions and sensitivity analysis over linking rules.`

HCI: `We observe that developers often reject automated suggestions not because the suggested change is wrong, but because the rationale is missing at the moment of review. This observation suggests that explanation timing is as important as explanation content. Based on this observation, we introduce inline rationale cards that appear only when a developer pauses on a suggestion. The mechanism reduces interruption because explanations are available at the point of uncertainty without forcing every suggestion into an expanded view. Our evaluation tests this claim through a controlled study and qualitative analysis of review sessions.`
