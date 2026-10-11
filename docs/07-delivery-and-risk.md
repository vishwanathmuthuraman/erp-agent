# 07 — Delivery, tradeoffs and risk

Status: planning estimates. No commercial validation, implementation or operating costs have been observed. [Task tracker](../planning/tasks.csv).

## Milestones and decisions

| Milestone | Tasks | Exit decision |
| --- | --- | --- |
| M1 Contract | T01–T05 | Semantics, schemas and scope accepted; license decision recorded. |
| M2 Clean slice | T06–T12 | One independently runnable workflow with bounded evidence. |
| M3 Faults/adapters | T13–T18 | Four valid defect classes; external stub uses the same boundary. |
| M4 Suites/report | T19–T26 | Failure explanations and regression comparison inspectable. |
| M5 Evaluation | T27–T33 | Frozen comparison completed with all cases accounted for. |
| M6 Handoff | T34–T38 | Reproduction and publication gates evaluated; optional T39 deferred. |

The tracker totals 147 estimated core hours plus five optional viewer hours. At 15–20 focused hours weekly, core implementation is approximately eight to ten weeks before substantial surprises; six weeks would require about 25 hours weekly plus reviewer availability. Calendar duration is not a promise. Review actual effort weekly. Defer optional UI/model work before reducing core fault coverage. Never shrink a sealed dataset silently to meet a date.

## Decision log to maintain

| ID | Proposed decision | Reason | Revisit trigger |
| --- | --- | --- | --- |
| D-01 | CLI/static report before UI | Faster inspectable end-to-end workflow | Reviewers cannot navigate artifacts. |
| D-02 | SQLite per execution | Simple reproducibility and separation | Real concurrency fidelity becomes an accepted requirement. |
| D-03 | Deterministic primary benchmark | Isolate checking behavior | Explicit model comparison is funded and frozen separately. |
| D-04 | Request-key deduplication only in simulator | Expose repeated business intent under new keys | Target ERP contract differs; create a versioned profile. |
| D-05 | Observable contract rather than vendor replica | Bounds implementation and claims | Partner supplies a documented interface and sandbox. |
| D-06 | License selection pending | Ownership and reuse terms need an explicit decision | Before reusable/public release. |

Append actual decision date, owner, alternatives, evidence and consequences when a decision is accepted. Proposed choices are not decisions already made by a customer.

## Risk register

| Risk and consequence | Control and verification | Residual risk / response |
| --- | --- | --- |
| Suites see fault labels and overstate detection | Allowlisted bundles; leakage canaries and separate scorer | A human author may know the test set; disclose limits. |
| Equivalent mutant inflates/deflates scores | Trigger review and unmutated counterpart before sealing | Model realism still limited; publish exclusions. |
| Simulator is mistaken for a real ERP | Contract table and unsupported behaviors in each report | Require new validation before a partner integration. |
| Duplicate writes from response loss | Separate intent/key IDs; known retry fixtures | Provider behavior varies; do not generalize. |
| Partial writes mislabeled successful | Intermediate state and commitment assertions | No claim of atomicity across external services. |
| Checker flags legitimate denial/recovery | Clean controls and public allowed-status rules | New workflows require new control definitions. |
| Arbitrary adapter accesses secrets/network | Trusted adapter scope, minimal process environment, verified isolation | Version 1 is not a hostile-code sandbox. |
| Public artifacts expose private material | Original synthetic records; no real exports in examples | Review generated logs before release. |
| Checking budgets censor hard cases | Report timeouts/coverage alongside detection | Increase budgets only with a new protocol. |
| Scope expands into a full ERP | One line/currency/workflow; defer UI/model work | A broader product needs a separate scoped plan. |
| Licensing unclear | No invented license; ownership/dependency review gate | Release remains pending until resolved. |
| No buyer benefit beyond existing tools | Inspect concrete handover incidents and alternatives | Keep a bounded research/tooling release. |

Use qualitative likelihood until evidence supports numbers. Each risk links to a consequence, a control, a test and the remaining limitation; a risk score alone is not mitigation.

## Cost model

The deterministic reference path is designed for local execution with zero external model calls. That does not make labor or computing free. Record engineering hours, reviewer hours, machine runtime, storage and any CI charges separately.

Planned primary workload: 120 captured executions plus 360 checking passes. At the caps, capture wall time is 3,600 seconds and checking wall time 1,800 seconds, excluding setup, validation, artifact generation and development work. These are arithmetic upper bounds for serial capped steps, not measured runtimes or a throughput claim.

For optional models: estimated cost equals input tokens × quoted input price plus output tokens × quoted output price, divided by the price unit, plus any tool charges. Record provider/model, price date, currency, retries and an explicit hard spend cap. No provider, subscription, deployment or spending is authorized by this document.

Commercial discovery should measure time to prepare cases, investigate a failure and repeat a release test. Proposed value remains unproven until observed with the intended users. Treat a useful open demonstration, a successful handover and a paying deployment as separate outcomes.
