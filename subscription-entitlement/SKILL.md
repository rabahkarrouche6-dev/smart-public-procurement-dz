---
name: subscription-entitlement
description: Provides future-ready plans, subscriptions, feature entitlements, and AI usage controls while keeping MVP AI free.
---

# Subscription & Entitlement Skill

## Role
Act as a Senior SaaS Billing and Authorization Architect.

## Model
Plan → Subscription → Entitlement → Feature → Usage.

## MVP
Use an MVP_FREE plan with AI enabled. Do not add payment friction to core MVP workflows.

## Future Plans
Architecture may support:
- FREE
- PRO
- ENTERPRISE

Do not hard-code plan names throughout application logic.

## Enforcement
Entitlements must be checked server-side. Frontend hiding is not authorization.

## Usage
Track AI usage by organization, user, feature, and time period where appropriate.

## Audit
Record entitlement and subscription changes with actor, time, old state, new state, and source.

## Separation
Keep:
- role authorization
- tenant authorization
- feature entitlement
- document/payment entitlement

as separate concerns.

## Quality Gate
Test:
- expired subscriptions
- missing entitlements
- role/entitlement interaction
- usage limits
- concurrent changes
- fail-safe behavior
- unauthorized feature access
