from datetime import datetime, timezone

from app import create_app, db
from app.models import GlucoseReading, PatientProfile, Role, User


def make_patient_app():
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
        other_patient = User(email="other-patient@example.test")
        other_patient.set_password("other-password")
        other_patient.roles.append(patient_role)
        clinician = User(email="clinician@example.test")
        clinician.set_password("clinician-password")
        clinician.roles.append(clinician_role)
        db.session.add_all([patient, other_patient, clinician])
        db.session.flush()
        db.session.add_all(
            [
                PatientProfile(
                    user=patient,
                    assigned_clinician=clinician,
                    display_name="Demo Patient",
                ),
                PatientProfile(
                    user=other_patient,
                    assigned_clinician=clinician,
                    display_name="Other Demo Patient",
                ),
            ]
        )
        db.session.flush()
        other_reading = GlucoseReading(
            patient=other_patient.patient_profile,
            value_demo=7.25,
            recorded_at=datetime(2026, 11, 6, 8, 0, tzinfo=timezone.utc),
            reading_context="Other patient's demo entry",
        )
        db.session.add(other_reading)
        db.session.commit()

    return app


def login_patient(client):
    return client.post(
        "/auth/login",
        data={"email": "patient@example.test", "password": "patient-password"},
    )


def test_patient_can_create_and_view_own_reading():
    app = make_patient_app()
    client = app.test_client()
    login_patient(client)

    response = client.post(
        "/patient/readings",
        data={
            "value_demo": "6.40",
            "recorded_at": "2026-11-06T09:30",
            "reading_context": "Before breakfast",
        },
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/patient")
    dashboard = client.get("/patient")
    assert dashboard.status_code == 200
    assert b"Before breakfast" in dashboard.data
    assert b"6.4" in dashboard.data

    with app.app_context():
        reading = GlucoseReading.query.filter_by(reading_context="Before breakfast").one()
        assert reading.patient.user.email == "patient@example.test"


def test_invalid_reading_is_rejected_with_field_error():
    app = make_patient_app()
    client = app.test_client()
    login_patient(client)

    response = client.post(
        "/patient/readings",
        data={
            "value_demo": "-1",
            "recorded_at": "2026-11-06T09:30",
            "reading_context": "Invalid demo entry",
        },
    )

    assert response.status_code == 400
    assert b"Number must be at least 0" in response.data


def test_patient_cannot_view_another_patients_reading():
    app = make_patient_app()
    client = app.test_client()
    login_patient(client)

    with app.app_context():
        other_reading = GlucoseReading.query.filter_by(
            reading_context="Other patient's demo entry"
        ).one()
        other_reading_id = other_reading.id

    response = client.get(f"/patient/readings/{other_reading_id}")

    assert response.status_code == 404
    assert b"Other patient's demo entry" not in response.data
