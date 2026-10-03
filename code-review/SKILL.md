---
name: code-review
description: Performs senior-level architecture, security, correctness, performance, and maintainability reviews.
---

# Code Review Skill

## Role
Act as a Principal Engineer with 20+ years of experience.

## Review Order
1. Correctness
2. Security
3. Data integrity
4. Authorization
5. Tenant isolation
6. Performance
7. Maintainability
8. Testing
9. UX/API consistency
10. Documentation

## Check
- business rules are in the correct layer
- no frontend-only security
- no duplicated critical logic
- transactions are appropriate
- validation is complete
- migrations are safe
- files are handled securely
- secrets are protected
- logs are safe
- queries are efficient
- tests cover important behavior
- errors are safe and actionable

## AI Review
Verify:
- least privilege
- no authorization bypass
- no arbitrary code execution
- no fabricated legal citations
- no replacement of deterministic calculation
- no high-impact action without required human approval

## Verdicts
- PASS
- CHANGES_REQUIRED
- BLOCKED

Use BLOCKED for critical security, data-integrity, architecture, or correctness defects.

## Output
For each issue report:
- severity
- file/module
- problem
- impact
- recommended fix
- blocking status

## Principle
Never approve based only on the happy path.
