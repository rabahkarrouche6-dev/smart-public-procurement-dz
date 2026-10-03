---
name: tender-document-engine
description: Builds a structured, auditable engine for intelligent tender-document analysis and management.
---

# Tender Document Engine Skill

## Role
Act as a Senior Document Workflow and Procurement Document Engineer.

## Objective
Transform tender documents into structured, reviewable information while keeping the original document authoritative.

## Pipeline
Upload → Security Scan → Parse/OCR → Structure → Extract → Validate → Human Review → Version → Index.

## Extractable Information
- evaluation criteria
- weights
- thresholds
- formulas
- quantities
- prices
- deadlines
- required documents
- technical requirements
- eligibility conditions

## AI Rule
AI may extract, classify, summarize, compare, and flag inconsistencies. It must not invent missing requirements or formulas.

## Versioning
Published versions are immutable. Record:
- source file
- version number
- timestamp
- publisher
- content hash
- change history

## Traceability
Every high-impact extracted value should be traceable to page, section, paragraph, or source location when technically possible.

## Access
Tender documents remain private by default. Server-side authorization must verify identity, organization/role, and any legally applicable entitlement before access.

## Payment/Entitlement
If tender-document payment is legally applicable:
- verify payment/entitlement server-side
- never unlock files using frontend state alone
- issue short-lived authorized access URLs
- keep payment entitlement separate from AI entitlement

## Quality Gate
Verify extraction accuracy, version integrity, traceability, access control, human review paths, and audit events.
