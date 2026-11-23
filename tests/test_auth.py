from app import create_app, db
from app.models import PatientProfile, Role, User


def make_auth_app():
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
        clinician = User(email="clinician@example.test")
        clinician.set_password("clinician-password")
        clinician.roles.append(clinician_role)
        administrator = User(email="admin@example.test")
        administrator.set_password("admin-password")
        administrator.roles.append(administrator_role)
        db.session.add_all([patient, clinician, administrator])
        db.session.flush()
        db.session.add(
            PatientProfile(
                user=patient,
                assigned_clinician=clinician,
                display_name="Demo Patient",
            )
        )
        db.session.commit()

    return app


def make_empty_auth_app():
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

    return app


def test_successful_login_redirects_to_the_role_dashboard():
    app = make_auth_app()
    response = app.test_client().post(
        "/auth/login",
        data={"email": "patient@example.test", "password": "patient-password"},
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")

    dashboard = app.test_client()
    dashboard.post(
        "/auth/login",
        data={"email": "patient@example.test", "password": "patient-password"},
    )
    response = dashboard.get("/patient")
    assert response.status_code == 200
    assert b"Patient area" in response.data


def test_failed_login_shows_a_generic_error():
    app = make_auth_app()
    response = app.test_client().post(
        "/auth/login",
        data={"email": "patient@example.test", "password": "wrong-password"},
    )

    assert response.status_code == 200
    assert b"Invalid email or password." in response.data


def test_empty_database_shows_first_administrator_link():
    app = make_empty_auth_app()

    response = app.test_client().get("/auth/login")

    assert response.status_code == 200
    assert b"Create the first administrator" in response.data


def test_first_administrator_bootstrap_creates_account_and_logs_in():
    app = make_empty_auth_app()
    client = app.test_client()

    response = client.post(
        "/auth/bootstrap-admin",
        data={
            "email": "first.admin@example.test",
            "display_name": "First Demo Administrator",
            "password": "first-admin-password",
            "confirm_password": "first-admin-password",
        },
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")
    with app.app_context():
        administrator = User.query.filter_by(
            email="first.admin@example.test"
        ).one()
        assert administrator.display_name == "First Demo Administrator"
        assert administrator.check_password("first-admin-password")
        assert administrator.has_role("administrator")


def test_first_administrator_bootstrap_is_unavailable_after_first_user():
    app = make_empty_auth_app()
    client = app.test_client()
    client.post(
        "/auth/bootstrap-admin",
        data={
            "email": "first.admin@example.test",
            "display_name": "First Demo Administrator",
            "password": "first-admin-password",
            "confirm_password": "first-admin-password",
        },
    )

    response = client.get("/auth/bootstrap-admin")
    login_page = client.get("/auth/login")

    assert response.status_code == 404
    assert b"Create the first administrator" not in login_page.data


def test_first_administrator_bootstrap_validates_password_confirmation():
    app = make_empty_auth_app()

    response = app.test_client().post(
        "/auth/bootstrap-admin",
        data={
            "email": "first.admin@example.test",
            "display_name": "First Demo Administrator",
            "password": "short",
            "confirm_password": "different",
        },
    )

    assert response.status_code == 200
    assert b"Field must be between 12 and 255 characters long." in response.data
    assert b"Passwords must match." in response.data
    with app.app_context():
        assert User.query.count() == 0


def test_patient_cannot_access_other_role_dashboards():
    app = make_auth_app()
    client = app.test_client()
    client.post(
        "/auth/login",
        data={"email": "patient@example.test", "password": "patient-password"},
    )

    assert client.get("/patient").status_code == 200
    assert client.get("/clinician").status_code == 403
    assert client.get("/admin").status_code == 403


def test_seed_demo_command_creates_fictional_accounts():
    app = create_app(
        {
            "TESTING": True,
            "AUTO_MIGRATE": False,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
        }
    )
    with app.app_context():
        db.create_all()

    result = app.test_cli_runner().invoke(
        args=["seed-demo", "--password", "demo-password"]
    )

    assert result.exit_code == 0
    assert "Fictional demo accounts are ready" in result.output
    with app.app_context():
        patient = User.query.filter_by(email="patient@example.test").one()
        assert patient.check_password("demo-password")
        assert patient.has_role("patient")
        assert patient.patient_profile.assigned_clinician.email == (
            "clinician@example.test"
        )
