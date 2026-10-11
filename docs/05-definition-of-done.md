# 05 — Definition of done

**All targets below are pending. No test has been implemented or passed, and no performance target is achieved.** [Evaluation protocol](04-evaluation.md).

## Completion gates

| Gate | Required evidence |
| --- | --- |
| Contract complete | Every example validates; invalid references/types/versions fail before writes; adapter and rule versions documented. |
| Functional slice | Independent reference and stub adapters complete the clean task; clean timeout recovery produces exactly one effect. |
| Fault coverage | Four reviewed development defects yield correct hybrid findings; clean counterparts do not fail; missing evidence cannot pass. |
| Isolation | Fresh state per run; no cross-case reads/writes; oracle/mutation fields absent from adapter/suite inputs; default run makes no external calls. |
| Reproducibility | Separate clean installation repeats normalized deterministic state and suite verdicts for all released examples. |
| Evaluation integrity | 40 development and 120 held-out cases documented; no split-group overlap; 360 suite evaluations with complete denominators and errors. |
| Operational report | Every finding has rule/evidence/value links; report opens locally; injected HTML renders as text; regression view exposes new failures. |
| Public release | Ownership/license decisions resolved; claims match evidence; protocol, reproducible artifacts and limitations available. |

Initial **performance hypotheses** for an acceptance-focused v1: hybrid detects at least 54/60 held-out faulty cases, at least 12/15 per class, with at most 3/60 clean false alarms and zero missing records in the evaluation inventory. A new critical regression blocks release of the affected reference-agent version. Freeze these targets before the test set is opened; they are proposed engineering acceptance thresholds, not validated industry standards.

Missing a performance target does not justify changing labels, removing hard cases or hiding results. Publish a clearly labeled experimental report with unmet targets; keep the acceptance-focused release gate open. A complete honest study and an accepted product release are different states.

## Requirement-to-test plan

Names below designate tests to implement, not existing files or results. All map to future `tests/` modules described in the build plan.

| Requirement | Planned smoke/positive test | Planned fault/negative test | False-positive or boundary check |
| --- | --- | --- | --- |
| FR-01 | `test_valid_case` | `test_invalid_type_rejected` | `test_optional_fields_omitted` |
| FR-02 | `test_fresh_run_state` | `test_cross_run_access_denied` | `test_identical_ids_in_separate_runs` |
| FR-03 | `test_order_commitment_complete` | `test_partial_state_not_complete` | `test_resume_does_not_reapply` |
| FR-04 | `test_stub_adapter_conformance` | `test_unknown_rpc_version` | `test_allowed_review_terminal` |
| FR-05 | `test_reference_clean_retry` | `test_retry_key_mutant` | `test_lost_response_same_key_clean` |
| FR-06–07 | `test_clean_disturbance_controls` | `test_four_mutants_trigger` | `test_equivalent_mutant_quarantined` |
| FR-08–09 | `test_ordered_evidence` | `test_oracle_field_leak` | `test_public_policy_remains_visible` |
| FR-10 | `test_three_suites_same_bundle` | `test_suite_budget_exhaustion` | `test_no_new_evidence_for_hybrid` |
| FR-11 | `test_valid_failure_classification` | `test_runner_crash_is_error` | `test_missing_events_inconclusive` |
| FR-12 | `test_report_evidence_links` | `test_html_payload_escaped` | `test_zero_findings_readable` |
| FR-13 | `test_new_failure_reported` | `test_mismatched_manifests_rejected` | `test_fixed_failure_not_new_regression` |
| FR-14 | `test_within_budget` | `test_wall_timeout_stops_agent` | `test_exact_limit_boundary` |
| FR-15 | `test_offline_demo` | `test_external_destination_rejected` | `test_replay_normalized_state_equal` |
| FR-16 | `test_demo_known_expectations` | `test_unexpected_ci_failure_exit` | `test_expected_fault_is_demo_success` |

## Five-minute demonstration, after implementation

1. State the scope: synthetic one-line purchasing workflow; no production certification.
2. Run the future `erp-bench demo` command from [the build plan](03-build-plan.md). Display the manifest and environment.
3. Open the clean retry: first response is lost, the agent reuses the key, and quantity moves from 10 to 13 once. All three suites should pass.
4. Open the faulty retry: changed key produces quantity 16 and two business effects. Smoke should pass; state/hybrid should fail. Show the exact two records and retry events.
5. Show one case for each remaining fault class and its clean counterpart; distinguish intentionally seeded defects from implementation errors.
6. Open the release comparison; show one newly failing rule and one fixed rule without aggregating them away.
7. End with measured counts, false alarms, incomplete evidence and simulator limitations. Do not substitute expected fixture values for observed output.

Completion evidence goes into the tracker and release notes with artifact paths and hashes. A checked box without supporting output is insufficient.
