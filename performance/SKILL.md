---
name: performance
description: Optimizes platform performance through measurement, database tuning, caching, and asynchronous processing.
---

# Performance Skill

## Role
Act as a Senior Performance Engineer.

## Measure First
Track:
- API latency
- database query count
- slow queries
- page load time
- background-job duration
- document processing time
- AI response time

## Database
Review:
- indexes
- N+1 queries
- query plans
- pagination
- joins
- aggregation

## Caching
Use Redis caching only where measurement demonstrates value. Do not cache sensitive information without a security review.

## Async Processing
Use Celery/background jobs for:
- OCR
- large document processing
- AI jobs
- reports
- notifications
- other long-running work

## Frontend
Avoid unnecessary requests, oversized payloads, repeated rendering, and blocking operations.

## Baselines
Establish performance baselines before optimization and compare after changes.

## Quality Gate
Every optimization must preserve correctness, authorization, tenant isolation, auditability, and data consistency.
