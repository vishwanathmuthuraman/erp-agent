# Repository working instructions

Read README.md, ENGINEERING.md, requirements, architecture, evaluation and definition of done before changing behavior. This repository currently contains research specifications, synthetic examples and documentation tooling; application implementation is pending.

1. Follow public milestones in docs/03-build-plan.md. Detailed internal delivery planning is maintained separately; do not republish it.
2. Preserve requirement identifiers, contracts, exact financial arithmetic, state rules and evaluation semantics. Record deliberate architecture changes before revising those boundaries.
3. Implement one bounded behavior and record actual test evidence. Never turn planned work or expected scenario output into a completed result.
4. Keep identity, permissions, money, approval binding and external effects deterministic. Optional model output is untrusted proposed input.
5. Preserve organization boundaries, source versions, idempotency, explicit unknown outcomes and human review where relevant.
6. Keep development examples separate from held-out cases. Do not expose expected labels, future facts or evaluator state to the system under test.
7. Keep public changes scoped to synthetic research artifacts. Credentials, private affiliations, customer records, delivery estimates and commercial plans remain outside the public tree.
8. Use the configured personal maintainer identity; preserve genuine human attribution and required source notices. Do not add assistant branding or automated assistant coauthor credits. Do not fabricate manual authorship, measured results, awards or endorsements.
9. Run scripts/check_public_docs.py for documentation changes and the affected behavioral checks once application code exists. Documentation validation is not an application test.
10. Follow docs/08-publication.md. A future architecture does not authorize connecting production systems, sending messages, financial actions, deployment or unrelated publication.

Markdown is the editable source of truth. Existing public Git history remains historical evidence; normal file deletion does not erase prior access. License selection is pending.
