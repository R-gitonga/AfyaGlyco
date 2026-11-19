# AfyaGlyco

## Project overview

AfyaGlyco is an academic capstone prototype for Mount Kenya University. It demonstrates how a web application could help patients record diabetes-related self-management information and help healthcare providers review that information in an organized way.

The project is a simulated proof of concept. It is intended for demonstration, assessment, and learning. It is not a clinically validated product, a diagnostic tool, or a replacement for professional medical care.

## Project goal

Build a simple, secure, and responsive web platform that supports:

- Patient self-monitoring
- Clinician review of patient records
- Basic charts and progress summaries
- Medication and follow-up reminders
- Role-based access for patients, doctors, and administrators

The system should make it easy to demonstrate the complete workflow from account creation to patient data entry, clinician review, and administrative management.

## Intended users

### Patient

- Register and sign in
- Maintain a basic profile
- Record fictional glucose readings
- Log meals and physical activity
- Record medication events or view medication reminders
- Review personal history and simple trends
- View clinician feedback

### Doctor or clinician

- Sign in to a clinician dashboard
- View assigned patient profiles
- Review patient entries and trends
- Add feedback or follow-up notes
- View basic summaries and reports

### Administrator

- Manage users
- Assign roles
- Activate or deactivate accounts
- Review basic system activity
- Manage demonstration data and application settings

## Capstone scope

The first version should focus on a small, complete, demonstrable workflow rather than attempting to reproduce a full hospital or electronic health-record system.

### In scope

- Authentication and role-based authorization
- Patient, clinician, and administrator dashboards
- Patient profiles
- Glucose reading records
- Meal records
- Exercise records
- Medication reminders or medication-event records
- Clinician comments and follow-up notes
- Basic charts and summaries
- Seeded demonstration data
- Automated tests for important application behavior

### Out of scope

- Diagnosis or autonomous treatment decisions
- Medication-dose or insulin recommendations
- Automatic interpretation of medical emergencies
- Real patient data
- Integration with hospitals or electronic health-record systems
- Integration with glucometers or wearable devices
- Production deployment or clinical certification
- Claims that the system improves medical outcomes

## Demonstration scenario

The primary demonstration should follow this sequence:

1. Run the seed command to prepare fictional patient, clinician, and administrator accounts.
2. The patient signs in and records several fictional glucose readings.
3. The patient dashboard displays recent entries and a simple recorded-value summary.
4. The assigned clinician signs in and reviews the patient's readings.
5. The clinician adds a clinician-authored feedback note.
6. The patient signs in again and sees the stored feedback.
7. The administrator reviews users and activates or deactivates another fictional account.

This MVP scenario is sufficient to demonstrate the main value of the platform without requiring real-world healthcare integration. Meal and exercise records are now available as additional patient self-monitoring context; medication, reminder, and broader reporting workflows remain post-MVP extensions.

## Technology stack

- Python
- Flask
- Jinja2 templates
- PostgreSQL
- SQLAlchemy or Flask-SQLAlchemy
- Alembic or Flask-Migrate
- Flask-Login or an equivalent authentication extension
- Tailwind CSS
- Chart.js for visual summaries
- Pytest

The project also includes a local Python virtual environment workflow and an npm-based Tailwind CSS build. PostgreSQL configuration belongs in a local `.env` file; use `.env.example` as the template.

Flask will provide the web application and request handling. Jinja templates will render server-side pages. PostgreSQL will store the application records. Tailwind CSS will provide responsive styling, and Chart.js will display simple trends.

The project does not require React, Vue, Laravel, Livewire, or a separate mobile application for the capstone prototype.

## Application routes

This is the living route inventory. Update it whenever an application route is added, changed, or removed. Framework-generated static-file routes are not listed here.

| Method | Path | Purpose | Access |
| --- | --- | --- | --- |
| GET | `/` | Redirect to sign-in or the signed-in user's role dashboard | Public / authenticated |
| GET | `/health` | Confirm that the AfyaGlyco service is running | Public |
| GET | `/auth/login` | Display the sign-in form | Public |
| POST | `/auth/login` | Authenticate a fictional user and start a session | Public |
| POST | `/auth/logout` | End the current session | Authenticated |
| GET | `/dashboard` | Redirect to the current user's role dashboard | Authenticated |
| GET | `/patient` | Display the patient landing dashboard | Patient role |
| GET | `/patient/readings/new` | Display the patient reading-entry form | Patient role |
| POST | `/patient/readings` | Validate and store a reading for the signed-in patient | Patient role |
| GET | `/patient/readings` | Display the signed-in patient's reading history | Patient role |
| GET | `/patient/readings/<reading_id>` | Display one reading when it belongs to the signed-in patient | Patient role |
| GET, POST | `/patient/readings/<reading_id>/edit` | Display and process edits for the signed-in patient's reading | Patient role |
| POST | `/patient/readings/<reading_id>/delete` | Delete the signed-in patient's reading after CSRF validation | Patient role |
| GET | `/patient/meals/new` | Display the meal-entry form | Patient role |
| POST | `/patient/meals` | Validate and store a meal for the signed-in patient | Patient role |
| GET | `/patient/meals` | Display the signed-in patient's meal history | Patient role |
| GET | `/patient/meals/<meal_id>` | Display one meal when it belongs to the signed-in patient | Patient role |
| GET, POST | `/patient/meals/<meal_id>/edit` | Display and process edits for the signed-in patient's meal | Patient role |
| POST | `/patient/meals/<meal_id>/delete` | Delete the signed-in patient's meal after CSRF validation | Patient role |
| GET | `/patient/exercise/new` | Display the exercise-entry form | Patient role |
| POST | `/patient/exercise` | Validate and store an exercise entry for the signed-in patient | Patient role |
| GET | `/patient/exercise` | Display the signed-in patient's exercise history | Patient role |
| GET | `/patient/exercise/<exercise_id>` | Display one exercise entry when it belongs to the signed-in patient | Patient role |
| GET, POST | `/patient/exercise/<exercise_id>/edit` | Display and process edits for the signed-in patient's exercise entry | Patient role |
| POST | `/patient/exercise/<exercise_id>/delete` | Delete the signed-in patient's exercise entry after CSRF validation | Patient role |
| GET | `/clinician` | Display patients assigned to the signed-in clinician | Clinician role |
| GET | `/clinician/patients/<patient_id>` | Review readings and notes for an assigned patient | Assigned clinician |
| POST | `/clinician/patients/<patient_id>/notes` | Store a clinician-authored note for an assigned patient | Assigned clinician |
| GET | `/admin` | Display fictional users, roles, and account statuses | Administrator role |
| POST | `/admin/users/<user_id>/status` | Activate or deactivate another fictional account | Administrator role |

## Suggested application areas

```text
app/
  __init__.py
  business_rules.py
  auth/
  admin/
  patient/
  clinician/
  models/
  templates/
  static/
  services/
  forms/
migrations/
tests/
seed/
config.py
run.py
requirements.txt
```

The exact structure may change as implementation begins, but related functionality should remain separated and easy to test.

## Data and privacy boundaries

All development and demonstration records must be fictional, seeded, or otherwise non-identifying. Do not add real patient names, contact details, medical histories, or photographs to the repository.

The interface should clearly identify the application as an academic prototype. Health-related information displayed by the system should be treated as sensitive even when it is fictional. Secrets, database passwords, API keys, and local environment files must not be committed.

## Quality expectations

- Keep the main user flows simple and easy to demonstrate.
- Validate user input on the server.
- Hash passwords; never store plaintext passwords.
- Enforce authorization on the server, not only in the user interface.
- Use migrations for database changes.
- Add tests for authentication, authorization, record creation, and access boundaries.
- Keep sample data deterministic so demonstrations are repeatable.
- Avoid unsupported medical claims or clinical advice in the application.
- Prefer clear, maintainable code over unnecessary framework complexity.

## Project status

Project documentation, the Flask foundation, migrations, authentication, role protection, patient glucose-reading workflow, meal and exercise CRUD workflows, assigned-clinician review workflow, and basic administrator status management are in place. Medication, reminders, and broader reporting features remain post-MVP extensions.

## Project documentation

- [System tutorials and flowcharts](docs/system-tutorials.md)
- [Instructions for coding agents](agents.md)
- [Sprint workspace](sprints/README.md)

## Local setup

### 1. Create and activate the virtual environment

PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

# Run this in Powershell once if it blocks activation.
  ```open powershell command prompt
    Run
      Set-ExecutionPolicy -Scope CurrentUser RemoteSigned ```

The project should always be worked on from this virtual environment. If activation is not persistent, use `.venv\Scripts\python.exe` for Python commands.

### 2. Install frontend dependencies

```powershell
npm install
npm run build:css
```

Use `npm run build:css:watch` while developing styles.

### 3. Configure PostgreSQL

Copy `.env.example` to `.env` and set `DATABASE_URL` to the PostgreSQL database created in PgAdmin. Do not commit `.env`.

Example format:

```text
DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/diabetes_self_monitoring
```

### 4. First-time demo account setup

There is no public registration page yet. The first-time setup creates fictional patient, clinician, and administrator accounts through the seed command. Set `DEMO_SEED_PASSWORD` in the local `.env`, or pass `--password`; if neither is provided for new accounts, the command generates and prints a random password.

```powershell
flask --app run:app seed-demo --password "choose-a-local-demo-password"
```

The command creates `patient@example.test`, `clinician@example.test`, and `admin@example.test`. After starting the app, open `http://127.0.0.1:5000/auth/login` and sign in with one of those fictional accounts.

Do not commit the password or place real personal information in the seed data.

### 5. Run the application

```powershell
flask --app run:app run --debug
```

When `AUTO_MIGRATE=1`, the application applies committed migrations automatically during startup. For a deliberate schema change, create and review a migration first:

```powershell
flask --app run:app db migrate -m "describe the schema change"
flask --app run:app db upgrade
```

The application will also apply the committed migration automatically the next time it starts.

### 6. Run tests

```powershell
.venv\Scripts\python.exe -m pytest -q
```

