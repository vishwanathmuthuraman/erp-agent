# Project working instructions

This repository currently contains a build blueprint, data contracts and original synthetic examples. Read README.md and docs/01-product-requirements.md through docs/05-definition-of-done.md before implementing application behavior. The application is not implemented yet; proposed commands are not evidence that it runs.

## Implementation workflow

1. Find the task tracker linked from README.md. Work on the earliest task whose dependencies are complete.
2. Preserve functional requirement IDs, data contracts and evaluation definitions. Document any necessary design change and its consequences before revising a contract.
3. Implement a bounded task and verify the acceptance behavior described in the build plan. Record actual evidence and actual status in the tracker.
4. Use deterministic calculations and state rules for consequential decisions. Optional AI output must remain subject to validation, evidence checks and explicit failure handling.
5. Keep development cases separate from held-out evaluation cases. Do not tune on held-out outcomes or expose expected labels to the system being evaluated.
6. Distinguish documentation validation, implementation tests and measured benchmark results. Never fill a results table with invented runs or mark work complete because a document describes it.
7. Follow docs/08-publication.md before release. A valid negative experiment can be reported honestly even if a stronger product-performance target is unmet.

## Public repository boundary

Use original synthetic data and authorized public sources. Keep credentials, customer records, private affiliations, interview notes, commercial plans and private working directories outside the repository. Briefly paraphrase and link public research; do not copy reports or claim source authors endorse this project. License decisions remain pending until explicitly recorded.

Do not add remote integrations, send messages, make financial changes, publish a release or upload data merely because a future architecture describes those actions. Use only the current task's authorized scope.

## Documentation

The Markdown files are the editable source of truth. BLUEPRINT.html is an offline reading snapshot. Update its content when the underlying specification changes. Keep all actual source links relative and valid; use code formatting for paths to planned files that do not exist yet.
