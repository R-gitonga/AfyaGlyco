# Sprint 03 Patient Reading Workflow

## Sprint goal

Allow a signed-in patient to record, view, and review fictional glucose readings while enforcing ownership at every patient-facing query.

## Scope and user stories

- As a patient, I can open a mobile-friendly form to record a value, timestamp, and optional context.
- As a patient, I can see my recent readings on my dashboard.
- As a patient, I can view my complete reading history and an individual reading detail page.
- As a patient, I cannot view another patient's reading by changing a URL identifier.
- As a demonstrator, I can show a simple recorded-value visual summary without clinical interpretation.

## Planned tasks

- Add a patient blueprint for dashboard, reading creation, history, and detail routes.
- Add server-side form validation for numeric values, timestamps, and context length.
- Filter every patient reading query through the signed-in user's patient profile.
- Add responsive reading-entry, history, and detail templates.
- Add an accessible recorded-value summary for recent entries.
- Add tests for creation, validation failure, dashboard display, and cross-patient access boundaries.
- Update the README route inventory and system tutorial.

## Design or data-model decisions

- Reading creation always uses the current user's patient profile; the browser does not submit a patient identifier.
- Reading detail uses both the reading ID and current patient profile in the database query. A record outside that scope returns not found.
- The summary shows recorded demo values only. It does not calculate medical ranges, alerts, diagnoses, or treatment recommendations.
- The form accepts a non-negative numeric demo value and does not assume a clinical unit or threshold.

## Completed work

- Added responsive patient dashboard, entry form, history page, and detail page.
- Added patient-scoped create, list, and detail routes.
- Added a recent recorded-value summary with an accessible fallback for empty state.
- Added validation and ownership-boundary tests.
- Documented first-time account setup and all new routes.

## Testing and verification

- Nine tests pass using isolated SQLite data.
- Tailwind CSS must be rebuilt after template changes.
- Verify the patient workflow with a seeded fictional account in the local PostgreSQL environment.

## Open issues or blockers

- Clinicians cannot yet review assigned patient readings through their dashboard.
- Clinician notes are stored in the model but are not yet authored through the interface.

## Carry-over work

- Add clinician assigned-patient list and patient review page in Sprint 4.
- Add clinician-authored feedback notes and patient feedback display.

## Review notes and next steps

The patient can now create and safely view only their own readings. Sprint 4 should reuse the explicit patient-to-clinician assignment and keep clinician queries scoped to assigned profiles.
