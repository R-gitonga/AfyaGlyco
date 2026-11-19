# Instructions for Coding Agents

## Project context

This repository contains an academic capstone prototype called AfyaGlyco. The goal is to demonstrate a patient self-monitoring and clinician-review workflow using fictional or seeded data.

Read `README.md` before making changes. Treat the README as the current product scope unless the user explicitly changes it.

## Virtual environment rule

Always work from the project virtual environment. Create it at `.venv` if it does not exist, activate it before running Python or Flask commands, and install Python dependencies into that environment only. Do not install project packages globally.

PowerShell setup:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

When activation is not persistent across commands, invoke `.venv\Scripts\python.exe` and `.venv\Scripts\flask.exe` explicitly. Keep `.venv/` out of version control.

## Core product boundary

This is a demonstration system, not a clinical product. Do not implement or describe features as if the system can diagnose disease, detect emergencies reliably, prescribe medication, recommend insulin doses, or replace a healthcare professional.

Clinical-looking features must remain within safe prototype boundaries:

- Record data entered by a user.
- Display trends and summaries.
- Store clinician-authored notes.
- Show reminders based on configured demonstration data.
- Use clearly labelled simulated alerts if alerts are needed for a demonstration.

Do not invent medical thresholds or treatment protocols. If a workflow requires clinical rules, keep the rules configurable, label them as demonstration logic, and ask the user for clarification before presenting them as medical guidance.

## Technology decisions

Use the agreed stack unless the user requests a change:

- Python
- Flask
- Jinja2
- PostgreSQL
- SQLAlchemy or Flask-SQLAlchemy
- Alembic or Flask-Migrate
- Flask-Login or an equivalent authentication extension
- Tailwind CSS
- Chart.js where charts are needed
- Pytest

Prefer server-rendered Flask and Jinja pages for the capstone. Do not introduce a separate frontend framework unless there is a clear requirement that cannot be met with the existing approach.

## Development priorities

Implement in this order:

1. Application configuration and environment handling
2. Database connection and migrations
3. User accounts and role-based authorization
4. Patient profiles
5. Patient data-entry workflows
6. Clinician review and feedback
7. Administrator management
8. Charts, reports, seeded data, and polish
9. Automated tests and demonstration documentation

Keep each step runnable. Do not build a large untested feature batch when a smaller vertical slice can be demonstrated first.

## Feature completeness and CRUD

Every feature must define its complete set of applicable Create, Read, Update, and Delete operations before implementation begins. For each operation, document which roles may perform it and enforce that authorization in the route handler and service or query layer.

Implement every allowed operation as part of the feature slice, including its server-side validation, responsive UI, tests, and documentation. If an operation is intentionally not allowed—for example, audit events may be append-only or clinician-authored notes may be immutable—record the restriction, explain the reason, and enforce it explicitly rather than silently omitting it.

## Security and data rules

- Never commit passwords, tokens, API keys, or production connection strings.
- Use environment variables for secrets and database configuration.
- Hash passwords with a well-tested password-hashing library.
- Enforce access control in route handlers and service functions.
- Do not rely on hiding links or buttons as authorization.
- Validate all user input on the server.
- Use ORM queries or parameterized SQL; do not concatenate user input into SQL.
- Protect state-changing requests against CSRF when using browser sessions.
- Use fictional or seeded records only.
- Do not add real health data to fixtures, screenshots, tests, commits, or documentation.

## Data model guidance

The initial model should stay understandable. Likely entities include:

- User
- Role
- PatientProfile
- GlucoseReading
- MealLog
- ExerciseLog
- Medication
- MedicationEvent or Reminder
- ClinicianNote
- AuditEvent, if needed for the demonstration

Use foreign keys, timestamps, and clear ownership relationships. Avoid premature abstractions or a generic health-metrics model until the concrete workflows are working.

## UI guidance

- Make the patient workflow fast and low-friction.
- Use responsive layouts with Tailwind CSS.
- Build every feature mobile-first and keep it responsive at all times. Verify new pages at narrow phone widths before considering the feature complete.
- Avoid horizontal scrolling in normal workflows; make forms, navigation, cards, tables, charts, and validation messages usable on small screens.
- Use touch-friendly controls and responsive layouts that scale up to tablet and desktop widths without creating a separate mobile-only implementation.
- Keep navigation role-specific and obvious.
- Display empty states when a user has no records.
- Show validation errors next to the relevant fields.
- Use charts only when they help a user understand a trend.
- Label seeded or simulated content clearly where confusion is possible.

## Testing expectations

At minimum, tests should cover:

- Successful and failed login
- Password handling
- Role-based route protection
- A patient creating and viewing their own records
- A patient being unable to access another patient's records
- A clinician viewing an assigned patient's records
- A clinician adding feedback
- An administrator managing user status or roles
- Validation failures for invalid or incomplete input

Tests should use isolated test data and must not depend on a developer's personal database.

## Documentation expectations

Update `README.md` when the implemented scope changes. Document setup, environment variables, database initialization, migrations, seed commands, test commands, and the capstone demonstration flow once those commands exist.
Maintain the README's application-route inventory as the project progresses. Whenever an application route is added, changed, or removed, update its method, path, purpose, and access level in the same change.

Maintain `docs/system-tutorials.md` as a living tutorial and system-design reference. It must contain the current user walkthroughs and Mermaid flowcharts for the main data flows, user roles, application interconnections, and conceptual records.

Whenever there is a significant design change, update `docs/system-tutorials.md` in the same change. Significant changes include adding or removing a role or major module, changing a data relationship, changing an authorization boundary, changing a major user flow, or adding an external integration. Update the affected explanations and diagrams, verify that arrows and labels match the implementation, and add an entry to the design-change log.

Keep documentation honest. Do not claim that the system is clinically validated, production-ready, interoperable with hospitals, or proven to improve health outcomes.

## Working style

- Inspect existing files before editing them.
- Make focused changes that are easy to review.
- Preserve user changes and avoid destructive commands.
- Prefer migrations and reversible changes over direct database edits.
- Run targeted tests after each meaningful implementation step.
- Before declaring a feature complete, verify both the happy path and access-control boundaries.
- If a request expands the system into real clinical deployment, pause and ask for a revised scope rather than assuming that authorization.

