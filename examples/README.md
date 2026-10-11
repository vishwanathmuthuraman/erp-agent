# Synthetic specification examples

These files are **design inputs and expected outcomes**, authored for this blueprint. They have not been executed and are not benchmark results. All identifiers and amounts are fictional.

| Case | Disturbance / specimen | Expected quantity and effects | Expected suites |
| --- | --- | --- | --- |
| [Clean retry](clean-retry.case.json) | Response lost after commit; correct same-key retry | 13; one operation record and commitment | smoke/state/hybrid pass |
| [Duplicate retry](duplicate-retry.case.json) | Same disturbance; retry-key mutation | 16; two operation records and commitments | smoke pass; state/hybrid fail |

Expected details are in [clean expected](clean-retry.expected.json) and [duplicate expected](duplicate-retry.expected.json). The [case schema](../schemas/case.schema.json) and [expected-result schema](../schemas/expected-result.schema.json) define structure. Implemented validation must additionally check cross-record references and scenario semantics.

Initial order quantity is 10, unit price is 1,000 minor USD units and the requested delta is 3. Each application creates an incremental commitment of 3,000 minor units. The approval authorizes that operation once, with an authority limit of 20,000 minor units. The simulator validates payload/approval fields per request but deduplicates only by request key; it deliberately does not enforce business-operation uniqueness. The checker detects duplicated intent independently.

The two files share `example-retry-template-v1` and must remain in the same development partition. `development_example` means they are outside the planned counted dataset until explicitly reviewed/adopted. Never use this public pair as held-out evidence. Runtime observations must replace revealing IDs with opaque tokens and strip mutation, expected-path, split and template metadata before suites receive them.
