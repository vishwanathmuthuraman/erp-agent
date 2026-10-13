# ADR 0001 — independently runnable offline core

Status: accepted for the initial 0.1.0 component boundary; full application architecture remains in [02-architecture.md](../02-architecture.md).

## Decision and reason

Use Python 3.12.13 for these bounded research calculations and contract controls. The planned Python baseline matches the data/schema ecosystem and avoids another runtime before measurements justify one. Install with uv 0.13.0 and commit `uv.lock`. Runtime contract validation uses jsonschema 4.26.0; pytest 9.1.1 and Ruff 0.16.6 validate behavior and source hygiene. Markdown 3.10.3 remains a development dependency for existing handoff tooling. The build backend is setuptools 80.10.2. Existing root schema JSON files are installed as package resources, rather than duplicated into source.

Each repository owns its package; it imports no sibling project. SQLite backs local transactional facts or retry effects where needed; other components are pure offline calculations. Monetary state uses integer minor units; decimal quantity/rate calculations specify rounding. No web service, database deployment, connector, model key or third-party account is required to run the slice.

## Alternatives and consequences

A web interface and service stack would add authentication, deployment and infrastructure work before these controls are trustworthy. Go/Rust services require a measured systems constraint; Rails would require a separate CRUD/service decision. None is introduced here. This choice does not establish throughput, production isolation or model quality. The maintainer reviews dependency changes through a lockfile diff and affected behavioral tests; installed dependency notices remain applicable. The original license decision was pending at the time of this ADR; the current Apache-2.0 decision is recorded in docs/09-licensing.md.

The current `src/` package is an independently testable component. Future API/worker/UI applications may call or relocate it through a reviewed architecture decision. If superseded, preserve the tested arithmetic/contracts and document migration/rollback before changing service boundaries.

## Evidence

[Fresh wheel installation, schema loading and behavioral checks](../../reports/initial-implementation/verification.json). [Component scope and unfinished work](../IMPLEMENTATION.md).
