# ERP Agent Testbench

**Status: documentation blueprint only — application, runner, simulator, tests and measured results are not implemented.** The supplied JSON files are original synthetic design examples with expected outcomes, not execution results. All implementation tasks are `not_started`.

Planned outcome: a local testbench that connects an agent to a simulated purchase-order workflow, introduces controlled failures, and produces a reviewable acceptance/regression report. Its four fault classes are duplicate execution, policy/approval violations, schema mismatches and partial execution.

## Start here

1. Read [requirements](docs/01-product-requirements.md) and [architecture](docs/02-architecture.md).
2. Open [the build plan](docs/03-build-plan.md) and [task tracker](planning/tasks.csv). Begin T01; dependencies determine the next task.
3. Inspect the [clean example](examples/clean-retry.case.json), [faulty example](examples/duplicate-retry.case.json) and their [guide](examples/README.md).
4. Implement the local vertical slice before generating a full benchmark or adding a model provider.
5. Use [evaluation](docs/04-evaluation.md) and [definition of done](docs/05-definition-of-done.md) to decide what can be claimed.

There is no installation or launch command today. Commands in the build plan describe a **future CLI contract** and will fail until its prerequisites are implemented. No API key is needed for the planned deterministic reference agent.

## Documentation map

| Document | Decision it supports |
| --- | --- |
| [01 Requirements](docs/01-product-requirements.md) | Users, scope, stories and functional requirements |
| [02 Architecture](docs/02-architecture.md) | Boundaries, adapter, events, data and report layout |
| [03 Build plan](docs/03-build-plan.md) | Ordered work, files, commands and checkpoints |
| [04 Evaluation](docs/04-evaluation.md) | Dataset, fair comparisons and regression metrics |
| [05 Definition of done](docs/05-definition-of-done.md) | Release gates and requirement-to-test mapping |
| [06 Sources](docs/06-sources-and-design-rationale.md) | Primary evidence versus project inference |
| [07 Delivery and risk](docs/07-delivery-and-risk.md) | Milestones, effort, risks and decisions |
| [08 Publication](docs/08-publication.md) | Review and release handoff |
| [Task tracker](planning/tasks.csv) | Dependencies, outputs and acceptance criteria |

The proposed stack is Python 3.12, uv and SQLite, with a CLI and static HTML report first. A local FastAPI report viewer is optional. This project must work independently: a separate reference agent is included in the planned implementation; no sibling project, live ERP or hosted service is required.

Reports will describe synthetic benchmark performance under specified controls. They will not certify an agent, establish production safety, or imply affiliation with a named ERP vendor. The simulator is a deliberately limited contract implementation.

**License decision pending.** No code, documentation or synthetic-data license grant is supplied, and no third-party reuse rights are asserted. Public sharing of this blueprint is not an application release. Resolve ownership, dependency licenses and attribution before an openly licensed reusable release; these decisions remain pending.
