# 08 — Public release and handoff

The current deliverable is prepared for authorized public GitHub sharing as a documentation blueprint, not an application release. License selection is pending; no code, documentation or synthetic-data license grant is supplied. Do not publish screenshots, badges, pass rates or a working-demo claim until those artifacts actually exist. [Completion gates](05-definition-of-done.md).

## Release checklist

- [ ] Decide code, documentation and synthetic-data licenses; confirm ownership and third-party terms. Do not infer permission from public availability.
- [ ] Verify every public fixture is synthetic; review logs, screenshots, configuration, filenames and version-control history for private material.
- [ ] Confirm `.env`, private/raw datasets, runtime databases and generated working output remain excluded. A `.gitignore` does not remove already tracked content or rotate credentials.
- [ ] Replace future commands with verified commands only after implementation. Preserve the blueprint status on incomplete components.
- [ ] Reproduce from a clean installation with the lockfile and record the environment, hardware, code and artifact hashes.
- [ ] Validate the full case inventory, split groups, mutant audit and evaluator/agent separation.
- [ ] Publish protocol, rule definitions, denominators, false alarms, errors, exclusions and limitations alongside result tables.
- [ ] Separate expected fixture output from measured results; mark every report with its actual execution status.
- [ ] Explain that published held-out cases are thereafter public regression data.
- [ ] Render-check static reports at desktop and narrow widths; inspect escaping, evidence links, keyboard navigation and readable status labels.
- [ ] Include one reference-agent example and one independent adapter demonstration; neither may depend on another repository checkout.
- [ ] Record remaining unsupported ERP operations, concurrency limits and the trusted-adapter boundary.
- [ ] Review claims: no certification, guaranteed production safety, unsupported novelty or unmeasured customer impact.
- [ ] Obtain independent review and record substantive feedback and fixes accurately.

## Proposed release bundle

After implementation, hand off a source archive, resolved license files, lockfile, protocol/rule manifests, original synthetic examples, clean/fault demo, JSON/HTML report, evaluation tables, reproduction instructions and known-limitations note. Approved small report examples may be copied into a deliberately reviewed `release/` directory; routine `artifacts/` output remains ignored. Do not publish an empty results folder as evidence.

An operator handoff should explain installation, adapter setup, local isolation, budgets, execution versus suite exit codes, locating evidence, resetting only a named run, and comparing releases. Include a rollback plan for reverting testbench code/configuration; this is not a promise to reverse business transactions.

## Suggested factual project description

Until implemented: “A documented blueprint for a local ERP-agent testbench covering retries, approvals, schema errors and partial execution. Includes original synthetic fixtures and a proposed evaluation protocol.”

After verified release, replace that sentence with the actual implemented scope and measured result, explicitly naming synthetic data, dataset size, relevant limits and remaining failures. Link the release and report. Do not insert anticipated results into publication drafts.

## Maintenance

Version contracts when fields or semantics change; version the benchmark when cases or labels change. A checker correction requires all affected comparisons to be rerun consistently. Preserve old manifests and explain corrections. Revalidate dependencies and publishing claims on every release. Track issues from actual users without exposing their data.
