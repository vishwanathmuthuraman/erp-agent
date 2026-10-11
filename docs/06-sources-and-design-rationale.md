# 06 — Sources and design rationale

Research checked 11 October 2026. Short paraphrases below preserve the distinction between reported findings and this project's choices. No firm endorses this project.

## Problem evidence

**PwC, 2025 Responsible AI survey.** Half of surveyed leaders identified translating principles into scalable operational processes as their largest hurdle. The survey covered 310 US business leaders at director level or above, fielded September 26–October 2, 2025. PwC also discusses testing, monitoring and feedback as operational capabilities. [Official report](https://www.pwc.com/us/en/tech-effect/ai-analytics/responsible-ai-survey.html).

**Project inference:** repeatable workflow tests may help an automation owner turn stated controls into inspectable evidence. The survey does not measure demand for this testbench, willingness to pay, or the frequency of these four defects. Its self-reported US sample is not a universal enterprise failure rate.

**Deloitte, State of AI in the Enterprise, January 2026.** Page 20 reports that 21% of companies surveyed had a mature governance model for autonomous agents. The report describes 3,235 senior respondents across 24 countries, fielded August–September 2025, supplemented by 15 interviews. The sample targets organizations and leaders involved in AI. [Official PDF, governance page 20 and methodology page 40](https://www.deloitte.com/content/dam/assets-zone3/us/en/docs/services/consulting/2026/state-of-ai-2026.pdf).

**Project inference:** a concrete acceptance process is worth testing with implementers. The statistic does not establish that testing alone closes the governance gap, nor that this simulator predicts production reliability.

## Existing approaches and limits of novelty

[Veris](https://veris.ai/) markets policy/workflow benchmarks in simulated systems. [Fabrik](https://www.fabriklabs.ai/) describes stateful workflow tests, reviewed business rules and release comparisons. These are vendor descriptions, not independently verified performance. The proposed contribution is a small inspectable workflow contract, an explicit fault protocol and reproducible comparison. Generic simulation, regression testing and agent tracing are established approaches.

## Technical references and chosen use

| Primary reference | What it establishes | Project decision |
| --- | --- | --- |
| [uv project guide](https://docs.astral.sh/uv/guides/projects/) | Project manifests, lockfiles and uv execution workflow | Pin Python 3.12 and commit a generated lockfile after implementation. |
| [Python 3.12 sqlite3](https://docs.python.org/3.12/library/sqlite3.html) | Transaction control through explicit autocommit configuration | Set transaction behavior explicitly instead of relying on changing defaults. |
| [SQLite isolation](https://www.sqlite.org/isolation.html) | Database transaction/isolation behavior | One writer per run and independent databases; do not imply cross-service atomicity. |
| [JSON Schema 2020-12](https://json-schema.org/draft/2020-12) | Schema vocabulary and validation specification | Use supplied strict schemas, plus semantic reference checks in code. |
| [pytest invocation](https://docs.pytest.org/en/stable/how-to/usage.html) | CLI test selection and invocation | Use meaningful unit, integration and acceptance tests once implemented. |
| [FastAPI manual serving](https://fastapi.tiangolo.com/deployment/manually/) | Serving an ASGI application | Optional read-only localhost report viewer, after static reporting works. |
| [Temporal event history](https://docs.temporal.io/encyclopedia/event-history) | Durable history and replay in its own workflow system | Reuse the general discipline of inspectable histories; this project does not implement Temporal guarantees. |

Our sample sizes, budgets, architecture, prices if later proposed, acceptance thresholds and timelines are design assumptions. Technical citations establish underlying mechanisms, not that this unimplemented testbench works. Recheck dependency/API details at implementation and record selected versions.
