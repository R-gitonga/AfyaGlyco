from datetime import datetime, timezone

from app import create_app, db
from app.models import (
    ExerciseLog,
    GlucoseReading,
    MealLog,
    MedicationEvent,
    MedicationReminder,
    PatientProfile,
    Role,
    User,
)
from app.reporting import build_patient_report


def make_report_app():
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
        administrator_role = Role(name="administrator")
        patient = User(email="patient@example.test")
        patient.set_password("patient-password")
        patient.roles.append(patient_role)
        other_patient = User(email="other-patient@example.test")
        other_patient.set_password("other-password")
        other_patient.roles.append(patient_role)
        clinician = User(email="clinician@example.test")
        clinician.set_password("clinician-password")
        clinician.roles.append(clinician_role)
        other_clinician = User(email="other-clinician@example.test")
        other_clinician.set_password("other-clinician-password")
        other_clinician.roles.append(clinician_role)
        administrator = User(email="admin@example.test")
        administrator.set_password("admin-password")
        administrator.roles.append(administrator_role)
        db.session.add_all(
            [patient, other_patient, clinician, other_clinician, administrator]
        )
        db.session.flush()
        profile = PatientProfile(
            user=patient,
            assigned_clinician=clinician,
            display_name="Demo Patient",
        )
        other_profile = PatientProfile(
            user=other_patient,
            assigned_clinician=other_clinician,
            display_name="Other Demo Patient",
        )
        db.session.add_all([profile, other_profile])
        db.session.flush()
        reminder = MedicationReminder(
            patient=profile,
            configuring_clinician=clinician,
            medication_label_demo="Demo reminder",
            schedule_description="Fictional morning schedule",
        )
        db.session.add_all(
            [
                GlucoseReading(
                    patient=profile,
                    value_demo=6.4,
                    recorded_at=datetime(2026, 11, 6, 9, 30, tzinfo=timezone.utc),
                    reading_context="First fictional reading",
                ),
                GlucoseReading(
                    patient=profile,
                    value_demo=7.1,
                    recorded_at=datetime(2026, 11, 7, 9, 30, tzinfo=timezone.utc),
                    reading_context="Second fictional reading",
                ),
                MealLog(
                    patient=profile,
                    meal_type="breakfast",
                    description="Fictional breakfast",
                    recorded_at=datetime(2026, 11, 6, 8, 0, tzinfo=timezone.utc),
                ),
                ExerciseLog(
                    patient=profile,
                    activity_type="Fictional walking",
                    duration_minutes=20,
                    recorded_at=datetime(2026, 11, 7, 17, 0, tzinfo=timezone.utc),
                ),
                reminder,
                MedicationEvent(
                    patient=profile,
                    reminder=reminder,
                    status="recorded",
                    recorded_at=datetime(2026, 11, 7, 19, 0, tzinfo=timezone.utc),
                    context="Fictional recorded event",
                ),
                GlucoseReading(
                    patient=other_profile,
                    value_demo=9.9,
                    recorded_at=datetime(2026, 11, 6, 9, 30, tzinfo=timezone.utc),
                    reading_context="Other patient's fictional reading",
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


def test_patient_report_is_derived_owned_and_filterable():
    app = make_report_app()
    client = app.test_client()
    login(client, "patient@example.test", "patient-password")

    report_response = client.get("/patient/reports")
    assert report_response.status_code == 200
    assert b"Recorded demo summary" in report_response.data
    assert b"Medication event statuses" in report_response.data
    assert b"Other patient's fictional reading" not in report_response.data

    with app.app_context():
        profile = PatientProfile.query.filter_by(display_name="Demo Patient").one()
        report = build_patient_report(profile)
        assert report["counts"] == {
            "readings": 2,
            "meals": 1,
            "exercises": 1,
            "medication_events": 1,
        }
        assert report["reminder_count"] == 1

    filtered_response = client.get(
        "/patient/reports?start_date=2026-11-06&end_date=2026-11-06"
    )
    assert filtered_response.status_code == 200
    assert b"Showing records from 06 Nov 2026 to 06 Nov 2026" in filtered_response.data
    with app.app_context():
        profile = PatientProfile.query.filter_by(display_name="Demo Patient").one()
        filtered = build_patient_report(
            profile,
            start_date=datetime(2026, 11, 6).date(),
            end_date=datetime(2026, 11, 6).date(),
        )
        assert filtered["counts"]["readings"] == 1
        assert filtered["counts"]["meals"] == 1
        assert filtered["counts"]["exercises"] == 0
        assert filtered["counts"]["medication_events"] == 0


def test_report_date_filters_reject_incomplete_reversed_and_excessive_ranges():
    app = make_report_app()
    client = app.test_client()
    login(client, "patient@example.test", "patient-password")

    incomplete = client.get("/patient/reports?start_date=2026-11-06")
    assert incomplete.status_code == 400
    assert b"Enter both a start date and an end date" in incomplete.data

    reversed_range = client.get(
        "/patient/reports?start_date=2026-11-07&end_date=2026-11-06"
    )
    assert reversed_range.status_code == 400
    assert b"End date must be on or after" in reversed_range.data

    excessive_range = client.get(
        "/patient/reports?start_date=2025-01-01&end_date=2027-01-01"
    )
    assert excessive_range.status_code == 400
    assert b"366 days or less" in excessive_range.data


def test_report_empty_period_is_explicit_without_interpretation():
    app = make_report_app()
    client = app.test_client()
    login(client, "patient@example.test", "patient-password")

    response = client.get(
        "/patient/reports?start_date=2028-01-01&end_date=2028-01-02"
    )

    assert response.status_code == 200
    assert b"No recorded records match this period" in response.data
    assert b"does not indicate adherence" in response.data


def test_assigned_clinician_can_read_report_but_other_roles_cannot():
    app = make_report_app()
    with app.app_context():
        patient_id = PatientProfile.query.filter_by(
            display_name="Demo Patient"
        ).one().id
        other_patient_id = PatientProfile.query.filter_by(
            display_name="Other Demo Patient"
        ).one().id

    clinician_client = app.test_client()
    login(clinician_client, "clinician@example.test", "clinician-password")
    response = clinician_client.get(f"/clinician/patients/{patient_id}/reports")
    assert response.status_code == 200
    assert b"Demo Patient" in response.data
    assert b"Recorded demo summary" in response.data
    assert clinician_client.get(
        f"/clinician/patients/{other_patient_id}/reports"
    ).status_code == 404

    admin_client = app.test_client()
    login(admin_client, "admin@example.test", "admin-password")
    assert admin_client.get("/patient/reports").status_code == 403
    assert admin_client.get(
        f"/clinician/patients/{patient_id}/reports"
    ).status_code == 403


def test_reports_are_read_only_get_routes():
    app = make_report_app()
    patient_client = app.test_client()
    login(patient_client, "patient@example.test", "patient-password")
    assert patient_client.post("/patient/reports").status_code == 405

    with app.app_context():
        patient_id = PatientProfile.query.filter_by(
            display_name="Demo Patient"
        ).one().id
    clinician_client = app.test_client()
    login(clinician_client, "clinician@example.test", "clinician-password")
    assert clinician_client.post(
        f"/clinician/patients/{patient_id}/reports"
    ).status_code == 405

