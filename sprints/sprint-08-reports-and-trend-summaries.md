# Sprint 08 Read-only Reports and Trend Summaries

## Status

Implemented. The report aggregation, read-only routes, templates, tests, route inventory, and system documentation are complete. Final full-suite, CSS, migration-state, and narrow-phone verification are recorded below.

## Sprint goal

Turn the existing records into clear, read-only summaries for patients and assigned clinicians. The sprint should improve the board demonstration by making trends and record coverage easier to understand without diagnosing, scoring risk, or recommending treatment.

## Why this sprint comes next

The capstone scope includes basic charts, progress summaries, and reports. AfyaGlyco now has the underlying glucose, meal, exercise, medication-reminder, and medication-event records, along with the authorization contract established in `app/business_rules.py`. A derived reporting slice can use those records without adding another clinical-looking data-entry module or a premature reporting table.

## Scope and user stories

- As a patient, I can view a read-only summary of my own records.
- As an assigned clinician, I can view a read-only summary for an assigned patient.
- As a patient or clinician, I can optionally narrow a summary to a valid recorded-date range.
- As a demonstrator, I can show a simple trend chart and record-count summary without clinical interpretation.
- As an administrator, I cannot view patient health summaries by default.
- As a demonstrator, I can follow a documented report walkthrough using seeded data.

## Business-rules contract and CRUD decision

Reports are derived views, not stored records. Their applicable operation is intentionally read-only:

| Resource | Patient | Assigned clinician | Administrator |
| --- | --- | --- | --- |
| Patient report | Read own derived summary | Read assigned patient's derived summary | No health-record access by default |

Create, update, and delete are not applicable to this feature because the application does not persist a separate report record. This restriction must be explicit in the sprint implementation: expose only GET routes, do not add mutation forms, and enforce the same ownership and assignment checks used by the source records.

The report must display recorded data and transparent aggregates only, such as record counts, date coverage, and a simple value trend. It must not produce a diagnosis, target range, adherence score, emergency signal, risk level, treatment advice, dose guidance, or causal conclusion.

## Proposed derived summary

Keep the first version small and explainable:

- Reading count and date coverage.
- A simple recorded-value trend using the existing glucose readings.
- Meal and exercise record counts for the selected period.
- Medication-event counts grouped by the entered status, without calling the result adherence.
- Reminder count and active/inactive display, without claiming delivery.
- An empty state when the selected period has no records.

Use clearly labelled “recorded demo data” language and show the selected date range. Do not calculate medical averages or thresholds unless the user explicitly approves a safe demonstration rule and it is documented as such.

## Planned data model

No new database table is planned. Build the summary from existing authorized queries against:

- `GlucoseReading`
- `MealLog`
- `ExerciseLog`
- `MedicationReminder`
- `MedicationEvent`

If a reusable query/service layer is introduced, keep it focused on report aggregation and make its authorization contract explicit. Do not create a generic health-metrics abstraction or persist duplicate report data.

## Planned routes

Finalize exact paths before implementation and add them to the README route inventory in the same change:

- `GET /patient/reports` — show the signed-in patient's derived summary with an optional date range.
- `GET /clinician/patients/<patient_id>/reports` — show the assigned patient's derived summary with an optional date range.

These routes are read-only. No POST, PUT, PATCH, or DELETE report routes should be added.

## Planned tasks

- Extend `app/business_rules.py` with the explicit read-only report permission matrix and shared date-range constraints.
- Add a small report aggregation service or query module that accepts an already-authorized patient profile.
- Add patient and assigned-clinician report routes with ownership and assignment enforcement.
- Add responsive report templates with accessible chart fallbacks, summary cards, selected-period labels, and empty states.
- Link patient reports from the patient dashboard and clinician reports from the assigned-patient review page.
- Add tests for patient ownership, clinician assignment, administrator denial, empty periods, valid ranges, invalid ranges, and no mutation routes.
- Rebuild Tailwind CSS and verify report pages at a narrow phone width.
- Update `README.md`, route inventory, `docs/system-tutorials.md`, and the Sprint 8 implementation record after coding begins.
- Add a short demonstration checklist for the capstone report evidence.

## Implementation record

- Added the read-only `patient_report` permission matrix and a maximum 366-day inclusive date-range rule to `app/business_rules.py`.
- Added `app/reporting.py` to derive authorized counts, recorded-value bars, medication-event status counts, reminder counts, and date coverage without persisting duplicate report data.
- Added GET-only patient and assigned-clinician report routes with ownership and assignment checks.
- Added responsive patient and clinician report pages with optional date filters, accessible chart fallbacks, transparent labels, and empty states.
- Linked reports from the patient dashboard and clinician patient-review page.
- Added tests for report aggregation, filtering, empty periods, ownership, clinician assignment, administrator denial, and forbidden mutation methods.
- Updated the README route inventory and system tutorial diagrams and design-change log.

## Verification and carry-over

- Focused report and business-rule tests: 10 passed.
- Full suite: 35 passed.
- Tailwind CSS rebuilt successfully.
- PostgreSQL migration state remains at head `d7e3f9a1b2c4`.
- Flask route discovery includes only GET report routes.
- Narrow-phone browser rehearsal of the report pages remains the final manual presentation check.

## Design and safety boundaries

- Use seeded data only.
- Treat every report as a view over records the current user is already authorized to read.
- Return a non-disclosing not-found response when an unassigned clinician requests another patient's report.
- Do not expose reports to administrators unless a later requirements decision explicitly adds a safe aggregate-only administrator report.
- Do not label counts as adherence, compliance, control, improvement, or risk.
- Do not generate alerts, notifications, diagnoses, prescriptions, dose recommendations, or clinical thresholds.
- Keep filters deterministic, server-validated, timezone-aware, and easy to explain during the board demonstration.

## Acceptance criteria

- The business-rules module defines the read-only report permission matrix before implementation.
- A patient can view a report containing only that patient's authorized records.
- An assigned clinician can view a report for the assigned patient.
- An unassigned clinician cannot retrieve another patient's report.
- An administrator cannot access patient reports by default.
- Valid date ranges filter the displayed summary; invalid or incomplete ranges are rejected with field-level errors.
- The report contains a simple accessible trend and transparent record counts without medical interpretation.
- Empty periods have a clear empty state and do not imply missing care or non-adherence.
- Only GET report routes exist; create, update, and delete are explicitly not applicable and are not silently omitted.
- The full test suite passes, CSS is rebuilt, routes are documented, and narrow-phone verification is complete.

## Out of scope

- PDF or CSV export.
- Scheduled reports or external delivery.
- Provider-wide or administrator-wide patient analytics.
- Clinical thresholds, risk scores, adherence scores, or treatment recommendations.
- New health-record types, device integrations, hospital integrations, or background jobs.
- Persisted report snapshots or audit/reporting warehouses.

## Dependencies and carry-over

- Depends on the Sprint 6 centralized rules and self-monitoring records.
- Depends on the Sprint 7 medication reminder and medication-event records.
- Reuse existing ownership-scoped and assigned-clinician queries.
- Preserve the prototype boundary documented in `agents.md` and `docs/system-tutorials.md`.

## Open questions for implementation

- Confirm whether the board demonstration needs a single patient report page or separate patient and clinician report pages; the proposed routes keep both experiences explicit.
- Confirm whether date-range filtering should default to all recorded demo data or a small recent window. The default should not hide older seeded records unexpectedly.
- Decide whether the existing patient chart should be reused directly or whether a shared chart partial is worthwhile after the first vertical slice is working.

## Review notes and next decision

Approve the read-only derived-report scope before implementation. Once approved, implement one patient report vertical slice first, add the authorization and empty-state tests, then extend the same aggregation to assigned-clinician review.
