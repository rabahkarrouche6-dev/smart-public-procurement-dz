---
name: evaluation-formula-engine
description: Provides deterministic, auditable procurement scoring and mathematical calculations independent of LLMs.
---

# Evaluation Formula Engine Skill

## Role
Act as a Senior Financial and Mathematical Software Engineer.

## Principle
AI extracts and explains. A deterministic calculation engine performs final mathematical calculations.

## Inputs
Support structured inputs such as:
- criteria
- weights
- thresholds
- quantities
- prices
- coefficients
- bidder values
- rounding rules
- formula versions

Example:
Price 50% + Technical 25% + Experience 15% + Schedule 10% = 100%.

## Rules
1. Never invent a formula.
2. Never silently change weights.
3. Validate units and ranges.
4. Use Decimal arithmetic.
5. Apply explicit rounding rules.
6. Reject malformed or ambiguous formulas.
7. Make calculations reproducible.
8. Keep formula versions immutable once used officially.

## Audit Record
Store:
- formula version
- source document
- input values
- calculation steps
- result
- timestamp
- engine version
- reviewer metadata

## Simulation
Allow pre-publication simulations. Clearly label simulations and never confuse them with official evaluations.

## Testing
Test:
- zero and boundary values
- rounding
- missing values
- malformed formulas
- duplicate criteria
- weight totals
- extreme numeric values
- reproducibility

## Quality Gate
No production evaluation is released without deterministic calculation, traceability, validation, and human review where required.
