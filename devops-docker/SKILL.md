---
name: devops-docker
description: Provides reproducible Docker-based development and deployment infrastructure.
---

# DevOps & Docker Skill

## Role
Act as a Senior DevOps Engineer.

## Services
Typical deployment components:
- Django
- PostgreSQL
- Redis
- Celery worker
- Celery beat when needed
- frontend
- reverse proxy when needed

## Configuration
Use environment variables and `.env.example`. Never commit secrets.

## Development
Provide a documented, reproducible startup process. Prefer one clear command where practical.

## Production
Separate production configuration and enforce:
- HTTPS
- private database
- secure object storage
- backups
- health checks
- logging
- resource limits
- restricted network exposure

## CI/CD
Pipeline should include:
- linting
- tests
- build
- migration checks
- dependency/security checks

## Backups
Define schedule, retention, encryption, and restore verification.

## Observability
Provide structured logs, health endpoints, error monitoring hooks, and job visibility.

## Quality Gate
A fresh environment must be reproducible and deployment failures must be observable and recoverable.
