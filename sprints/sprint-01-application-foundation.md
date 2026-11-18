# Sprint 01 Application Foundation

## Sprint goal

Create the core database schema needed for the first demonstrable patient-to-clinician workflow while keeping the data model small and understandable.

## Sprint sequence

1. Core domain models and migration — current sprint
2. Authentication, seeded accounts, and role protection
3. Patient dashboard and glucose-reading entry
4. Clinician review and feedback notes
5. Responsive presentation polish, administrator view, and demo rehearsal

## Scope and user stories

- As a patient, my account can have one patient profile.
- As a patient, I can have fictional glucose readings associated with my profile.
- As a clinician, I can be assigned to a patient profile.
- As a clinician, I can author a note associated with an assigned patient.
- As an administrator, roles can be assigned to users in the demonstration data model.

## Planned tasks

- Add SQLAlchemy models for users, roles, role assignments, patient profiles, glucose readings, and clinician notes.
- Add explicit patient-to-clinician assignment to support authorization in later sprints.
- Create a reversible Alembic migration for the core schema.
- Add model relationship and password-hashing tests using isolated SQLite test data.
- Keep all future pages mobile-first and responsive under the project agent instructions.

## Design or data-model decisions

- A patient profile belongs to one user and may be assigned to one clinician for the first MVP.
- A user may have multiple roles through a role-assignment table.
- Glucose readings store recorded demo values and timestamps; the database does not interpret them or apply clinical thresholds.
- Clinician notes store clinician-authored text and do not generate treatment instructions.
- Meal, exercise, medication, reminder, audit, and report records are deferred until the core loop works.

## Completed work

- Added the six core tables and their relationships.
- Added a second migration after the existing placeholder migration so the migration history remains append-only.
- Added isolated model coverage for relationships and password hashing.
- Added the mobile-responsiveness rule to `agents.md`.

## Testing and verification

- Run `.venv\Scripts\python.exe -m pytest -q`.
- Run the migration upgrade against the configured local database before the next sprint.
- Confirm the schema can be downgraded and upgraded in a disposable development database.

## Open issues or blockers

- Authentication routes and authorization checks are not implemented yet.

## Carry-over work

- Add the Flask-Login user loader and login/logout routes.
- Add role-protected route helpers.
- Add deterministic fictional seed commands.

## Review notes and next steps

The model is intentionally narrower than the full README scope. The next sprint should use this schema to establish a repeatable login and seeded-account workflow before adding more record types.
