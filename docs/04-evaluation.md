# 04 — Evaluation protocol

Status: proposed protocol `0.1`; no executions, scores or accepted benchmark cases exist yet. The two supplied examples demonstrate contracts and are not a completed dataset.

## Question and comparison unit

Which checking approach detects seeded workflow failures while limiting false alarms and checking work? The study evaluates **check suites applied to observed executions**, not three different agents. Capture each execution once, then give the identical sanitized artifact to all three suites. This removes agent randomness from the primary comparison.

| Suite | Planned checks | Deliberate limitation |
| --- | --- | --- |
| Smoke | Terminal completion, parseable output, expected operation reference and presence of an updated order | Does not establish uniqueness, correct final state or approval ordering. |
| State | Smoke plus record/schema, final quantity, unique intent, commitment consistency and approval binding invariants | May miss a transient violation later hidden by repair. |
| Hybrid | State checks plus ordered tool/approval/retry/partial-completion rules | More checks can increase false positives and work. |

All suites receive the same records, event history and public policy. They choose what to inspect; stronger suites do not receive additional ground truth. All are deterministic in the primary study. Adding an LLM judge would be a separate experiment requiring its own frozen protocol and budget.

## Dataset allocation

| Partition | Duplicate | Approval/policy | Schema | Partial execution | Total |
| --- | --- | --- | --- | --- | --- |
| Development faulty | 5 | 5 | 5 | 5 | 20 |
| Development clean | 5 | 5 | 5 | 5 | 20 |
| Held-out faulty | 15 | 15 | 15 | 15 | 60 |
| Held-out clean | 15 | 15 | 15 | 15 | 60 |

There are 40 development cases and 120 held-out executions. Evaluate each held-out execution with three suites: **360 suite evaluations**, each potentially containing multiple assertions. Do not describe this as 360 independent incidents or 360 individual assertions.

Keep related workflow templates, parameter variants, clean/fault pairs and mutation-family variants in the same partition. Categories may recur across partitions; an instantiated template must not. Save template-group IDs in a controller-only split manifest, check overlaps automatically, and manually inspect structural similarity. Different names or random seeds do not make a reused template independent.

A reviewer holds test fixtures and oracle files outside the agent/suite environment until code and protocol hashes are frozen. Authoring all test labels yourself limits blinding; disclose that if independent review is unavailable. Once held-out cases are published, they become public regression cases; future claims require a new withheld set. Never relabel a publicly seen corpus as unseen.

## Disturbances, mutants and ground truth

A disturbance is a response loss, denial, changed interface or interruption. A mutant is a deliberate defect in the specimen agent/connector, or an explicitly stated system component. A disturbance that is handled correctly is a clean case, even if it produces retries.

For each candidate mutant: prove the trigger executes; run the unmutated counterpart under the same schedule; inspect the resulting behavior; identify the violated rule; and have a reviewer confirm it without using suite predictions. Require an observable defect at the supported interface. Non-triggered, equivalent and ambiguous mutants are quarantined before sealing; preserve counts and reasons. No post-result replacement to improve detection scores.

Clean cases must be independently checked for validity, including successful recovery, legitimate denial/review where the task requires it, and benign schema evolution within the declared contract. The suite must know the public task's accepted terminal statuses. Hidden oracle labels cannot supply that business rule.

## Budgets and fairness

Primary execution caps: 20 tool calls, 100 ticks and 30 wall seconds per specimen. Each suite gets at most 100 evidence reads and five wall seconds. Define one evidence read as one requested snapshot or event object; file reads alone are not the unit. Record actual reads, assertions and elapsed time. Freeze the machine description, environment, concurrency and adapter versions. Use a warm-up outside scored cases and randomize suite order or rotate it deterministically.

Timeout, missing evidence and runner failure are not passes or detections. Report fault detection on all 60 assigned faulty executions and false alarms on all 60 clean executions, alongside coverage and inconclusive/error rates. If eligibility defects are discovered after sealing, show both original-assignment counts and a transparently corrected analysis; rescore all suites consistently.

## Measures

- **Fault detection:** faulty executions with at least one valid failure finding / 60. Also report each class / 15.
- **Clean false-alarm rate:** clean executions with a failure finding / 60. Unsupported findings are not discarded silently.
- **Complete coverage:** evaluations yielding pass/fail with all intended checks complete / 120, per suite. Report incomplete/error cases separately.
- **Localization:** detected faulty executions identifying an oracle-accepted rule and causal evidence / detected faulty executions. Publish the rule-mapping policy before scoring.
- **Checking work:** median/p95 reads, assertions and runtime; execution work is reported separately and identical across suites.
- **Regression rate:** cases that pass in the baseline release and fail in the candidate / cases that passed in baseline with comparable observations. If none pass, rate is undefined. List new critical failures individually; a fixed old failure cannot cancel a new critical failure.

For release comparison, rerun the same frozen scenario set with candidate and baseline agent versions, then apply one frozen suite version. Separate a checker change from an agent change; do not compare unlike protocols. Report lost coverage and newly errored cases as regressions in evidence quality, not successful tests.

Use paired differences between suites and uncertainty clustered by shared template group. Synthetic family balance is a design choice, not an estimate of real defect prevalence. Do not claim precision on live workloads from a 50/50 constructed corpus. Three suites on the same execution are correlated observations.

## Replay, artifacts and optional model runs

Manifests record case hashes, split/group manifest hash, schema/protocol versions, code commit when available, lock hash, adapter and rule versions, seed, schedule, budgets, machine/runtime and artifact hashes. Stable normalized state and verdicts should reproduce; volatile timestamps/run IDs are compared separately.

Store raw observations, predictions and ground truth separately. Scoring joins opaque IDs only after evaluation. An optional model experiment needs a fixed subset, repetitions, model/provider version, prompt hash, token limits and a separate spending cap. It cannot be silently folded into the 360 deterministic suite evaluations.

Negative results are valid outputs. If hybrid checking adds no useful detection or too many alarms, report that finding and preserve the original protocol.
