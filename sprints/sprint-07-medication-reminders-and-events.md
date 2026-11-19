# Sprint 07 Medication Reminders and Events

## Status

Defined for planning only. No Sprint 07 application code, migration, routes, or route-inventory changes are implemented yet.

## Sprint goal

Add a safe, demonstration-only medication workflow in which an assigned clinician configures fictional reminders and a patient records medication events, while keeping dosage decisions and clinical interpretation outside the system boundary.

## Why this sprint comes next

The university project requirements include medication scheduling and adherence-related records. The current prototype already has centralized business rules and complete CRUD patterns for patient self-monitoring data. Sprint 07 can extend those patterns without introducing medication recommendations, automated clinical decisions, or external notification services.

## Scope and user stories

- As an assigned clinician, I can create, read, update, and delete a fictional medication reminder for an assigned patient.
- As an assigned clinician, I cannot configure a reminder for an unassigned patient.
- As a patient, I can read the fictional reminders configured for me.
- As a patient, I can create, read, update, and delete my own medication-event records.
- As an assigned clinician, I can read medication events for an assigned patient.
- As an unassigned clinician, I cannot access another clinician's patient's reminders or medication events.
- As a demonstrator, I can show a reminder and a patient-entered event without the system judging adherence or recommending treatment.

## Business-rules contract

Extend `app/business_rules.py` before adding routes. The permissions must be explicit and tested:

| Resource | Patient | Assigned clinician | Administrator |
| --- | --- | --- | --- |
| Medication reminder | Read own configured reminders | Create, read, update, delete for assigned patient | No health-record access by default |
| Medication event | Create, read, update, delete own events | Read events for assigned patient | No health-record access by default |

Intentional restrictions:

- A reminder is a stored demonstration schedule, not a prescription.
- The first version stores a medication label and schedule description; it does not calculate or recommend a dose.
- Patient events represent what the patient entered. The system does not infer adherence, missed doses, treatment effectiveness, or risk.
- Reminder delivery is displayed in the application only. Email, SMS, push notifications, and background scheduling are out of scope.
- Administrators continue to manage fictional account status rather than clinical content.

## Planned data model

Add concrete tables through a reviewed append-only migration:

- `MedicationReminder`: patient, medication label for demonstration, schedule description, reminder time or schedule text, active status, created timestamp, updated timestamp, and configuring clinician.
- `MedicationEvent`: patient, optional reminder reference, event status, recorded timestamp, created timestamp, and optional patient-entered context.

Use controlled values for event status, such as `recorded`, `skipped`, and `not_recorded`. Do not add dosage, insulin, prescription, diagnosis, or clinical-threshold fields.

## Planned routes

Exact paths must be finalized before implementation and added to the README route inventory. The intended route groups are:

- Patient reminder list and reminder detail under `/patient/reminders`.
- Patient medication-event create, history, detail, edit, and delete routes under `/patient/medication-events`.
- Assigned-clinician reminder create, list, detail, edit, and delete routes, or a focused reminder section on the existing patient review page.
- Assigned-clinician read-only medication-event display on the existing patient review page.

## Planned tasks

- Extend `app/business_rules.py` with reminder and medication-event permissions and field constraints.
- Add models and an append-only migration with explicit patient and clinician foreign keys.
- Add server-side forms and CSRF-protected routes for every allowed CRUD operation.
- Add patient reminder display and medication-event CRUD.
- Add assigned-clinician reminder CRUD and medication-event read-only review.
- Add responsive empty states, field-level validation, and clear demonstration labels.
- Add tests for every allowed operation, invalid input, ownership boundaries, assignment boundaries, and forbidden mutation paths.
- Update `README.md`, `docs/system-tutorials.md`, route inventory, system diagrams, and this sprint record.

## Design and safety boundaries

- Store fictional or seeded records only.
- Use explicit ownership and assignment queries for every operation.
- Return non-disclosing not-found responses for out-of-scope patient records.
- Do not send external notifications or claim that a reminder was delivered outside the application.
- Do not recommend medication, dosage, timing changes, insulin, or treatment plans.
- Do not infer adherence, emergencies, diagnoses, or health outcomes.
- Keep all pages mobile-first and verify narrow phone layouts before completion.

## Acceptance criteria

- The business-rules module defines the reminder and medication-event CRUD matrix before implementation.
- An assigned clinician can create, read, update, and delete a fictional reminder for an assigned patient.
- A patient can read only reminders configured for that patient profile.
- A patient can create, read, update, and delete only their own medication events.
- An assigned clinician can read medication events for the assigned patient without patient mutation controls.
- An unassigned clinician cannot retrieve or mutate another clinician's reminders or medication events.
- Invalid statuses, missing labels, incomplete schedules, and invalid timestamps are rejected server-side.
- No dosage guidance, adherence score, automated alert, or external notification is generated.
- The full test suite passes, CSS is rebuilt, all routes are documented, and narrow-phone verification is complete.

## Out of scope

- Medication-dose or insulin recommendations
- Prescription management
- Drug interaction checking
- Automated adherence scoring or risk interpretation
- Push, SMS, email, or background notifications
- Wearable or glucometer integration
- Clinical alerts or emergency detection
- Reports beyond simple reminder and event history

## Dependencies and carry-over

- Depends on the existing patient profile, clinician assignment, authentication, centralized rules, and CRUD patterns.
- Reuse explicit ownership queries and assigned-clinician review boundaries from Sprint 6.
- Update `docs/system-tutorials.md` in the same change because this sprint adds a new module and changes the patient and clinician data flows.

## Review notes and next decision

Before implementation begins, confirm the exact reminder fields and whether clinician-configured reminders are sufficient for the board demonstration. Keep the first slice application-visible and deterministic; defer external delivery mechanisms and advanced reporting to later work.
