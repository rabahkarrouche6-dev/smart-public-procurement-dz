---
name: audit-compliance
description: Builds useful, tamper-resistant audit trails and compliance evidence for procurement workflows.
---

# Audit & Compliance Skill

## Role
Act as a Senior Audit and Governance Engineer.

## Objective
Enable reconstruction of important platform actions and workflow history.

## Audit Record
Capture, as appropriate:
- who
- what
- when
- resource
- resource ID
- organization
- result
- old/new values
- correlation/request ID
- IP/device metadata where justified

## Events
Audit:
- authentication events
- permission changes
- procurement transitions
- publication
- document versions
- evaluation changes
- contract changes
- reception
- administrative changes
- security events

## Security
Ordinary users must not modify or delete audit records. Do not log passwords, tokens, or unnecessary sensitive content.

## Access
Provide authorized audit views with filtering and export controls appropriate to the user's role.

## Retention
Define retention and archival policy separately from normal business data deletion.

## Quality Gate
Verify completeness, timestamps, correlation IDs, access control, retention policy, integrity protections, and performance under high event volume.
