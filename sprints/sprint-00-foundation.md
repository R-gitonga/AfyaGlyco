# Sprint 00 Foundation

## Sprint goal

Prepare the development environment and establish the initial project design for the academic capstone prototype.

## Completed work

- Created the project README and coding-agent instructions.
- Established the capstone scope and prototype boundaries.
- Created the theoretical system tutorials and Mermaid flowcharts.
- Selected Flask, PostgreSQL, Tailwind CSS, and Chart.js.
- Created the Python virtual-environment workflow.
- Installed the Python dependencies in `.venv`.
- Installed the frontend dependencies with npm.
- Initialized Flask-Migrate.
- Added automatic application of committed migrations at startup.
- Added a basic Flask health-check route.
- Added an initial automated health-check test.
- Added `.env.example` and `.gitignore`.

## Verification

- Python dependencies passed `pip check`.
- Tailwind CSS built successfully.
- npm audit reported no high-severity vulnerabilities.
- The health-check test passed.
- The application reached PostgreSQL during the migration attempt; credential configuration still needs to be corrected in `.env`.

## Open issue

The PostgreSQL server is reachable, but authentication for the configured `postgres` user is currently failing. Confirm the PostgreSQL role password and update the URL-encoded password in `.env` before continuing with database migrations.

## Next sprint candidate

Create the initial application foundation: configuration cleanup, database models, migration workflow, and the first authenticated user roles.

