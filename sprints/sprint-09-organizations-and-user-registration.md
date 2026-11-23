# Sprint 09 Organizations, Clinician Onboarding, and Patient Registers

## Status

Implemented. The organization, clinician-provisioning, patient-register, assignment, profile, migration, test, and documentation changes are in the working tree. Automated verification is complete; one authenticated narrow-phone visual check remains before the sprint can be marked fully released.

## Sprint goal

Add a small organization and account-provisioning workflow so an administrator can register clinics or hospitals and clinicians, while clinicians can build a patient register within their organization. Preserve the existing patient ownership, clinician assignment, and health-record privacy boundaries.

## Why this sprint comes next

The prototype currently has seeded users and a single assigned-clinician relationship, but no user-facing way to establish the organizations or people that make up the demonstration workflow. This sprint should make the existing role model more realistic without becoming a hospital information system, public registration service, or external identity platform.

## Scope and user stories

- As an administrator, I can create, read, update, and deactivate a clinic or hospital record.
- As an administrator, I can register a clinician account and associate it with an active organization.
- As an administrator, I can view clinician account status and organization membership and activate or deactivate the account.
- As an administrator, I can assign or transfer a patient registration between clinicians in the same organization without viewing the patient's health records.
- As a clinician, I can view my patient register.
- As a clinician, I can register a new patient account and assign that patient to my own register.
- As a clinician, I can attach an existing unassigned patient account from my organization to my register.
- As a clinician, I cannot take over a patient already assigned to another clinician or add a patient from another organization.
- As a patient, I can see my own display name, organization, and assigned clinician as read-only profile information.
- As a demonstrator, I can create the organization and accounts needed for a repeatable board walkthrough.

## Business-rules contract and CRUD decision

The complete operation matrix must be added to `app/business_rules.py` before implementation. Hard deletion is intentionally unavailable for identity and organization records once they are referenced; deactivation, unassignment, and transfer are the reversible administrative operations.

| Resource | Patient | Clinician | Administrator |
| --- | --- | --- | --- |
| Organization | Read own organization summary | Read own organization summary | Create, read, update, deactivate |
| Clinician account | No access | Read own account summary | Create, read, update, activate/deactivate |
| Patient registration | Read own registration summary | Create, read, update own register entries | Read and update registration metadata |
| Patient assignment | Read own assignment | Create/read assignment for an unassigned patient in the same organization | Create/read/update assignment and transfer within an organization |

Intentional restrictions:

- Organization, clinician-account, and patient-registration hard delete operations are not applicable after references or records exist. The UI and routes must not expose delete controls; status or assignment changes must be explicit.
- Clinicians may create a new patient registration for their own organization and may attach an existing unassigned patient, but may not override an existing assignment.
- Administrators manage identity, organization, and assignment metadata. They do not receive patient glucose, meal, exercise, medication, note, or report access by default.
- Patients cannot change their organization, assigned clinician, role, or account status from the patient interface.
- Existing health-record permissions remain unchanged after an account or assignment change.

## Proposed data model

Keep the model understandable and avoid a general enterprise directory abstraction:

### `Organization`

- `id`
- `name`
- `organization_type` with controlled values `clinic` and `hospital`
- `is_active`
- `created_at` and `updated_at`

### Organization association

Use an explicit organization foreign key on the records that need the boundary:

- Add nullable `organization_id` to `User` for clinician membership; global administrators may remain unscoped.
- Add non-null `organization_id` to `PatientProfile` for patient registration scope.
- Keep `PatientProfile.assigned_clinician_id` for the current one-clinician assignment model.
- Add foreign keys and indexes, with restrictive behavior for organization deletion.

If implementation reveals that a user must belong to multiple organizations, stop and revise this plan before introducing a membership table. Multi-organization membership is not needed for the first demonstration slice.

### Account provisioning

For the local academic prototype, administrator and clinician registration may set an initial password through a CSRF-protected form. Passwords must be hashed immediately and never displayed, logged, or stored in plaintext. Email invitations, password-reset delivery, and external identity providers remain out of scope.

New patient registration should use the same account boundary. If a temporary onboarding credential is needed for the demonstration, the implementation must clearly label it as local demo setup and should require a password change before ordinary use if that flow can be added without expanding the sprint beyond a safe vertical slice.

## Proposed routes

Finalize exact paths before implementation and update the README route inventory in the same change.

Administrator organization routes:

- `GET /admin/organizations` — list organizations.
- `GET, POST /admin/organizations/new` — display and create an organization.
- `GET, POST /admin/organizations/<organization_id>/edit` — display and update organization metadata.
- `POST /admin/organizations/<organization_id>/status` — activate or deactivate an organization.

Administrator clinician routes:

- `GET /admin/clinicians` — list clinician accounts, statuses, and organizations.
- `GET, POST /admin/clinicians/new` — display and create a clinician account.
- `GET, POST /admin/clinicians/<user_id>/edit` — update clinician display and organization metadata.
- `POST /admin/clinicians/<user_id>/status` — activate or deactivate a clinician account.

Clinician patient-register routes:

- `GET /clinician/patients` — list the signed-in clinician's register.
- `GET, POST /clinician/patients/register` — display and process a new patient registration.
- `GET, POST /clinician/patients/add-existing` — attach an existing unassigned patient in the clinician's organization.
- Existing `/clinician/patients/<patient_id>` review routes remain assignment-scoped.

Patient profile route:

- `GET /patient/profile` — display the patient's own organization and assigned-clinician summary without exposing editable assignment controls.

## Planned tasks

- Add organization constants, account-provisioning constraints, and the full permission matrix to `app/business_rules.py`.
- Add `Organization` and organization foreign keys through a reviewed migration, including a safe data transition for existing seeded records.
- Add server-side forms for organization creation/editing, clinician registration, clinician status, and patient registration/attachment.
- Add administrator organization and clinician management views with CSRF-protected state changes.
- Add clinician patient-register views with same-organization and unassigned-patient checks.
- Add the patient read-only profile summary.
- Preserve administrator denial of health-record routes and existing patient/clinician record authorization.
- Add responsive empty states, validation messages, and navigation links for each role.
- Add tests for every allowed operation, unavailable delete operations, password hashing, organization boundaries, assignment conflicts, account status, and patient privacy.
- Update `README.md`, route inventory, `docs/system-tutorials.md`, seed/demo instructions, and this sprint record.
- Rebuild Tailwind CSS and verify organization, onboarding, register, and profile pages at a narrow phone width.

## Design and safety boundaries

- Store seeded accounts and organizations only.
- Do not add real clinic names, patient identities, emails, or medical information to fixtures or documentation.
- Use server-side role, active-status, organization, and assignment checks; never rely on hidden links or organization selectors alone.
- Do not allow a clinician to view or modify records belonging to another clinician's patient.
- Do not grant administrators health-record or report access merely because they manage users.
- Do not add hospital interoperability, insurance, billing, scheduling, referrals, prescriptions, or clinical workflows.
- Do not send invitation emails or expose passwords outside the local demonstration workflow.
- Keep organization deactivation and assignment transfer reversible and explicit.

## Acceptance criteria

- The business-rules module defines the complete organization, clinician-account, patient-registration, and patient-assignment operation matrix before routes are added.
- An administrator can create, read, update, and deactivate a clinic or hospital.
- An administrator can create and manage a clinician account associated with an active organization.
- Clinician passwords are hashed and are not returned in responses, logs, or templates after submission.
- A clinician can view only their own register and can register a new patient in their organization.
- A clinician can attach an existing unassigned patient in their organization.
- A clinician cannot attach an already-assigned patient or a patient from another organization.
- An administrator can transfer or unassign a patient assignment without receiving health-record content.
- A patient can read their own organization and assigned clinician summary but cannot edit the assignment.
- Inactive organizations cannot receive new clinician or patient registrations; inactive accounts cannot perform protected operations.
- Hard-delete routes are not exposed for referenced organizations, clinician accounts, patient registrations, or assignments.
- Existing health-record ownership and clinician-assignment tests continue to pass.
- The full test suite passes, CSS is rebuilt, all routes are documented, migration behavior is verified, and narrow-phone verification is complete.

## Out of scope

- Public patient self-registration.
- Email invitations, password reset delivery, SMS, or external identity providers.
- Multiple organization memberships for one user.
- Clinician-to-clinician shared care teams or concurrent assignments.
- Bulk import, CSV upload, or directory synchronization.
- Hospital/EHR interoperability, billing, insurance, appointments, referrals, prescriptions, or clinical alerts.
- Hard deletion of accounts or organizations with related records.

## Dependencies and carry-over

- Depends on the existing `User`, `Role`, `PatientProfile`, clinician assignment, authentication, admin status, and centralized business-rule implementations.
- Must preserve Sprint 6 and Sprint 7 ownership and assignment checks and Sprint 8 report authorization.
- Requires a reviewed migration because existing seeded patient and clinician records need an organization association.
- Update `docs/system-tutorials.md` because this sprint adds a major organization relationship and changes account and assignment flows.

## Resolved implementation decisions

- Both new patient registration and attachment of existing unassigned patients are implemented so the clinician register has a complete vertical slice.
- Initial passwords are accepted only through the supervised local demonstration workflow, hashed immediately, and never displayed or returned after submission. Password-change delivery remains out of scope.
- Organization deactivation blocks new clinician registrations, patient registrations, and assignment changes. It does not automatically disable existing member logins or grant access to health records.

## Implementation record

- Added `Organization`, organization-scoped user/profile relationships, timestamps, controlled organization types, and migrations `e8f4a2b6c1d5_organizations_and_user_registration.py` plus corrective `f3a7c9d1e2b4_repair_user_display_name.py`.
- Added centralized organization, clinician-account, patient-registration, and patient-assignment permissions and constraints in `app/business_rules.py`.
- Added administrator organization management, clinician provisioning/status management, and patient assignment transfer/unassignment routes.
- Added clinician patient-register, new patient registration, and existing unassigned-patient attachment routes.
- Added patient read-only profile metadata showing organization and assigned clinician.
- Added responsive templates, navigation links, README route inventory updates, and system-tutorial diagrams/design log updates.
- Added tests covering CRUD decisions, password hashing, organization boundaries, assignment conflicts, admin transfer/unassignment, privacy boundaries, and read-only patient profile access.

## Verification and carry-over

- Targeted Sprint 09 and business-rule tests: 11 passed.
- Migration applied successfully with `e8f4a2b6c1d5 (head)`.
- Full suite: 41 passed in 44.96 seconds.
- Tailwind CSS build: completed successfully.
- Route inventory: verified with Flask route discovery, including all Sprint 09 endpoints.
- Migration head: `f3a7c9d1e2b4`; verified that `users.display_name` now exists.
- `git diff --check`: passed; only normal Git line-ending warnings were reported.
- Narrow-phone visual check: not completed because the available browser session was unauthenticated and the new protected pages require a local demo login. The responsive templates use the existing mobile-first Tailwind patterns and remain ready for that final manual check.

## Review notes and next decision

The organization model and both patient-register entry paths were approved through implementation. Sprint 09 is ready for final verification and commit after the remaining release checks pass.
