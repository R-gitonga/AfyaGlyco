# Sprint Workspace

This folder contains the planning notes, decisions, progress updates, and review notes for each development sprint.

## MVP roadmap

| Sprint | Focus | Demonstrable outcome |
| --- | --- | --- |
| 01 | Application foundation | Core schema for users, roles, patient profiles, clinician assignment, readings, and notes |
| 02 | Authentication and access control | Fictional seeded accounts can sign in and reach only their role-appropriate areas |
| 03 | Patient workflow | A patient can add and review glucose readings on a responsive dashboard with a simple trend |
| 04 | Clinician workflow | An assigned clinician can review a patient and add a note that the patient can see |
| 05 | Administrator and presentation readiness | Demo-user status management, responsive polish, prototype safety messaging, seed preparation, and rehearsal |

Meal, exercise, medication, reminder, report, and external-integration features are post-MVP extensions. Every sprint must preserve the mobile-responsive requirement in `agents.md`.

## Sprint naming

Use one Markdown file per sprint:

```text
sprint-00-foundation.md
sprint-01-application-foundation.md
sprint-02-authentication.md
```

Keep sprint files focused on one delivery period. Update the relevant sprint file as work progresses rather than creating many scattered notes.

## Sprint format

Each sprint should include:

1. Sprint goal
2. Scope and user stories
3. Planned tasks
4. Design or data-model decisions
5. Completed work
6. Testing and verification
7. Open issues or blockers
8. Carry-over work
9. Review notes and next steps

## Sprint rules

- Keep the sprint scope small enough to demonstrate.
- Link significant design changes to `docs/system-tutorials.md`.
- Update the flowcharts when a sprint changes a major user flow, data relationship, module, or authorization boundary.
- Record testing results, not only implementation activity.
- Use fictional or seeded data only.
- Do not describe the capstone prototype as clinically validated or production-ready.

