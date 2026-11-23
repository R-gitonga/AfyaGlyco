"""Integration tests for organization, clinician, and patient registration flows."""

from app import create_app, db
from app.models import Organization, PatientProfile, Role, User


def make_registration_app():
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
        organization = Organization(
            name="Demo Clinic",
            organization_type="clinic",
        )
        other_organization = Organization(
            name="Demo Hospital",
            organization_type="hospital",
        )
        admin = User(email="admin@example.test")
        admin.set_password("admin-password")
        admin.roles.append(administrator_role)
        clinician = User(
            email="clinician@example.test",
            display_name="Demo Clinician",
            organization=organization,
        )
        clinician.set_password("clinician-password")
        clinician.roles.append(clinician_role)
        other_clinician = User(
            email="other-clinician@example.test",
            display_name="Other Clinician",
            organization=other_organization,
        )
        other_clinician.set_password("other-clinician-password")
        other_clinician.roles.append(clinician_role)
        unassigned_user = User(
            email="unassigned@example.test",
            display_name="Unassigned Patient",
            organization=organization,
        )
        unassigned_user.set_password("patient-password")
        unassigned_user.roles.append(patient_role)
        other_patient_user = User(
            email="other-patient@example.test",
            display_name="Other Patient",
            organization=other_organization,
        )
        other_patient_user.set_password("patient-password")
        other_patient_user.roles.append(patient_role)
        db.session.add_all(
            [
                organization,
                other_organization,
                admin,
                clinician,
                other_clinician,
                unassigned_user,
                other_patient_user,
            ]
        )
        db.session.flush()
        db.session.add_all(
            [
                PatientProfile(
                    user=unassigned_user,
                    organization=organization,
                    display_name="Unassigned Patient",
                ),
                PatientProfile(
                    user=other_patient_user,
                    organization=other_organization,
                    display_name="Other Patient",
                    assigned_clinician=other_clinician,
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


def test_administrator_can_manage_organizations_and_clinician_accounts():
    app = make_registration_app()
    client = app.test_client()
    login(client, "admin@example.test", "admin-password")

    assert client.get("/admin/organizations").status_code == 200
    organization_response = client.post(
        "/admin/organizations/new",
        data={"name": "New Hospital", "organization_type": "hospital"},
    )
    assert organization_response.status_code == 302
    with app.app_context():
        organization = Organization.query.filter_by(
            name="New Hospital"
        ).one()
        organization_id = organization.id

    edit_response = client.post(
        f"/admin/organizations/{organization_id}/edit",
        data={"name": "Updated Hospital", "organization_type": "hospital"},
    )
    assert edit_response.status_code == 302
    status_response = client.post(
        f"/admin/organizations/{organization_id}/status"
    )
    assert status_response.status_code == 302
    with app.app_context():
        assert db.session.get(Organization, organization_id).is_active is False
        active_organization_id = Organization.query.filter_by(
            name="Demo Clinic"
        ).one().id
    create_clinician = client.post(
        "/admin/clinicians/new",
        data={
            "email": "new-clinician@example.test",
            "display_name": "New Demo Clinician",
            "password": "new-clinician-password",
            "organization_id": str(active_organization_id),
        },
    )
    assert create_clinician.status_code == 302
    with app.app_context():
        clinician = User.query.filter_by(email="new-clinician@example.test").one()
        clinician_id = clinician.id
        assert clinician.has_role("clinician")
        assert clinician.check_password("new-clinician-password")
        assert clinician.password_hash != "new-clinician-password"
        assert clinician.organization.name == "Demo Clinic"

    edit_clinician = client.post(
        f"/admin/clinicians/{clinician_id}/edit",
        data={
            "email": "new-clinician@example.test",
            "display_name": "Updated Demo Clinician",
            "organization_id": str(active_organization_id),
        },
    )
    assert edit_clinician.status_code == 302
    assert client.post(f"/admin/clinicians/{clinician_id}/status").status_code == 302
    with app.app_context():
        assert db.session.get(User, clinician_id).is_active is False


def test_clinician_can_register_new_patient_and_add_existing_unassigned_patient():
    app = make_registration_app()
    client = app.test_client()
    login(client, "clinician@example.test", "clinician-password")

    assert client.get("/clinician/patients").status_code == 200
    create_response = client.post(
        "/clinician/patients/register",
        data={
            "email": "new-patient@example.test",
            "display_name": "New Demo Patient",
            "password": "new-patient-password",
        },
    )
    assert create_response.status_code == 302
    with app.app_context():
        patient = User.query.filter_by(email="new-patient@example.test").one()
        profile = patient.patient_profile
        assert patient.has_role("patient")
        assert patient.check_password("new-patient-password")
        assert patient.password_hash != "new-patient-password"
        assert profile.assigned_clinician.email == "clinician@example.test"
        assert profile.organization.name == "Demo Clinic"

        unassigned = PatientProfile.query.filter_by(
            display_name="Unassigned Patient"
        ).one()
        unassigned_id = unassigned.id

    add_existing = client.post(
        "/clinician/patients/add-existing",
        data={"patient_id": str(unassigned_id)},
    )
    assert add_existing.status_code == 302
    with app.app_context():
        assert db.session.get(PatientProfile, unassigned_id).assigned_clinician.email == (
            "clinician@example.test"
        )


def test_clinician_cannot_take_over_assigned_or_cross_organization_patient():
    app = make_registration_app()
    client = app.test_client()
    login(client, "clinician@example.test", "clinician-password")

    with app.app_context():
        other_patient = PatientProfile.query.filter_by(
            display_name="Other Patient"
        ).one()
        other_patient_id = other_patient.id
        assert other_patient.assigned_clinician.email == "other-clinician@example.test"

    response = client.post(
        "/clinician/patients/add-existing",
        data={"patient_id": str(other_patient_id)},
    )
    assert response.status_code == 200
    with app.app_context():
        assert db.session.get(PatientProfile, other_patient_id).assigned_clinician.email == (
            "other-clinician@example.test"
        )

    assert client.get(f"/clinician/patients/{other_patient_id}").status_code == 404


def test_administrator_can_transfer_or_unassign_assignment_without_health_records():
    app = make_registration_app()
    client = app.test_client()
    login(client, "admin@example.test", "admin-password")

    with app.app_context():
        patient = PatientProfile.query.filter_by(display_name="Other Patient").one()
        patient_id = patient.id
        clinician = User.query.filter_by(email="other-clinician@example.test").one()
        clinician_id = clinician.id

    response = client.post(
        f"/admin/patients/{patient_id}/assignment",
        data={"clinician_id": str(clinician_id)},
    )
    assert response.status_code == 302
    with app.app_context():
        assert db.session.get(PatientProfile, patient_id).assigned_clinician_id == clinician_id

    unassign_response = client.post(
        f"/admin/patients/{patient_id}/assignment",
        data={"clinician_id": ""},
    )
    assert unassign_response.status_code == 302
    with app.app_context():
        assert db.session.get(PatientProfile, patient_id).assigned_clinician_id is None

    assignment_page = client.get("/admin/patients")
    assert assignment_page.status_code == 200
    assert b"Only assignment metadata is shown" in assignment_page.data
    assert b"Recorded values" not in assignment_page.data


def test_patient_can_read_own_profile_and_cannot_change_assignment():
    app = make_registration_app()
    with app.app_context():
        user = User.query.filter_by(email="unassigned@example.test").one()
        user.patient_profile.assigned_clinician = User.query.filter_by(
            email="clinician@example.test"
        ).one()
        db.session.commit()

    client = app.test_client()
    login(client, "unassigned@example.test", "patient-password")
    response = client.get("/patient/profile")
    assert response.status_code == 200
    assert b"Demo Clinic" in response.data
    assert b"Demo Clinician" in response.data
    assert client.post("/patient/profile").status_code == 405
