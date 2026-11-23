from datetime import datetime, timezone

from app import create_app, db
from app.models import (
    MedicationEvent,
    MedicationReminder,
    PatientProfile,
    Role,
    User,
)


def make_medication_app():
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
        other_clinician = User(email="other-clinician@example.test")
        other_clinician.set_password("other-clinician-password")
        other_clinician.roles.append(clinician_role)
        db.session.add_all([patient, other_patient, clinician, other_clinician])
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
                    assigned_clinician=other_clinician,
                    display_name="Other Demo Patient",
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


def test_assigned_clinician_has_complete_reminder_crud_and_patient_read_access():
    app = make_medication_app()
    clinician_client = app.test_client()
    login(clinician_client, "clinician@example.test", "clinician-password")

    with app.app_context():
        patient_id = PatientProfile.query.filter_by(display_name="Demo Patient").one().id

    assert clinician_client.get(
        f"/clinician/patients/{patient_id}/reminders/new"
    ).status_code == 200
    create_response = clinician_client.post(
        f"/clinician/patients/{patient_id}/reminders",
        data={
            "medication_label_demo": "Demo morning reminder",
            "schedule_description": "Morning demonstration schedule",
            "is_active": "y",
        },
    )
    assert create_response.status_code == 302

    with app.app_context():
        reminder = MedicationReminder.query.one()
        reminder_id = reminder.id
        assert reminder.configuring_clinician.email == "clinician@example.test"

    assert clinician_client.get(
        f"/clinician/patients/{patient_id}/reminders/{reminder_id}"
    ).status_code == 200
    update_response = clinician_client.post(
        f"/clinician/patients/{patient_id}/reminders/{reminder_id}/edit",
        data={
            "medication_label_demo": "Updated demo reminder",
            "schedule_description": "Updated schedule",
        },
    )
    assert update_response.status_code == 302
    review = clinician_client.get(f"/clinician/patients/{patient_id}")
    assert b"Updated demo reminder" in review.data
    assert b"Updated schedule" in review.data

    patient_client = app.test_client()
    login(patient_client, "patient@example.test", "patient-password")
    patient_reminders = patient_client.get("/patient/reminders")
    assert patient_reminders.status_code == 200
    assert b"Updated demo reminder" in patient_reminders.data
    assert patient_client.post(
        f"/clinician/patients/{patient_id}/reminders",
        data={"medication_label_demo": "Not allowed", "schedule_description": "No"},
    ).status_code == 403

    delete_response = clinician_client.post(
        f"/clinician/patients/{patient_id}/reminders/{reminder_id}/delete"
    )
    assert delete_response.status_code == 302
    with app.app_context():
        assert db.session.get(MedicationReminder, reminder_id) is None


def test_patient_has_complete_medication_event_crud():
    app = make_medication_app()
    with app.app_context():
        profile = PatientProfile.query.filter_by(display_name="Demo Patient").one()
        clinician = User.query.filter_by(email="clinician@example.test").one()
        reminder = MedicationReminder(
            patient=profile,
            configuring_clinician=clinician,
            medication_label_demo="Demo event reminder",
            schedule_description="Evening demonstration schedule",
        )
        db.session.add(reminder)
        db.session.commit()
        reminder_id = reminder.id

    client = app.test_client()
    login(client, "patient@example.test", "patient-password")
    assert client.get("/patient/medication-events/new").status_code == 200
    create_response = client.post(
        "/patient/medication-events",
        data={
            "reminder_id": str(reminder_id),
            "status": "recorded",
            "recorded_at": "2026-11-19T08:30",
            "context": "patient-entered context",
        },
    )
    assert create_response.status_code == 302

    with app.app_context():
        event = MedicationEvent.query.one()
        event_id = event.id
        assert event.patient.display_name == "Demo Patient"
        assert event.reminder.medication_label_demo == "Demo event reminder"

    detail = client.get(f"/patient/medication-events/{event_id}")
    assert detail.status_code == 200
    assert b"patient-entered context" in detail.data
    update_response = client.post(
        f"/patient/medication-events/{event_id}/edit",
        data={
            "reminder_id": "",
            "status": "skipped",
            "recorded_at": "2026-11-19T09:00",
            "context": "Updated context",
        },
    )
    assert update_response.status_code == 302
    assert b"Updated context" in client.get(
        f"/patient/medication-events/{event_id}"
    ).data

    delete_response = client.post(f"/patient/medication-events/{event_id}/delete")
    assert delete_response.status_code == 302
    with app.app_context():
        assert db.session.get(MedicationEvent, event_id) is None


def test_invalid_medication_event_and_reminder_inputs_are_rejected():
    app = make_medication_app()
    client = app.test_client()
    login(client, "patient@example.test", "patient-password")
    response = client.post(
        "/patient/medication-events",
        data={
            "status": "invented-status",
            "recorded_at": "2026-11-19T08:30",
        },
    )
    assert response.status_code == 400
    assert b"Not a valid choice" in response.data

    clinician_client = app.test_client()
    login(clinician_client, "clinician@example.test", "clinician-password")
    with app.app_context():
        patient_id = PatientProfile.query.filter_by(display_name="Demo Patient").one().id
    reminder_response = clinician_client.post(
        f"/clinician/patients/{patient_id}/reminders",
        data={"medication_label_demo": "", "schedule_description": ""},
    )
    assert reminder_response.status_code == 400
    assert b"Medication label for demonstration" in reminder_response.data


def test_medication_records_enforce_ownership_and_assignment_boundaries():
    app = make_medication_app()
    with app.app_context():
        other_profile = PatientProfile.query.filter_by(
            display_name="Other Demo Patient"
        ).one()
        other_clinician = User.query.filter_by(
            email="other-clinician@example.test"
        ).one()
        reminder = MedicationReminder(
            patient=other_profile,
            configuring_clinician=other_clinician,
            medication_label_demo="Other patient's reminder",
            schedule_description="Other patient's schedule",
        )
        event = MedicationEvent(
            patient=other_profile,
            reminder=reminder,
            status="recorded",
            recorded_at=datetime(2026, 11, 19, 8, 0, tzinfo=timezone.utc),
            context="Other patient's event",
        )
        db.session.add_all([reminder, event])
        db.session.commit()
        reminder_id = reminder.id
        event_id = event.id
        other_patient_id = other_profile.id

    patient_client = app.test_client()
    login(patient_client, "patient@example.test", "patient-password")
    assert patient_client.get(f"/patient/reminders/{reminder_id}").status_code == 404
    assert patient_client.get(f"/patient/medication-events/{event_id}").status_code == 404

    clinician_client = app.test_client()
    login(clinician_client, "clinician@example.test", "clinician-password")
    assert clinician_client.get(f"/clinician/patients/{other_patient_id}").status_code == 404
    assert clinician_client.get(
        f"/clinician/patients/{other_patient_id}/reminders/{reminder_id}"
    ).status_code == 404

