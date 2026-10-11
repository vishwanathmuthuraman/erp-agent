# 01 — Product requirements

Status: proposed requirements; none is marked implemented. [Start here](../README.md).

## Problem and end goal

An automation owner sees an agent complete one purchase-order demo. After a lost response the agent repeats the amendment, or it declares success although the order and commitment records disagree. A happy-path demonstration does not establish behavior under those conditions.

Version 1 provides a bounded way to inspect these failures before handover or after a change. A reviewer must be able to connect every reported failure to an observable record, rule and event. Expected demand from implementation firms is a hypothesis; existing simulation and evaluation products overlap with this idea.

## Users and stories

| User | Story | Successful interaction |
| --- | --- | --- |
| Implementation engineer | Connect an existing agent without changing its planning logic. | Adapter conformance passes; the agent uses only simulator tools. |
| Automation owner | Establish the rules a deployment must meet. | A versioned rule manifest identifies each control and its scope. |
| Reviewer | Understand a failed handover test. | Report shows an assertion, expected/observed values and evidence IDs. |
| Maintainer | Detect regressions after a change. | Paired report identifies newly failing rules and improvements separately. |
| Independent reproducer | Re-run a published experiment. | Pinned environment and artifacts reproduce deterministic verdicts. |

## Bounded workflow

Use one synthetic supplier, one currency per case, one order line and integer quantity changes. An agent reads an order and policy, locates a pre-existing approval, submits an amendment, checks completion and returns a status. The simulated ERP records the updated order and a commitment entry. A controlled interruption can occur between those two writes.

Approval refers to the business operation and approved payload; it is not inferred from natural-language enthusiasm. Business operation ID, idempotency key, request hash and transport attempt ID have separate meanings. Reusing an idempotency key returns the prior result; changing it may perform the operation twice. This deliberately models a provider that deduplicates request keys rather than business intent.

In scope: local deterministic simulator, JSON contracts, external-agent adapter, independent reference agent, seeded faults, three check suites, CLI, static report and CI example. Optional after core completion: localhost FastAPI viewer and an explicitly enabled model-backed agent.

Out of scope: real purchasing, payments, ERP certification, production access controls, general ERP emulation, arbitrary user-code sandboxing, unbounded multi-agent workflows and automatic repair of real transactions.

## Functional requirements

| ID | Requirement | Observable acceptance |
| --- | --- | --- |
| FR-01 | Validate cases before execution. | Unknown fields, wrong types and invalid cross-record references fail before any write. |
| FR-02 | Create isolated state per execution. | Two concurrent cases cannot read or change each other's database or artifacts. |
| FR-03 | Support the documented purchase-order state machine. | Clean execution creates one amendment and one matching commitment. |
| FR-04 | Provide an independent adapter contract. | A second stub agent works through the same interface as the reference agent. |
| FR-05 | Supply a deterministic reference agent. | Clean retry reuses its key, checks operation status and completes correctly. |
| FR-06 | Separate disturbances from defective behavior. | A timeout recovered correctly is a clean case; a changed retry key can expose a duplicate. |
| FR-07 | Represent four fault classes. | Each class has a reviewed behavior-changing mutant and a clean counterpart. |
| FR-08 | Produce bounded, ordered observable evidence. | Tool request/response, logical time, state transition and terminal status have stable references. |
| FR-09 | Keep ground truth outside agent and suite inputs. | Fixture label, mutation configuration and expected verdicts are absent from observation bundles. |
| FR-10 | Evaluate smoke, state and hybrid suites. | All receive the same immutable bundle and declared budget; skipped checks remain visible. |
| FR-11 | Distinguish failure, error and incomplete evidence. | Invalid input or runner crashes cannot masquerade as a detected agent defect or pass. |
| FR-12 | Generate JSON and readable reports. | Each finding links rule, evidence, expected value, observed value and severity. |
| FR-13 | Compare candidate and baseline releases. | Only matching case/protocol manifests are paired; new failures appear individually. |
| FR-14 | Enforce execution and checking budgets. | Exceeding wall time/tool calls stops work and returns an explicit incomplete/error record. |
| FR-15 | Run offline by default and reproduce runs. | Reference demo needs no secrets/network; replay preserves substantive verdicts. |
| FR-16 | Support CI and public handoff. | Expected demo failures, unexpected regressions and infrastructure errors have distinct exits. |

## Nonfunctional requirements

Money is signed integer minor units with an explicit currency; no binary floating-point business arithmetic. Case ticks are integers, separate from measured wall time. Validate all JSON at boundaries; reject unrecognized schema versions. Use explicit SQLite transactions and foreign-key enforcement on every connection. Logs contain synthetic tool evidence, not model secrets or hidden reasoning.

Proposed limits: 20 agent tool calls, 100 logical ticks and 30 seconds wall time per execution; 100 evidence reads and five seconds per suite evaluation. These are initial development budgets, not performance measurements. Freeze revisions before held-out evaluation. The model path is disabled by default and requires an explicit provider, model, spend cap and authorization.

## Discovery before commercial extension

Ask implementation engineers for the last escaped retry, approval, schema or partial-write problem; the artifacts they used; time to diagnose; current tools; and who accepts deployment risk. Record negative findings. Access to real data, integrations and paid work is not assumed. Public examples stay synthetic even if discovery informs scenario design.
