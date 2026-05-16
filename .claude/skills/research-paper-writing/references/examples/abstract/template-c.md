# Abstract Template C: Multiple Contributions -> Evidence and Scope

Use this when the paper has several contributions that must be named without turning the abstract into a table of contents.

```latex
% Context and gap
% Contribution 1 + advantage
% Contribution 2 + advantage
% Optional contribution 3 + advantage
% Evidence
% Scope and limitation
```

## Reusable skeleton

1. `[Problem context] remains difficult because [central gap].`
2. `We make three contributions.`
3. `First, [contribution 1] [technical advantage].`
4. `Second, [contribution 2] [technical advantage].`
5. `Third, [contribution 3] [technical advantage].`
6. `We evaluate these contributions with [evidence forms] and find [main results].`
7. `The claims apply to [scope]; [limitation or assumption] remains outside this paper.`

## Concrete example

`Reliable permission management remains difficult because access-control policies are written by many teams but enforced by shared infrastructure. We make three contributions. First, we define a policy normalization layer that converts heterogeneous rules into a common intermediate form, making conflicts explicit before deployment. Second, we introduce an incremental checker that validates only the affected portion of the policy graph, keeping feedback fast enough for review. Third, we design explanations that map checker results back to the original policy fragments, helping engineers repair violations without learning the intermediate form. We evaluate these contributions using a prototype, a historical-policy replay, and interviews with security engineers. The results show that the approach exposes latent conflicts and produces actionable explanations for the policy styles in our corpus; policies with dynamic runtime predicates remain outside this paper's scope.`
