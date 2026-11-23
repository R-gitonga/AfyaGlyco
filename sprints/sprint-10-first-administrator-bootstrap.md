# Sprint 10 First-Administrator Bootstrap

## Status

Implemented. The empty-database login flow now exposes a one-time, CSRF-protected administrator setup form. The server creates the first administrator with a hashed password, signs the account in, and rejects later bootstrap attempts.

## Sprint goal

Make a fresh or reset demonstration database self-starting without requiring the seeded demo command to succeed first. Preserve the boundary that this is a fictional academic prototype and not a public account-registration system.

## Scope and user stories

- As a panel demonstrator, I can open the login page on an empty database and see a first-administrator setup link.
- As a demonstrator, I can submit a fictional email, display name, and password to create the first administrator.
- As the system, I expose the setup link and accept the form only while no user exists.
- As the system, I hash the password, assign the administrator role, start a session, and redirect to the role dashboard.
- As an existing user, I cannot reopen or reuse the public bootstrap flow.

## CRUD and authorization contract

- Create: the unauthenticated bootstrap form may create exactly one administrator only when the `users` table is empty. Server-side validation, CSRF protection, password hashing, role assignment, and the empty-table check are required.
- Read: an unauthenticated visitor may read the bootstrap form only while no user exists. The public flow does not expose user records.
- Update: not applicable to bootstrap. Existing administrators use the established administrator account-management routes.
- Delete: not applicable to bootstrap. The prototype does not provide public user deletion, and an empty database after an intentional reset starts a new bootstrap cycle.

The route handler and authentication service both enforce the one-time condition. PostgreSQL requests use a table lock around the check-and-create transaction so concurrent public submissions cannot create multiple first administrators.

## Planned tasks

- Add a validated administrator bootstrap form and responsive template.
- Add a public login-page link that is rendered only when no user exists.
- Add a service-layer create operation with password hashing, role assignment, and one-time enforcement.
- Add route inventory, tutorial, flowchart, and demonstration documentation.
- Add tests for availability, successful creation, password handling, validation failure, and reuse protection.

## Completed work

- Added `/auth/bootstrap-admin` GET and POST routes.
- Added `BootstrapAdminForm` with required fields, password confirmation, and a 12-character minimum password length.
- Added the first-administrator service and PostgreSQL check-and-create lock.
- Added the empty-database link and responsive setup page.
- Updated README routes, setup guidance, sprint roadmap, and system tutorials.
- Added authentication tests covering the happy path and access boundary.

## Testing and verification

- Full Pytest suite passes after implementation.
- Bootstrap tests verify that the first account receives the administrator role and a hashed password.
- Bootstrap tests verify that the link and endpoint disappear after the first account exists.
- Validation tests verify password length and confirmation failure without creating a user.

## Open issues or blockers

- The seed command remains available for repeatable fictional patient, clinician, and administrator accounts.
- No password-reset or email-delivery workflow is added; those remain outside the prototype scope.

## Carry-over work

- None for the bootstrap slice.

## Review notes and next steps

Use the bootstrap link after resetting the Render demonstration database, then create or seed the remaining fictional accounts through the administrator workflow or the documented seed command.
