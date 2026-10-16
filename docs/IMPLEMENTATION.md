# Initial implementation — 0.1.0

This is the first implemented offline slice. “Complete” below means the bounded component passed the recorded checks; it does not mean the proposed product or evaluation is complete.

## Completed component tasks

| Task | Work | Status | Delivered behavior |
|---|---|---|---|
| C01 | Build the bounded retry simulator | Complete for this slice | SQLite order, receipt and commitment transaction; stable-key retries, payload conflicts, approval/policy denial and call/tick budgets. |
| C02 | Check captured business evidence | Complete for this slice | Separate smoke, state and hybrid checkers consume the same observation; missing evidence yields inconclusive, with evidence-linked defect findings. |
| C03 | Package, test and document the slice | Complete for this slice | Independent Python package, packaged existing schema resources, locked dependencies, CLI error behavior, behavioral tests, CI and captured demo evidence. |
| C04 | Separate public retry-adapter inputs from controller state | Complete for this slice | Immutable public records, restricted amendment tool responses, separately invoked reference adapter, controller-selected duplicate specimen and independent test stub; in-process only. |

Source: [core](../src/erp_agent_testbench/core.py), [contracts/utilities](../src/erp_agent_testbench/common.py), [CLI](../src/erp_agent_testbench/cli.py), [behavioral tests](../tests/test_core.py), [CLI tests](../tests/test_cli.py). Runtime selection is recorded in [ADR 0001](decisions/0001-offline-core.md).

## Initial verification (historical)

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

## C04 — Public retry-adapter boundary

This M1/M2 slice advances FR-04, FR-05 and FR-09 without closing their full acceptance gates. Inspection of baseline `dd601c9` found that the controller directly chose both retry keys and invoked the simulator. The [reference adapter and public records](../src/erp_agent_testbench/agent.py) now live separately from the [controller and checkers](../src/erp_agent_testbench/core.py).

The in-process protocol `0.1` invokes `AgentAdapter.run(inputs, tools)`. `AgentInput` contains the public task, initial order, approval, policy and limits. The controller constructs each nested record from an explicit field allowlist; records are frozen and accepted terminal statuses become a tuple. Business identities, amounts and source versions remain visible. Case IDs, template groups, split/seed, expected filenames, mutation controls and disturbance schedules are omitted. The reference module does not import the controller or evaluator.

`AmendmentTools.apply_amendment` accepts an immutable business request and a separate idempotency key. Its immutable response exposes either an unknown outcome with no receipt fields, or the observed operation ID, committed status and order version. The controller withholds the first receipt after committing; the adapter decides to retry from that unknown response and reuses its original key. It requires a matching receipt with an advanced order version before declaring completion. Two unknown responses produce `incomplete`. An incomplete adapter result leaves suites inconclusive even if captured durable state shows an effect; it is neither a pass nor a defect detection.

The controller selects the new-key specimen before invocation. Both specimens receive identical public inputs under the same disturbance schedule; their retry decisions cause the observable difference. `execute(case, adapter=...)` supports a trusted test adapter when mutation kind is `none`. A custom adapter combined with a built-in mutation, or a duplicate-retry mutation targeting another component, is rejected before simulator allocation. This does not add an external adapter/RPC implementation; the existing output flag remains false.

The [boundary tests](../tests/test_agent.py) exercise the reference with public scripted responses and an independent stub against the real simulator. They also cover nested metadata exclusion/rejection, unchanged inputs and suite observations under controller metadata changes, frozen/detached records, unsupported protocol versions, invalid/stale receipts, invalid adapter results, and unknown outcomes. The existing clean/fault oracle assertions and simulator denial, idempotency, arithmetic and budget tests remain enabled. Injected labels are synthetic development-test sentinels, not held-out evidence.

### Initial C04 verification

Run locally on Python **3.12.13**, Darwin, against the C04 working-tree change based on `dd601c9`. No new commit or historical report was created. The baseline suite first passed **18 tests**; after this slice, the commands below produced these results:

| Command | Actual result |
|---|---|
| `.venv/bin/pytest -q` | **45 passed, zero failed**. |
| `.venv/bin/ruff check src tests` | Passed. |
| `.venv/bin/ruff format --check src tests` | Passed; 9 files already formatted. |
| `.venv/bin/python -m erp_agent_testbench run examples/clean-retry.case.json` | Exit 0; two attempts, quantity 13, one commitment totaling 3,000 minor units; all suites pass. |
| `.venv/bin/python -m erp_agent_testbench run examples/duplicate-retry.case.json` | Exit 0; two attempts, quantity 16, two commitments totaling 6,000 minor units; smoke passes, state/hybrid fail. |
| `.venv/bin/python scripts/check_public_docs.py` | Passed: 9 JSON files, 62 relative links and 1 SVG; documentation-only validation. |
| `git diff --check` | Passed. |

These are local component regressions. Clean wheel installation has not been repeated for C04; the earlier wheel verification above applies only to the initial slice. Documentation integrity is checked separately and does not establish application behavior.

### C04 budget exhaustion repair

Review reproduced an FR-11/FR-14 boundary failure: an adapter could catch the third same-key call's budget error, return `completed`, and receive passing suite results after exceeding either two tool calls or six logical ticks. The controller-owned simulator now retains exhaustion for the rest of the execution and refuses subsequent effects. After the adapter returns, `execute` checks that state before accepting any adapter result or invoking the suites. Exhaustion raises `ContractError("execution budget exhausted")`, preserving the existing error path for uncaught budget errors; it produces neither a pass nor a defect finding. Exactly two calls at ticks 5 and 6 remain valid at the corresponding limits.

The existing adapter implementation and initial verification above are preserved. The repair adds paired exact-limit/caught-exhaustion tests for both limits, plus a simulator regression showing that a new-key write at an earlier tick cannot resume an exhausted execution. This is a call/tick budget repair within the trusted in-process boundary; wall-clock enforcement and complete execution error records remain pending.

Verification used Python **3.12.13**, Darwin, on the same uncommitted C04 working tree based on `dd601c9`. The existing suite passed **45 tests** before adding regressions. The targeted command below first produced **3 failed, 2 passed, 41 deselected**, exposing both swallowed errors and the resumed-write boundary. After the implementation repair:

| Command | Actual result |
|---|---|
| `.venv/bin/pytest -q tests/test_agent.py tests/test_core.py -k 'caught_budget_exhaustion or tick_budget_exhaustion'` | **5 passed, 41 deselected**. |
| `.venv/bin/pytest -q` | **50 passed, zero failed**. |
| `.venv/bin/ruff check src tests` | Passed. |
| `.venv/bin/ruff format --check src tests` | Passed; 9 files already formatted. |
| `.venv/bin/python -m erp_agent_testbench run examples/clean-retry.case.json` | Exit 0; two attempts, quantity 13, one commitment totaling 3,000 minor units; all suites pass. |
| `.venv/bin/python -m erp_agent_testbench run examples/duplicate-retry.case.json` | Exit 0; two attempts, quantity 16, two commitments totaling 6,000 minor units; smoke passes, state/hybrid fail. |

Documentation verification after the repair: `.venv/bin/python scripts/check_public_docs.py` passed (9 JSON files, 62 relative links, 1 SVG; documentation only), and `git diff --check` passed. Clean wheel verification has not been repeated for this repair.

### C04 rejected-request budget repair

Follow-up review exposed a gap in the repair above: unknown-order and malformed-field requests were rejected before call accounting and tick enforcement. Two valid same-key calls at ticks 5 and 6 followed by an unknown-order request at tick 7 could still yield passing suites under a two-call or six-tick limit when the adapter caught the rejection. The earlier five regressions exercised valid requests only; their recorded results remain evidence for that narrower boundary.

`Simulator.apply` now counts the call and checks the controller-supplied tick before validating amendment fields or order identity. An over-limit request persists exhaustion and returns the budget error before request validation. The existing post-adapter exhaustion check rejects claimed completion before suites run. Within budget, request validation still returns its original error without business effects, and recovery remains possible; `apply_attempts` now includes these rejected requests.

Eight additional regressions cover both limits: the reported caught unknown-order request and its exact-limit counterpart, plus unknown-order/missing-field rejection accounting, in-budget recovery, and refusal of later writes after exhaustion even at an earlier tick. No existing checks were removed or weakened. Rejected requests still have no event entries in the initial aggregate observation; complete request/error traces, structured execution error records and wall-clock enforcement remain pending. This repairs FR-11/FR-14 handling within the existing M1/M2 component, not the full benchmark.

Verification used Python **3.12.13**, Darwin, on the same uncommitted C04 working tree based on `dd601c9`. The starting suite passed **50 tests**. Before the implementation fix, the targeted command below produced **8 failed, 46 deselected**, exposing uncounted requests and over-budget executions reaching the suites. After the fix:

| Command | Actual result |
|---|---|
| `.venv/bin/pytest -q tests/test_agent.py tests/test_core.py -k 'caught_rejected_request or rejected_requests_consume'` | **8 passed, 46 deselected**. |
| `.venv/bin/pytest -q` | **58 passed, zero failed**. |
| `.venv/bin/ruff check src tests` | Passed. |
| `.venv/bin/ruff format --check src tests` | Passed; 9 files already formatted. |
| `.venv/bin/python -m erp_agent_testbench run examples/clean-retry.case.json` | Exit 0; two attempts, quantity 13, one commitment totaling 3,000 minor units; all suites pass. |
| `.venv/bin/python -m erp_agent_testbench run examples/duplicate-retry.case.json` | Exit 0; two attempts, quantity 16, two commitments totaling 6,000 minor units; smoke passes, state/hybrid fail. |

Documentation verification: `.venv/bin/python scripts/check_public_docs.py` passed (9 JSON files, 62 relative links, 1 SVG; documentation only), and `git diff --check` passed. Clean wheel verification has not been repeated for this follow-up repair. The initial C04 implementation and all earlier verification records remain preserved.

### C04 serialization and tick-overflow budget repair

Further review reproduced two paths missed by the previous repair. After two valid calls, a plain dictionary passed to the adapter tool failed in `asdict()` before reaching simulator accounting. Separately, starting at tick `2**63 - 2` allowed two valid calls but rejected the third tick in integer validation before counting it or persisting exhaustion. Catching either error and claiming completion could reach passing suites despite an exhausted call or tick budget. The earlier verification records above cover their stated cases and remain unchanged.

Both simulator entry points now share accounting before serialization, tick validation or business validation. The adapter bridge passes the request directly to `Simulator.apply_amendment`, which accounts once before converting the dataclass; direct dictionary calls through `Simulator.apply` use the same accounting. Over-limit calls persist exhaustion before raising the existing budget error. A controller tick beyond the supported signed 64-bit range also exhausts execution, even if the configured tick limit is larger. The post-adapter guard still rejects exhaustion before any suite runs. Within budget, serialization errors retain their original exception, consume a call and cause no business effects; subsequent valid calls can recover within the remaining budget.

Twenty-two additional regression cases cover plain dictionaries and failing field serialization under both limits, exact-limit rejection accounting and recovery, exact maximum ticks versus caught overflow with and without a restrictive call cap, and refusal of later writes at an earlier tick after overflow. The existing clean/fault, isolation and budget checks remain enabled. This is a repair to the existing trusted M1/M2 boundary, not completion of the benchmark or an external adapter implementation.

Verification used Python **3.12.13**, Darwin, on the same uncommitted C04 working tree based on `dd601c9`. The starting suite passed **58 tests**. Before the implementation fix, the targeted command below produced **18 failed, 4 passed, 54 deselected**, exposing both bypasses and missing attempt counts. After the fix:

| Command | Actual result |
|---|---|
| `.venv/bin/pytest -q tests/test_agent.py tests/test_core.py -k 'serialization_failure or tick_overflow' --tb=short` | **22 passed, 54 deselected**. |
| `.venv/bin/pytest -q` | **80 passed, zero failed**. |
| `.venv/bin/ruff check src tests` | Passed. |
| `.venv/bin/ruff format --check src tests` | Passed; 9 files already formatted. |
| `.venv/bin/python -m erp_agent_testbench run examples/clean-retry.case.json` | Exit 0; two attempts, quantity 13, one commitment totaling 3,000 minor units; all suites pass. |
| `.venv/bin/python -m erp_agent_testbench run examples/duplicate-retry.case.json` | Exit 0; two attempts, quantity 16, two commitments totaling 6,000 minor units; smoke passes, state/hybrid fail. |

Documentation verification: `.venv/bin/python scripts/check_public_docs.py` passed (9 JSON files, 62 relative links, 1 SVG; documentation only), and `git diff --check` passed. Clean wheel verification has not been repeated for this repair. Rejected requests still lack complete request/error events; structured execution error records, wall-clock enforcement, process isolation and the full workflow/evaluation remain pending.

### C04 receipt-binding of completion claims

A completed result is now accepted only if the controller-owned tool bridge actually delivered a committed receipt for the task operation to the adapter. Previously an adapter could call the tool once (response withheld as unknown, effect durable), never see a receipt, and claim `completed`, receiving passing suites from durable state alone. `execute` now raises `ContractError("completion claimed without receipt")` before suites run. Non-completion claims (for example `incomplete` after an unknown outcome) are unchanged and remain inconclusive. Receipt tracking lives in the controller and is not exposed to the adapter. Limit: this binds the claim to receipt delivery only; it does not verify the adapter's reasoning, and the in-process trust limits below still apply.

Verification used the local `uv run --locked` environment on the working tree based on `db7d82a`. Starting suite: 80 tests. Commands actually run:

| Command | Actual result |
|---|---|
| `uv run --locked pytest -q` | **84 passed, zero failed** (4 new: no-call and one-call completion rejected, two-call counterpart passes, incomplete claim stays inconclusive). |
| `uv run --locked ruff check src tests` | Passed. |
| `uv run --locked ruff format src tests` | Applied formatting to one file; rerun check follows with no remaining diffs. |
| `uv run --locked python scripts/check_public_docs.py` | Passed (9 JSON files, 71 relative links, 3 SVG files; documentation only). |

Clean wheel verification was not repeated for this change.

## Relationship to the full plan

M1, M2 and M4 have partial component evidence; M3 has one seeded duplicate-retry defect only. M5 remains pending. Packaging covers this slice of M6.

The [build plan](03-build-plan.md), [requirements](01-product-requirements.md), [evaluation](04-evaluation.md) and [definition of done](05-definition-of-done.md) remain the release criteria. Planned acceptance registers describe the wider system; partial progress does not replace their full conditions. Documentation checks validate authored artifacts separately from application CI.

## Explicit limits

This controller supports only a lost response after the first commit, with either a stable key or the seeded new-key defect. It deliberately permits the defective specimen to expose inadequate checking. The retry adapter is independently invoked within the same trusted process; frozen records and a narrow tool interface do not contain malicious Python or prevent introspection of process memory. It is not a production ERP adapter or a separately running agent. Initial public snapshots are supplied by the controller; read/status/resume tools, wall-clock/process isolation, durable resume, additional fault families and the held-out benchmark are unimplemented. Wall-time limits are visible but unenforced. Suite observations still use the initial aggregate format, not the complete validated/immutable observation contract proposed in the architecture.

All example records and observations are synthetic. No network integration or external business action exists in this slice. Financial and property results support human review. No customer impact, trained-model quality, production readiness or independent endorsement is established.

## Next implementation steps

1. Extend the public adapter boundary with read/status tools and the complete reference workflow; add a separate-process RPC runner with verified isolation from fixture files, databases and controller memory.
2. Implement wall-time enforcement and durable reset/resume, then add approval, schema and partial-execution defects with valid clean counterparts.
3. Validate the observation/result contracts and complete fault accounting before freezing a comparative benchmark.

For each step, add meaningful failure-case tests, capture actual output, preserve evidence/time/money boundaries, and update this record with the revision and unresolved limitations. Do not mark the full release complete from component test counts.
