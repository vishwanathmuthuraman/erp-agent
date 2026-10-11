# Contributing and reviewing

The project is at the specification stage. Useful contributions challenge a requirement, identify a missing failure case, improve a synthetic example, or explain a reproducibility gap.

1. Read the README status, architecture, evaluation protocol and ENGINEERING.md.
2. Describe one bounded issue and the expected behavior. Link its requirement or protocol section.
3. Use original synthetic data. Do not include customer records, private correspondence, credentials, operational logs or copied reports.
4. Preserve deterministic controls and the separation between expected answers and observed runs.
5. Run `python scripts/check_public_docs.py` for documentation changes. Application changes require relevant behavioral tests once an implementation exists.
6. Preserve attribution and explain sources and ownership. License terms are pending; discuss contribution terms before submitting substantial code or external assets.

Do not present a design proposal as a working feature or add outcome claims without matching reproducible evidence. Security-sensitive findings should use an available private reporting channel rather than a public issue containing exploit details or secrets.
