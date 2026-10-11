# 03 — Sequenced build plan

**Every command in this document is FUTURE and unimplemented unless it is a standard dependency-tool command. Do not run this as an existing application.** All paths below are relative to the project root. [Tracker](../planning/tasks.csv) provides task-level dependencies and estimates.

Prerequisites: a terminal, an editor, Python 3.12 and uv. Their presence is not assumed. Install uv using its [official installation instructions](https://docs.astral.sh/uv/getting-started/installation/) and verify `uv --version`; record the version used. uv can provision Python 3.12 during the future setup. No dependencies were installed as part of this blueprint.

## A. Establish the contract — T01–T05

Inputs: [requirements](01-product-requirements.md), supplied schemas, clean/fault design examples. Review the operation/approval semantics and decide licenses. Create `pyproject.toml`, a source package, `.python-version` and the `erp-bench` entry point. Preserve existing documentation; do not overwrite it with a project-generator template. Select a small dependency set: JSON Schema validation, pytest and a formatter/linter; use standard-library SQLite and argparse initially.

**Future setup commands after writing the package manifest:**

```sh
uv python pin 3.12
uv add jsonschema
uv add --dev pytest ruff
uv lock
uv sync --frozen
uv run erp-bench --help
```

Expected output: a locked environment and honest CLI help, with unfinished commands explicitly unavailable. Implement schema validation plus cross-record validation; never accept a schema-valid dangling approval reference. Checkpoint A: malformed inputs fail before state creation, and every supplied example validates.

## B. Build one clean execution — T06–T12

Create `storage.py`, `simulator.py`, `observation.py`, adapter contracts and deterministic reference agent. Implement order read, policy/approval read, amendment, operation lookup and resume. Keep source writes transactional within each modeled step. Implement a fresh run directory and database per execution. Add test coverage for normal state transitions, approval expiry, same-key/different-payload conflict and idempotency.

**Future commands after T12:**

```sh
uv run pytest tests/unit tests/integration
uv run erp-bench validate examples/clean-retry.case.json
uv run erp-bench execute --case examples/clean-retry.case.json --agent reference --out artifacts/clean-demo
```

Expected output eventually: `manifest.json`, `observation.json`, `events.jsonl` and a local database under the new output directory. Refuse an existing output directory unless a distinct run ID is provided; never overwrite a prior run silently. The cleaned observation is the only input to suites.

Checkpoint B: one timeout-after-commit followed by a same-key retry yields quantity 13, one committed operation and one commitment. This is a target, not a recorded result.

## C. Expose four defect classes — T13–T18

Create controller-only mutation hooks and disturbance scheduling. First implement response loss independently of retry-key mutation. Then implement approval bypass, schema-coercion/error handling and incomplete-operation success mutants. Give each mutation an explicit activation condition and traceable evidence. Add clean variants where the disturbance occurs but the reference system behaves correctly.

Create the independent subprocess adapter with a benign stub agent. Test protocol-version rejection, tool allowlisting and budgets. A process crash or invalid protocol is an adapter/runner error, not a detection success. Checkpoint C: all four mutants change behavior under at least one reviewed case; clean counterparts satisfy their intended rules. Quarantine equivalent, unreachable and ambiguous mutants.

## D. Implement checking and reports — T19–T26

Build smoke, state and hybrid suites as pure readers of one observation. Define the rule catalog before implementations. Build JSON findings, static HTML and CLI return codes; then add version comparison. Validate render escaping with a synthetic string containing HTML markup.

**Future commands after T26:**

```sh
uv run erp-bench execute --case examples/duplicate-retry.case.json --agent reference --out artifacts/fault-demo
uv run erp-bench check --observation artifacts/fault-demo/observation.json --suite all --out artifacts/fault-checks
uv run erp-bench report --checks artifacts/fault-checks --out artifacts/fault-report.html
uv run erp-bench compare --baseline artifacts/baseline --candidate artifacts/candidate --out artifacts/comparison
```

The case controller applies the specified specimen mutation during execution; suites do not receive it. Expected example: smoke passes, state/hybrid identify duplicate application. `check` returns exit 1 for detected failure; that is an intentional demonstration outcome. `compare` rejects missing or incompatible baseline/candidate manifests with exit 2. The example directories for comparison do not exist today.

Checkpoint D: every finding links to real observation evidence; incomplete observations never become clean passes; compare reports a seeded new failure rather than hiding it in an average.

## E. Freeze and evaluate — T27–T33

Construct 40 development cases; use them to tune rules and limits. A separate reviewer authors or withholds the 120 test executions and oracle files. Freeze code, protocol, group split and budgets first. Run mutant validity checks outside the suites, then capture observations once and evaluate every suite on those identical artifacts.

**Future benchmark commands after T31 and reviewer handoff:**

```sh
uv run erp-bench benchmark --manifest private/heldout/manifest.json --suites smoke,state,hybrid --out artifacts/heldout-run
uv run erp-bench score --run artifacts/heldout-run --oracle private/heldout/oracle.json --out artifacts/heldout-score
uv run erp-bench report --checks artifacts/heldout-run --scores artifacts/heldout-score --out artifacts/heldout-report.html
```

`private/heldout` is a proposed ignored directory, not a supplied dataset. Labels must be inaccessible to agent/suite processes. Benchmark exit 0 means the evaluation pipeline completed, not every specimen was safe; expected faulty specimens are part of its dataset. Pipeline errors return 2. Scoring must retain every assigned case, with invalid/error counts and exclusions explained.

Checkpoint E: exactly 120 eligible executions × three suites = 360 suite evaluations. Do not silently reduce the denominator, rerun a failing case until it passes, or adjust thresholds after seeing test outcomes.

## F. Independent reproduction and release — T34–T38

Generate a reusable CI workflow only after local commands are stable. The CI job installs Python 3.12, synchronizes the lockfile, validates examples, runs meaningful tests and publishes bounded synthetic report artifacts. An acceptance wrapper distinguishes an expected fault fixture from an unexpected regression.

Ask a second person or use a separate clean environment to repeat the deterministic release. Resolve findings, record limitations and choose a release gate outcome. Publish only after the [handoff checklist](08-publication.md), license gate and claim review pass.

**Future release verification:**

```sh
uv sync --frozen
uv run ruff check .
uv run pytest
uv run erp-bench demo --out artifacts/release-demo
```

`demo` must verify the known clean/fault expectations and return 0 only when both match, with a report still showing the fault. It does not treat all agent runs as passing.

Optional T39 adds the local report viewer only after the core release. Its future command is `uv run uvicorn erp_agent_testbench.web:app --host 127.0.0.1 --port 8000`, after adding the dependencies and implementing `web.py`. UI work must not delay an inspectable CLI/static report.

## Resume rules

Select the lowest task whose dependencies are done. Record exact outputs and evidence before changing status. If a requirement changes, update the FR, affected tests, protocol version and task acceptance together. Keep unfinished commands labeled future; do not create placeholder passing tests or fabricated result files to make a milestone appear complete.
