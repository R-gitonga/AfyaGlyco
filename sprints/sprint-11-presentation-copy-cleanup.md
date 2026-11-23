# Sprint 11 Presentation Copy Cleanup

## Status

Implemented. User-facing screens, seed output, README guidance, system tutorials, tests, and sprint notes no longer repeatedly label users, records, organizations, or reminders with synthetic-data wording. The academic-prototype and non-clinical safety boundaries remain explicit.

## Sprint goal

Make the small school-project interface feel natural during a panel demonstration by removing repetitive labels that describe every account or record as synthetic.

## Scope and user stories

- As a panel member, I can read patient, clinician, organization, and administrator screens without repetitive synthetic-record wording.
- As a demonstrator, I can understand that the system is an academic prototype from its concise scope and safety messaging.
- As a maintainer, I can use the README, system tutorial, and sprint notes without inconsistent copy.
- As a developer, I still have explicit guidance to use seeded, synthetic, or non-identifying data and not to present clinical decisions as application capabilities.

## CRUD and authorization contract

This sprint changes presentation copy only. No Create, Read, Update, or Delete operation, route, authorization boundary, data relationship, or validation rule changes. Existing operations and access controls remain authoritative.

## Planned tasks

- Audit application templates, form descriptions, flash messages, seed output, tests, and documentation for repetitive wording.
- Remove the adjective from normal interface copy and use concise terms such as “demo,” “recorded,” or “seeded” where context is useful.
- Retain academic-prototype, sensitive-data, non-identifying-data, and non-clinical safety messages.
- Add a sprint record and verify that the clean-up does not change behavior.

## Completed work

- Cleaned patient, clinician, administrator, organization, reminder, meal, exercise, reading, report, and bootstrap copy.
- Simplified seed command output and form descriptions.
- Updated README walkthroughs, route descriptions, system tutorials, sprint roadmap, and prior sprint prose for consistent terminology.
- Kept clinical disclaimers, prototype scope, seeded/synthetic data requirements, and the instruction not to use real patient information.

## Testing and verification

- Existing automated tests continue to cover behavior and authorization; only descriptive test names and fixture labels were updated where copy changed.
- Search audit confirms the repeated wording is removed from application, README, tutorial, and sprint content; the coding-agent instruction file remains authoritative.
- `git diff --check` must pass before release.

## Open issues or blockers

- None for the copy clean-up.

## Carry-over work

- None.

## Review notes and next steps

Review the deployed pages during the panel rehearsal to confirm that the shorter labels feel clearer at phone and desktop widths.
