# 07 — Technical limitations and research risks

This is a proposed local testbench, not an implemented ERP, production certification or demonstrated detection system.

| Limitation | Consequence | Verification or disclosure required |
|---|---|---|
| Narrow simulator contract | A passing case says little about unsupported real ERP behavior. | Publish supported operations and validate each later integration separately. |
| Equivalent or inactive injected defects | A seeded fault may never exercise the intended failure. | Review trigger evidence and unmutated counterparts before freezing cases. |
| Hidden-label leakage | Suites may detect fixture construction instead of behavior. | Separate evaluator truth; test IDs, paths, metadata and response projections. |
| Missing evidence | Absent events can be mistaken for a successful task. | Preserve inconclusive outcomes and distinguish runner errors from agent defects. |
| Retry semantics | A new request key may duplicate the same business action. | Test changed keys and lost responses against the documented operation identity. |
| Trusted external adapters | A local process boundary is not a malicious-code sandbox. | State the trust model and prohibit containment claims the implementation cannot support. |
| Budget censoring | Hard cases may disappear behind time or work limits. | Include timeout and coverage denominators in every comparative report. |
| Synthetic distribution | Balanced fault classes do not estimate production prevalence. | Publish per-class outcomes, false alarms and limits on generalization. |

All suites must inspect the same captured evidence. Additional evidence or hidden oracle access for one suite invalidates the intended comparison. A failing performance hypothesis is publishable; relabeling or omitting difficult cases to claim success is not.

The design uses independent local state and deterministic controls to make failures inspectable. Local reproducibility does not establish cross-service atomicity, hostile-code isolation, legal compliance or customer return on investment.

See [evaluation](04-evaluation.md), [release gates](05-definition-of-done.md) and [publication rules](08-publication.md). Public data remains synthetic; operational exports and private integration details are excluded.
