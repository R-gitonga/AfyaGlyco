# Sprint 05 Administrator and Demonstration Readiness

## Sprint goal

Give the administrator a small, safe interface for managing account status and finish the responsive presentation surface for the board demonstration.

## Scope and user stories

- As an administrator, I can view users, their displayed roles, and account status.
- As an administrator, I can activate or deactivate another account.
- As an administrator, I cannot deactivate my own administrator account from the dashboard.
- As a patient, clinician, or administrator, I can navigate to my role area from a responsive navigation bar.
- As a presenter, I can rehearse the patient-to-clinician workflow with seeded accounts.

## Planned tasks

- Add an administrator blueprint and account-status action route.
- Add server-side authorization and CSRF protection to administrator actions.
- Prevent administrator self-lockout.
- Replace placeholder administrator and navigation UI with responsive cards and role links.
- Update the route inventory, administrator flowchart, and demonstration instructions.
- Verify the full application test suite and rebuild responsive CSS.

## Design or security decisions

- The Sprint 5 administrator surface manages account status only; role assignment remains visible but is not editable from this small MVP screen.
- A status action targets a specific user ID and is restricted to administrator-role users.
- Deactivating the current administrator is rejected to preserve access to the demonstration system.
- Only seeded accounts are intended for this workflow.
- The seed command remains the preparation mechanism for demo data; this sprint does not add a destructive reset operation.

## Completed work

- Added administrator user listing with role and active/inactive status.
- Added activate/deactivate action for other accounts.
- Added self-lockout protection and CSRF-protected status forms.
- Added responsive role navigation to the shared layout.
- Updated README routes and system tutorial diagrams.

## Testing and verification

- Fifteen tests pass using isolated SQLite data.
- Tailwind CSS must be rebuilt after template changes.
- PostgreSQL-backed route discovery must include the administrator status route.
- Manual rehearsal should use only the seed accounts.

## Open issues or blockers

- Role assignment editing and a destructive demo-data reset command remain deferred for a later iteration.
- Meal, exercise, medication, and report modules remain post-MVP extensions.

## Carry-over work

- Rehearse and capture the final patient-to-clinician board demonstration.
- Consider adding role assignment management only if the capstone presentation requires it.

## Review notes and next steps

The MVP now has the complete core story: seeded accounts, patient reading entry, assigned clinician review, clinician feedback, and administrator status management. Further work should be driven by presentation feedback rather than adding broad clinical-looking features.
