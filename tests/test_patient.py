from datetime import datetime, timezone

from app import create_app, db
from app.models import ExerciseLog, GlucoseReading, MealLog, PatientProfile, Role, User


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


def test_patient_has_complete_crud_for_own_reading():
    app = make_patient_app()
    client = app.test_client()
    login_patient(client)
    assert client.get("/patient/readings/new").status_code == 200

    create_response = client.post(
        "/patient/readings",
        data={
            "value_demo": "6.40",
            "recorded_at": "2026-11-06T09:30",
            "reading_context": "Before breakfast",
        },
    )
    assert create_response.status_code == 302

    with app.app_context():
        reading = GlucoseReading.query.filter_by(
            reading_context="Before breakfast"
        ).one()
        reading_id = reading.id

    update_response = client.post(
        f"/patient/readings/{reading_id}/edit",
        data={
            "value_demo": "7.10",
            "recorded_at": "2026-11-06T10:00",
            "reading_context": "Updated demo context",
        },
    )
    assert update_response.status_code == 302
    assert b"Updated demo context" in client.get(
        f"/patient/readings/{reading_id}"
    ).data

    delete_response = client.post(f"/patient/readings/{reading_id}/delete")
    assert delete_response.status_code == 302
    with app.app_context():
        assert db.session.get(GlucoseReading, reading_id) is None


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
    assert client.post(
        f"/patient/readings/{other_reading_id}/delete"
    ).status_code == 404


def test_patient_has_complete_crud_for_own_meal():
    app = make_patient_app()
    client = app.test_client()
    login_patient(client)
    assert client.get("/patient/meals/new").status_code == 200

    create_response = client.post(
        "/patient/meals",
        data={
            "meal_type": "breakfast",
            "description": "breakfast entry",
            "recorded_at": "2026-11-06T08:00",
        },
    )
    assert create_response.status_code == 302

    with app.app_context():
        meal = MealLog.query.one()
        meal_id = meal.id
        assert meal.patient.user.email == "patient@example.test"

    detail = client.get(f"/patient/meals/{meal_id}")
    assert detail.status_code == 200
    assert b"breakfast entry" in detail.data

    update_response = client.post(
        f"/patient/meals/{meal_id}/edit",
        data={
            "meal_type": "lunch",
            "description": "Updated lunch entry",
            "recorded_at": "2026-11-06T12:00",
        },
    )
    assert update_response.status_code == 302
    assert b"Updated lunch entry" in client.get(
        f"/patient/meals/{meal_id}"
    ).data

    delete_response = client.post(f"/patient/meals/{meal_id}/delete")
    assert delete_response.status_code == 302
    with app.app_context():
        assert db.session.get(MealLog, meal_id) is None


def test_patient_has_complete_crud_for_own_exercise():
    app = make_patient_app()
    client = app.test_client()
    login_patient(client)
    assert client.get("/patient/exercise/new").status_code == 200

    create_response = client.post(
        "/patient/exercise",
        data={
            "activity_type": "walking",
            "duration_minutes": "30",
            "recorded_at": "2026-11-06T17:00",
        },
    )
    assert create_response.status_code == 302

    with app.app_context():
        exercise = ExerciseLog.query.one()
        exercise_id = exercise.id

    detail = client.get(f"/patient/exercise/{exercise_id}")
    assert detail.status_code == 200
    assert b"walking" in detail.data

    update_response = client.post(
        f"/patient/exercise/{exercise_id}/edit",
        data={
            "activity_type": "Updated cycling",
            "duration_minutes": "45",
            "recorded_at": "2026-11-06T18:00",
        },
    )
    assert update_response.status_code == 302
    assert b"Updated cycling" in client.get(
        f"/patient/exercise/{exercise_id}"
    ).data

    delete_response = client.post(f"/patient/exercise/{exercise_id}/delete")
    assert delete_response.status_code == 302
    with app.app_context():
        assert db.session.get(ExerciseLog, exercise_id) is None


def test_invalid_meal_and_exercise_inputs_are_rejected():
    app = make_patient_app()
    client = app.test_client()
    login_patient(client)

    invalid_meal = client.post(
        "/patient/meals",
        data={
            "meal_type": "breakfast",
            "description": "   ",
            "recorded_at": "2026-11-06T08:00",
        },
    )
    assert invalid_meal.status_code == 400
    assert b"Meal description" in invalid_meal.data

    invalid_exercise = client.post(
        "/patient/exercise",
        data={
            "activity_type": "Walking",
            "duration_minutes": "0",
            "recorded_at": "2026-11-06T17:00",
        },
    )
    assert invalid_exercise.status_code == 400
    assert b"between 1 and 1440" in invalid_exercise.data


def test_patient_cannot_access_another_patients_meal_or_exercise():
    app = make_patient_app()
    with app.app_context():
        other_profile = PatientProfile.query.filter_by(
            display_name="Other Demo Patient"
        ).one()
        meal = MealLog(
            patient=other_profile,
            meal_type="dinner",
            description="Other patient's meal",
            recorded_at=datetime(2026, 11, 6, 19, 0, tzinfo=timezone.utc),
        )
        exercise = ExerciseLog(
            patient=other_profile,
            activity_type="Other patient's exercise",
            duration_minutes=20,
            recorded_at=datetime(2026, 11, 6, 18, 0, tzinfo=timezone.utc),
        )
        db.session.add_all([meal, exercise])
        db.session.commit()
        meal_id = meal.id
        exercise_id = exercise.id

    client = app.test_client()
    login_patient(client)

    assert client.get(f"/patient/meals/{meal_id}").status_code == 404
    assert client.get(f"/patient/exercise/{exercise_id}").status_code == 404
    assert client.post(
        f"/patient/meals/{meal_id}/edit",
        data={
            "meal_type": "lunch",
            "description": "Attempted update",
            "recorded_at": "2026-11-06T12:00",
        },
    ).status_code == 404
    assert client.post(f"/patient/exercise/{exercise_id}/delete").status_code == 404
