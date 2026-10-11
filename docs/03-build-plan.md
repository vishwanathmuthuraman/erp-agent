# 03 — Public milestones

The repository currently contains a benchmark design and two illustrative cases. Application and evaluation milestones are pending.

| Milestone | Intended result | Evidence required |
|---|---|---|
| M1 — Contracts and isolation | Validate case contracts and isolate state, adapters and evaluator-only truth. | Rejection tests, boundary tests and a reproducible environment. |
| M2 — Clean reference workflow | An independent reference agent completes the purchasing workflow and recovers from a lost response without a duplicate effect. | Actual clean retry trace, state assertions and replay record. |
| M3 — Fault coverage | Exercise duplicate execution, approval/policy errors, schema mismatch and partial execution with valid clean controls. | Reviewed defect triggers, clean counterparts and outcome classification. |
| M4 — Checking and reports | Compare smoke, state and hybrid suites on identical captured evidence. | Evidence-linked findings, bounded execution and safe local reporting. |
| M5 — Frozen evaluation | Evaluate the specified development/held-out corpus without leakage or unaccounted cases. | Split audit, complete denominators, false-alarm/error results and limitations. |
| M6 — Reproducible release | Another environment reproduces the offline demo and documented conclusions. | Clean-install record, regression report and publication review. |

The planned `erp-bench demo` command is an interface target, not an available command. It becomes a quick-start instruction only after a released implementation runs it successfully in a clean environment.

Read the [requirements](01-product-requirements.md), [architecture](02-architecture.md), [evaluation protocol](04-evaluation.md) and [definition of done](05-definition-of-done.md). Optional viewers and model integrations follow the core evaluation; they cannot substitute for fault coverage or trustworthy grading.

Record progress with source revisions and verification artifacts. Performance hypotheses remain hypotheses until the frozen study runs. Report unmet targets and inconclusive cases instead of revising the evaluation to obtain favorable results.
