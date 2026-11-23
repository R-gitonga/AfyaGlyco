# Sprint 06 Business Rules Meal and Exercise CRUD

## Status

Implemented. Manual narrow-phone browser rehearsal remains as presentation follow-up.

## Sprint goal

Extend the patient self-monitoring workflow with concrete meal and exercise records, and close the existing glucose CRUD gap, while making the allowed operations, role permissions, ownership checks, and safety boundaries explicit in one application rules module.

## Why this sprint comes next

The MVP already demonstrates the core patient-to-clinician loop with glucose readings and feedback. Meal and exercise logs add context to that loop without requiring medication decisions, clinical thresholds, device integration, or autonomous interpretation. Defining the rules before adding routes also prevents partial CRUD and duplicated authorization logic.

## Scope and user stories

- As a patient, I can create, read, update, and delete my own meal records.
- As a patient, I can create, read, update, and delete my own exercise records.
- As a patient, I can create, read, update, and delete my own glucose records.
- As a patient, I cannot access or change another patient's meal or exercise records.
- As an assigned clinician, I can read a patient's meal and exercise records.
- As an unassigned clinician, I cannot access another clinician's patient's meal or exercise records.
- As a demonstrator, I can show meal and exercise records as context without the system interpreting them or recommending actions.

## Business-rules contract

`app/business_rules.py` is the authoritative application-level source for this sprint's permissions and shared constraints. Routes and services must call these rules rather than duplicating decisions in templates or feature handlers.

| Resource | Patient | Assigned clinician | Administrator |
| --- | --- | --- | --- |
| Meal log | Create, read, update, delete own records | Read only | No health-record access by default |
| Exercise log | Create, read, update, delete own records | Read only | No health-record access by default |
| Clinician note | Read | Create and read assigned-patient notes | No edit access |

Intentional restrictions:

- Clinician review of meal and exercise records is read-only.
- Clinician notes are append-only in this prototype; patients cannot edit them.
- Administrators manage account status, not clinical record content.
- The system stores and displays entered data but does not calculate calories, nutritional targets, exercise prescriptions, medical scores, diagnoses, alerts, or treatment recommendations.

## Planned data model

Add concrete tables through a reviewed append-only migration:

- `MealLog`: patient, meal type, description, recorded timestamp, created timestamp.
- `ExerciseLog`: patient, activity type, duration in minutes, recorded timestamp, created timestamp.

Both records use explicit foreign keys to `PatientProfile`, timestamps, and clear ownership relationships. Do not introduce a generic health-metrics abstraction in this sprint.

## Planned routes

The route inventory must be updated with every implemented route:

- Patient meal routes under `/patient/meals` for new, collection create/history, detail, edit, and delete.
- Patient exercise routes under `/patient/exercise` for new, collection create/history, detail, edit, and delete.
- Assigned-clinician review remains on `/clinician/patients/<patient_id>` and displays the new records read-only.

## Planned tasks

- Add the central business-rules module and CRUD permission matrix.
- Add `MealLog` and `ExerciseLog` models and an append-only migration.
- Add patient forms with server-side validation and CSRF protection.
- Add patient-scoped create, list, detail, update, and delete views.
- Complete patient-owned update and delete views for glucose readings so the project-wide CRUD rule is true for the existing patient record feature.
- Add assigned-clinician read-only display of the new records.
- Add responsive navigation, empty states, and touch-friendly controls without horizontal scrolling.
- Add tests for every allowed CRUD operation, invalid input, patient ownership, clinician assignment, and forbidden operations.
- Update `README.md`, `docs/system-tutorials.md`, route inventory, and this sprint record.

## Completed work

- Added `app/business_rules.py` as the central permission and shared-constraint module.
- Added `MealLog` and `ExerciseLog` models with an append-only PostgreSQL migration.
- Added patient create, read, update, and delete routes with ownership-scoped queries.
- Completed patient-owned update and delete routes for existing glucose readings.
- Added responsive meal and exercise forms, histories, detail pages, and dashboard summaries.
- Added assigned-clinician read-only meal and exercise sections to patient review.
- Added tests for the CRUD matrix, validation failures, ownership boundaries, and clinician assignment.
- Updated the README route inventory and system tutorial flow/design log.

## Testing and verification

- `.venv\Scripts\python.exe -m pytest -q` — 24 tests pass.
- Tailwind CSS rebuilt successfully with `npm run build:css`.
- PostgreSQL migration `c4f6a1e2b7d3` applied successfully and is the current head.
- Flask route discovery includes all meal and exercise CRUD routes.
- A manual narrow-phone browser rehearsal remains before final presentation sign-off.

## Open issues or blockers

- No implementation blocker remains for this sprint.
- Medication, reminders, reports, and external integrations remain deferred.

## Carry-over work

- Rehearse patient CRUD and clinician read-only review in the browser at narrow phone width.
- Capture demonstration screenshots and evidence for the capstone report.

## Design and safety boundaries

- Store and display entries only.
- Use explicit ownership queries for every patient-facing read, update, and delete.
- Return non-disclosing not-found responses for records outside the signed-in patient's scope or clinician assignment.
- Do not calculate calories, nutritional targets, exercise prescriptions, medical scores, or treatment recommendations.
- Do not infer diagnoses, emergencies, adherence, or health outcomes from meal or exercise data.
- Clinicians can view the records, but the system will not generate clinical conclusions from them.
- Keep patient and clinician pages mobile-first and verify narrow phone layouts before completion.

## Acceptance criteria

- The business-rules module defines the allowed operations and role boundaries for meal and exercise records.
- A patient can create, read, update, and delete a meal entry belonging to that patient profile.
- A patient can create, read, update, and delete an exercise entry belonging to that patient profile.
- A patient can create, read, update, and delete a glucose entry belonging to that patient profile.
- A patient cannot retrieve or mutate another patient's meal or exercise entry by changing a URL identifier.
- An assigned clinician can read the patient's meal and exercise history without mutation controls.
- An unassigned clinician receives the same non-disclosing not-found behavior used by current review routes.
- Invalid or incomplete fields show server-side errors next to the relevant field.
- The full test suite passes, CSS is rebuilt, and all implemented routes are documented.

## Out of scope

- Medication events or reminders
- Medication-dose or insulin recommendations
- Simulated clinical alerts
- Wearable or glucometer integrations
- Automated meal, exercise, or treatment advice
- Reports beyond simple record history

## Dependencies and carry-over

- Depends on the existing `PatientProfile`, `GlucoseReading`, clinician assignment, login, and role-protection implementation.
- Reuse the existing ownership query patterns and responsive form components.
- Update the system tutorials and conceptual record diagram because this sprint changes the implemented data model and patient/clinician flow.

## Review notes and next decision

After this sprint, review the complete CRUD and authorization matrix before beginning medication or reminder work. Sprint 07 should only start after the new routes, tests, documentation, and narrow-layout verification are complete.
