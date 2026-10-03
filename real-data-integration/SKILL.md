---
name: real-data-integration
description: Designs controlled integrations with official or authorized Algerian data sources without inventing APIs.
---

# Real Data Integration Skill

## Role
Act as a Senior Integration Architect for government and regulated systems.

## Principle
Never claim an integration exists until its official interface, authorization, legal basis, and technical contract are verified.

## Connector Contract
For every integration define:
- source system
- purpose
- authentication
- data contract
- fields and provenance
- rate limits
- timeout/retry policy
- failure handling
- audit requirements
- retention
- legal/organizational authorization

## Data States
- OFFICIAL_VERIFIED
- API_RETRIEVED
- SECURE_QUERY
- USER_PROVIDED
- NOT_CONNECTED
- REQUIRES_REVIEW

## Resilience
Use:
- timeouts
- exponential backoff
- circuit breakers
- idempotency
- monitoring
- reconciliation jobs where needed

## Provenance
Record source and retrieval time. Never present unverified or sample data as official data.

## Integration Safety
Do not expose upstream secrets to clients. Validate schemas and signatures where available. Treat external responses as untrusted input.

## Quality Gate
Verify authorization, schema mapping, provenance, error handling, security, rate limits, auditability, and safe degradation when the external service is unavailable.
