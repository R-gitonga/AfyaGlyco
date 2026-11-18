# Sprint 02 Authentication and Access Control

## Sprint goal

Allow fictional seeded users to sign in and reach only the dashboard associated with their assigned role.

## Scope and user stories

- As a fictional patient, I can sign in and reach the patient dashboard.
- As a fictional clinician, I can sign in and reach the clinician dashboard.
- As a fictional administrator, I can sign in and reach the administrator dashboard.
- As an unauthenticated visitor, I am redirected to sign in before accessing protected pages.
- As a signed-in user, I cannot access another role's dashboard.
- As a demonstrator, I can create repeatable fictional accounts with a CLI seed command.

## Planned tasks

- Add Flask-Login user loading and session handling.
- Add CSRF protection for browser forms and state-changing requests.
- Add login and logout routes with generic authentication errors.
- Add server-side role-protection decorators.
- Add fictional patient, clinician, and administrator dashboards.
- Add a `seed-demo` command without committing passwords or real data.
- Update the README route inventory and setup instructions.
- Keep all pages mobile-first and responsive.

## Design or security decisions

- Passwords are stored only as hashes using Werkzeug's password-hashing helpers.
- Demo accounts use `example.test` email addresses and fictional profile data.
- The seed command accepts a local password through `--password` or `DEMO_SEED_PASSWORD`; otherwise it generates a password for newly created accounts and prints it once.
- Role authorization is enforced in route decorators, not only by hiding navigation links.
- Login errors are intentionally generic so the interface does not reveal whether an email exists.

## Completed work

- Added login, logout, session loading, CSRF protection, and role checks.
- Added responsive patient, clinician, and administrator landing pages.
- Added the fictional demo-account seed command.
- Added route inventory and seed/test setup documentation.

## Testing and verification

- Six tests pass, covering model relationships, password hashing, successful login, failed login, role boundaries, and demo seeding.
- Flask route discovery succeeds against the configured PostgreSQL database.
- The initial and core-domain migrations apply successfully to PostgreSQL.

## Open issues or blockers

- The role dashboards do not yet contain glucose entry or clinician-review workflows.
- The administrator page does not yet manage users.

## Carry-over work

- Add patient glucose-reading entry and history in Sprint 3.
- Add patient-specific data loading and the first trend summary.

## Review notes and next steps

The authentication boundary is ready for feature work. The next sprint should connect the patient dashboard to the `GlucoseReading` model while preserving patient ownership checks.
