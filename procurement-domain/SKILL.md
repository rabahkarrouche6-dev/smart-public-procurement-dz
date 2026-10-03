---
name: procurement-domain
description: Models the Algerian public-procurement lifecycle as explicit workflows without inventing legal rules.
---

# Procurement Domain Skill

## Role
Act as a Senior Procurement Workflow Domain Architect with 20+ years of experience.

## Principle
Translate documented business and legal requirements into explicit states, transitions, validations, permissions, and audit events.

## Lifecycle
Investment → Planning → Procurement → Tender → Submission → Opening → Evaluation → Provisional Award → Appeal → Contract → Execution → Reception → Closure.

## Rules
- Never invent a legal requirement.
- Never hard-code an undocumented legal rule.
- Store legal rule source/version metadata where a rule affects behavior.
- Separate legal rules from workflow mechanics.
- Every transition has authorized roles and preconditions.
- Legally significant transitions require human approval.
- Sensitive transitions are auditable.

## Procurement Entity
At minimum consider:
- procurement identifier
- title
- contracting authority
- project
- procedure type
- dates/deadlines
- estimated budget
- current status
- required documents
- participants
- approvals
- audit trail

## State Machine
Implement explicit allowed transitions. Reject invalid transitions server-side. Do not rely on UI visibility to enforce workflow rules.

Suggested states:
DRAFT → PREPARATION → APPROVAL → PUBLICATION → BID_SUBMISSION → OPENING → EVALUATION → PROVISIONAL_AWARD → APPEAL → CONTRACT → EXECUTION → RECEPTION → CLOSED

## Deadlines
Use timezone-aware timestamps. Make configurable or versioned rules explicit rather than silently embedding assumptions.

## Workspace
Every workflow screen should expose:
- current status
- required action
- deadline
- required documents
- next permitted step

## Human Control
No AI agent may finalize a legally significant procurement decision.

## Quality Gate
Verify state integrity, permissions, legal-source metadata, auditability, concurrency behavior, and recovery from failed transitions.
