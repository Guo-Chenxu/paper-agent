# Contribution Motivation Writing Patterns

`Motivation is usually problem-driven: because a specific difficulty remains, the paper introduces a contribution unit to handle it.`

Typical opening sentences:

1. `A remaining challenge is ...`
2. `However, this approach still ...`
3. `The direct solution is insufficient because ...`
4. `This creates a need for ...`

Usage note:

1. State the specific failure before introducing the contribution unit.
2. Keep motivation independent from implementation details.
3. Make the motivation evidence-facing: the reader should see what later proof, evaluation, study, or measurement must establish.

## Area-specific examples

Systems: `A remaining challenge is that complete tracing gives detailed evidence only after an incident has already affected users.`

Security: `The direct repair is insufficient because removing every unused privilege can break rare but legitimate workflows.`

PL: `This creates a need for a constraint representation that preserves source-level explanations after internal simplification.`

Theory: `The standard recurrence is insufficient because it assumes a fixed horizon, while the online variant may stop after any round.`

HCI: `A remaining challenge is that explanations shown too early interrupt users who already understand the suggestion.`

Measurement: `The direct sample is insufficient because repository metadata confounds active projects with generated mirrors.`
