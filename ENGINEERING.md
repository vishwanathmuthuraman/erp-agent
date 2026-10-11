# Engineering standards

These are standing implementation rules. They describe decisions to follow, not capabilities already delivered. Read the repository's requirements and current status before writing code.

## Choose technology for the workload

| Workload | Default | Decision rule |
|---|---|---|
| Research, statistics, ML training, evaluation | Python | Prefer its scientific ecosystem and a reproducible environment. Keep orchestration separate from measured model behavior. |
| Financial transformations and durable data | SQL; SQLite for isolated local studies, PostgreSQL for justified shared services | Make identity, amounts, permissions and transactions explicit. |
| Concurrent integrations and independent production services | Go when a service is justified | Require defined throughput, cancellation, retry and operational requirements. Keep a simpler Python service if it meets them. |
| A constrained inference or compute hot path | Rust when profiling supports it | Benchmark end-to-end latency, memory and correctness against the simpler baseline before adding a second runtime. |
| Browser interfaces | TypeScript | Use one maintained interface stack suited to the actual product. Do not build a UI before the core workflow is testable. |
| Conventional business CRUD application | Rails may be an alternative | Choose it only through an architecture decision based on team expertise and delivery needs. Do not add it alongside another backend without a clear boundary. |

There is no mandatory language collection. Language choice is not copy protection or evidence of sophistication. Existing project-specific Python/SQL plans remain the baseline until a recorded decision replaces them.

## Architecture decision required

Before a framework, language, database or service-boundary change, record: problem; correctness/security constraints; alternatives; representative workload; measured or explicitly unmeasured tradeoffs; operating cost; maintainer capability; migration and rollback; and the acceptance test. Freeze the decision for the release under study. Pin tested dependencies and supported toolchain versions when implementation begins.

## Correctness before model output

Use deterministic rules for money, authorization, identity, state changes, idempotency and dispatch. Treat model output and imported text as untrusted proposals. Preserve provenance and explicit unknown/error states. Never equate an anomaly with fraud, a request with completion, or an expected answer with an observed result.

## Reproducibility and evidence

Separate development, validation and held-out evaluation. Use appropriate time/entity splits; prevent future or label leakage. Keep an explicit baseline, locked evaluation protocol, run manifest and all material failures. Report relevant quality, cost, latency and workload limits together. A new dependency or optimization must pass the affected behavioral checks. Documentation checks do not establish application performance.

## Publication and authorship

Commit using the configured maintainer identity. Do not append assistant signatures, product branding or automated assistant coauthor trailers. Preserve real human contributions, required third-party notices and source citations. Do not invent sole manual authorship, completed features, scores, users, research acceptance, certifications or institutional endorsement. Honor required venue disclosures when submitting work.

Public artifacts use synthetic or explicitly authorized inputs. Customer data, credentials, internal schedules, commercial plans and operational access details stay outside public repositories. Keep algorithms and protocols public only to the extent deliberately chosen for reproducibility. Review both content and history before publication; ordinary deletion does not remove earlier public copies.
