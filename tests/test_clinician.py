from datetime import datetime, timezone

from app import create_app, db
from app.models import (
    ClinicianNote,
    ExerciseLog,
    GlucoseReading,
    MealLog,
    PatientProfile,
    Role,
    User,
)


def make_clinician_app():
    app = create_app(
        {
            "TESTING": True,
            "AUTO_MIGRATE": False,
            "WTF_CSRF_ENABLED": False,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
        }
    )

    with app.app_context():
        db.create_all()
        patient_role = Role(name="patient")
        clinician_role = Role(name="clinician")
        patient = User(email="patient@example.test")
        patient.set_password("patient-password")
        patient.roles.append(patient_role)
        assigned_clinician = User(email="clinician@example.test")
        assigned_clinician.set_password("clinician-password")
        assigned_clinician.roles.append(clinician_role)
        other_clinician = User(email="other-clinician@example.test")
        other_clinician.set_password("other-clinician-password")
        other_clinician.roles.append(clinician_role)
        db.session.add_all([patient, assigned_clinician, other_clinician])
        db.session.flush()
        profile = PatientProfile(
            user=patient,
            assigned_clinician=assigned_clinician,
            display_name="Demo Patient",
        )
        db.session.add(profile)
        db.session.flush()
        db.session.add_all(
            [
                GlucoseReading(
                    patient=profile,
                    value_demo=6.4,
                    recorded_at=datetime(2026, 11, 6, 9, 30, tzinfo=timezone.utc),
                    reading_context="Before breakfast",
                ),
                MealLog(
                    patient=profile,
                    meal_type="breakfast",
                    description="clinician-visible meal",
                    recorded_at=datetime(
                        2026, 11, 6, 8, 0, tzinfo=timezone.utc
                    ),
                ),
                ExerciseLog(
                    patient=profile,
                    activity_type="clinician-visible exercise",
                    duration_minutes=25,
                    recorded_at=datetime(
                        2026, 11, 6, 7, 0, tzinfo=timezone.utc
                    ),
                ),
            ]
        )
        db.session.commit()

    return app


def login(client, email, password):
    return client.post(
        "/auth/login",
        data={"email": email, "password": password},
    )


def test_assigned_clinician_can_review_patient_and_add_note():
    app = make_clinician_app()
    client = app.test_client()
    login(client, "clinician@example.test", "clinician-password")

    dashboard = client.get("/clinician")
    assert dashboard.status_code == 200
    assert b"Demo Patient" in dashboard.data

    with app.app_context():
        patient_id = PatientProfile.query.one().id

    review = client.get(f"/clinician/patients/{patient_id}")
    assert review.status_code == 200
    assert b"Before breakfast" in review.data
    assert b"clinician-visible meal" in review.data
    assert b"clinician-visible exercise" in review.data

    response = client.post(
        f"/clinician/patients/{patient_id}/notes",
        data={"note": "Demo follow-up note for the patient."},
    )
    assert response.status_code == 302

    with app.app_context():
        note = ClinicianNote.query.one()
        assert note.author.email == "clinician@example.test"
        assert note.patient.user.email == "patient@example.test"

    patient_client = app.test_client()
    login(patient_client, "patient@example.test", "patient-password")
    patient_dashboard = patient_client.get("/patient")
    assert patient_dashboard.status_code == 200
    assert b"Demo follow-up note for the patient." in patient_dashboard.data


def test_unassigned_clinician_cannot_review_patient():
    app = make_clinician_app()
    with app.app_context():
        patient_id = PatientProfile.query.one().id

    client = app.test_client()
    login(client, "other-clinician@example.test", "other-clinician-password")

    response = client.get(f"/clinician/patients/{patient_id}")

    assert response.status_code == 404


def test_empty_clinician_note_is_rejected():
    app = make_clinician_app()
    with app.app_context():
        patient_id = PatientProfile.query.one().id

    client = app.test_client()
    login(client, "clinician@example.test", "clinician-password")

    response = client.post(
        f"/clinician/patients/{patient_id}/notes",
        data={"note": "   "},
    )

    assert response.status_code == 400
    assert b"Enter a note." in response.data
    with app.app_context():
        assert ClinicianNote.query.count() == 0


def test_unassigned_clinician_cannot_read_meal_or_exercise_records():
    app = make_clinician_app()
    with app.app_context():
        patient = PatientProfile.query.one()
        patient_id = patient.id

    client = app.test_client()
    login(client, "other-clinician@example.test", "other-clinician-password")

    assert client.get(f"/clinician/patients/{patient_id}").status_code == 404
