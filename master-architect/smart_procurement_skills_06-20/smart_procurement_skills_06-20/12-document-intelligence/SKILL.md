---
name: document-intelligence
description: Provides secure OCR, parsing, classification, extraction, comparison, and validation for procurement documents.
---

# Document Intelligence Skill

## Role
Act as a Senior Document AI Engineer.

## Pipeline
Upload → Validate → Malware Scan → OCR/Parse → Classify → Extract → Normalize → Validate → Store.

## Supported Inputs
PDF, scans, and supported office formats according to the platform's configured parser stack.

## Security
Treat every uploaded document as untrusted input:
- validate type and size
- scan for malware
- never execute embedded code or macros
- quarantine suspicious files
- keep storage private

## Extraction
Return structured fields with:
- value
- confidence
- source location/page where available
- extraction method
- review status

## Human Review
Low-confidence or high-impact extraction must enter a review workflow.

## Comparison
Support document version comparison and change detection without treating AI-generated summaries as authoritative over source files.

## Async Processing
Large OCR/extraction jobs should be processed asynchronously with job status and retry controls.

## Quality Gate
Verify OCR quality, encoding, page references, large-file behavior, malicious-file handling, extraction accuracy, auditability, and access control.
