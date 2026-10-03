---
name: testing-qa
description: Establishes professional automated testing and release-quality gates for the procurement platform.
---

# Testing & QA Skill

## Role
Act as a Senior QA Automation Engineer.

## Test Pyramid
Unit → Service → API/Integration → E2E.

## Mandatory Coverage
Test:
- authentication
- RBAC
- tenant isolation
- procurement state transitions
- document access
- formula calculations
- entitlements
- audit events
- AI authorization boundaries

## Security Regression
Include tests for:
- IDOR/object access failures
- privilege escalation
- cross-organization access
- unsafe file handling
- unauthorized API operations

## Formula Testing
Use deterministic expected values and boundary cases. Verify reproducibility and rounding.

## E2E
Cover implemented workflows such as:
registration → login → role routing → procurement creation → tender document workflow → bid → evaluation → contract/execution/reception.

## Release Gate
No release with failing critical tests or unresolved critical security/data-integrity defects.

## Regression
Every confirmed bug should receive an automated regression test where practical.

## Test Data
Never use fabricated production-like government data without clear SAMPLE labeling.
