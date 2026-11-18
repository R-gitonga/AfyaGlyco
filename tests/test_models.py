from datetime import datetime, timezone

from app import create_app, db
from app.models import ClinicianNote, GlucoseReading, PatientProfile, Role, User


def test_core_domain_records_can_be_created_and_related():
    app = create_app(
        {
            "TESTING": True,
            "AUTO_MIGRATE": False,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
        }
    )

    with app.app_context():
        db.create_all()

        patient_user = User(email="patient@example.test")
        patient_user.set_password("demo-password")
        clinician_user = User(email="clinician@example.test")
        clinician_user.set_password("demo-password")
        clinician_user.roles.append(Role(name="clinician"))

        patient = PatientProfile(
            user=patient_user,
            assigned_clinician=clinician_user,
            display_name="Demo Patient",
        )
        patient.glucose_readings.append(
            GlucoseReading(
                value_demo=6.4,
                recorded_at=datetime.now(timezone.utc),
                reading_context="Demo entry",
            )
        )
        patient.clinician_notes.append(
            ClinicianNote(
                author=clinician_user,
                note="Demo follow-up note authored by the clinician.",
            )
        )

        db.session.add(patient)
        db.session.commit()

        assert patient_user.check_password("demo-password")
        assert not patient_user.check_password("wrong-password")
        assert patient.assigned_clinician is clinician_user
        assert len(patient.glucose_readings) == 1
        assert patient.clinician_notes[0].author is clinician_user
