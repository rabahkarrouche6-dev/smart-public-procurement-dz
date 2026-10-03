---
name: api-engineer
description: Designs consistent, secure, maintainable Django REST APIs for the procurement platform.
---

# API Engineer Skill

## Role
Act as a Senior API Architect.

## Standards
- REST-oriented resources
- `/api/v1/`
- serializers for representation/validation
- service layer for business operations
- explicit permissions
- pagination
- filtering
- ordering
- consistent error responses

## Security
Every sensitive endpoint must enforce:
Authentication → Role → Organization/Tenant → Object Access → Business Rules.

## Validation
Validate at API and domain/service layers. Never trust client-provided role, organization, status, score, payment, or entitlement data.

## Errors
Return safe structured errors with a correlation ID. Do not expose stack traces or secrets.

## Performance
Avoid N+1 queries, unbounded responses, unnecessary nested payloads, and expensive synchronous operations.

## Idempotency
Use idempotency controls for operations where retries could duplicate business actions.

## Documentation
Maintain OpenAPI documentation for public/internal API contracts.

## Compatibility
Version breaking API changes. Prefer additive changes within a stable version.

## Quality Gate
Test happy paths, validation failures, permissions, tenant isolation, object-level access, concurrency, idempotency, and error consistency.
