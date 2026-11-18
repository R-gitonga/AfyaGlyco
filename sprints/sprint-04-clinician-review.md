# Sprint 04 Clinician Review and Feedback

## Sprint goal

Allow a clinician to review only assigned fictional patients, see their recorded values, and add a clinician-authored note that the patient can view.

## Scope and user stories

- As a clinician, I can see the fictional patient profiles assigned to me.
- As an assigned clinician, I can review a patient's recorded readings and previous notes.
- As an assigned clinician, I can add a factual follow-up note for the patient.
- As a patient, I can see clinician-authored notes on my dashboard.
- As an unassigned clinician, I cannot open another clinician's patient review page or add notes to that patient.

## Planned tasks

- Add a clinician blueprint with assigned-patient dashboard and review routes.
- Query patient records only after checking `assigned_clinician_id` against the signed-in clinician.
- Add a CSRF-protected clinician note form with server-side validation.
- Display notes on both the clinician review page and patient dashboard.
- Keep all review and note pages mobile-first and responsive.
- Update the README route inventory, system tutorial, and sprint documentation.

## Design or security decisions

- A patient review lookup filters by both patient ID and the current clinician ID.
- Unauthorized assignment lookups return not found rather than exposing whether another clinician's patient exists.
- Notes are clinician-authored stored text. The system does not generate diagnoses, treatment plans, dosage recommendations, or emergency alerts.
- The patient dashboard displays feedback but does not allow the patient to edit the clinician's note.

## Completed work

- Added assigned-patient clinician dashboard.
- Added patient review page with readings and previous notes.
- Added clinician note creation with CSRF and server-side validation.
- Added patient dashboard feedback display.
- Added responsive empty states and demo-boundary messaging.
- Added tests for assigned review, note creation, patient visibility, unauthorized clinician access, and invalid notes.

## Testing and verification

- Twelve tests pass using isolated SQLite data.
- Tailwind CSS must be rebuilt after template changes.
- Verify the clinician review routes with the configured PostgreSQL database and fictional seeded accounts.

## Open issues or blockers

- Administrator user management is not implemented yet.
- The clinician review currently focuses on glucose readings; meal, exercise, and medication records remain planned extensions.

## Carry-over work

- Add administrator account/status management in Sprint 5.
- Rehearse the end-to-end patient-to-clinician demonstration with deterministic fictional data.

## Review notes and next steps

The first complete patient-to-clinician loop is now available: the patient records a value, the assigned clinician reviews it and adds feedback, and the patient sees the stored note. Sprint 5 should add only the administrator controls and presentation polish needed for the demonstration.
