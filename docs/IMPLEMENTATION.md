# Initial implementation — 0.1.0

This is the first implemented offline slice. “Complete” below means the bounded component passed the recorded checks; it does not mean the proposed product or evaluation is complete.

## Completed component tasks

| Task | Work | Status | Delivered behavior |
|---|---|---|---|
| C01 | Build the bounded retry simulator | Complete for this slice | SQLite order, receipt and commitment transaction; stable-key retries, payload conflicts, approval/policy denial and call/tick budgets. |
| C02 | Check captured business evidence | Complete for this slice | Separate smoke, state and hybrid checkers consume the same observation; missing evidence yields inconclusive, with evidence-linked defect findings. |
| C03 | Package, test and document the slice | Complete for this slice | Independent Python package, packaged existing schema resources, locked dependencies, CLI error behavior, behavioral tests, CI and captured demo evidence. |

Source: [core](../src/erp_agent_testbench/core.py), [contracts/utilities](../src/erp_agent_testbench/common.py), [CLI](../src/erp_agent_testbench/cli.py), [behavioral tests](../tests/test_core.py), [CLI tests](../tests/test_cli.py). Runtime selection is recorded in [ADR 0001](decisions/0001-offline-core.md).

## What actually ran

Verified on Python **3.12.13**, Darwin: **18 tests passed, zero failed**, Ruff lint/format checks passed. A wheel was built, installed with locked dependency hashes into a fresh environment and exercised from outside the checkout; its schema files loaded from the installed package. The CLI input/output hashes and implementation-file hashes are in the [verification record](../reports/initial-implementation/verification.json). That file identifies exact tested inputs; expected specifications were not copied into an execution report.

```sh
uv sync --locked
uv run --locked erp-bench run examples/clean-retry.case.json
uv run --locked ruff check src tests
uv run --locked ruff format --check src tests
uv run --locked pytest
```

Observed demo: The clean retry makes two calls but commits one effect: final quantity 13, one commitment of 3,000 minor units. The seeded new-key retry reaches quantity 16 with two commitments totaling 6,000. Smoke passes that defect; state and hybrid checks fail.

[Captured output](../reports/initial-implementation/demo-1.json). [Seeded defect output](../reports/initial-implementation/demo-2.json). Test use of authored expected files is restricted to development assertions; application code does not open them. These are component regressions, not independent held-out evaluation or performance measurements.

## Relationship to the full plan

M1, M2 and M4 have partial component evidence; M3 has one seeded duplicate-retry defect only. M5 remains pending. Packaging covers this slice of M6.

The [build plan](03-build-plan.md), [requirements](01-product-requirements.md), [evaluation](04-evaluation.md) and [definition of done](05-definition-of-done.md) remain the release criteria. Planned acceptance registers describe the wider system; partial progress does not replace their full conditions. Documentation checks validate authored artifacts separately from application CI.

## Explicit limits

This controller supports only a lost response after the first commit, with either a stable key or the seeded new-key defect. It deliberately permits the defective specimen to expose inadequate checking. It is not a production ERP adapter or an independently running agent. Wall-clock/process isolation, durable resume, additional fault families and the held-out benchmark are unimplemented.

All example records and observations are synthetic. No network integration or external business action exists in this slice. Financial and property results support human review. No customer impact, trained-model quality, production readiness or independent endorsement is established.

## Next implementation steps

1. Separate an independently invoked reference adapter from the controller; keep mutation and expected answers inaccessible to it.
2. Implement timeout/process isolation and durable reset/resume, then add approval, schema and partial-execution defects with valid clean counterparts.
3. Validate the observation/result contracts and complete fault accounting before freezing a comparative benchmark.

For each step, add meaningful failure-case tests, capture actual output, preserve evidence/time/money boundaries, and update this record with the revision and unresolved limitations. Do not mark the full release complete from component test counts.
