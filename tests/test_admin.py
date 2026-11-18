from app import create_app, db
from app.models import Role, User


def make_admin_app():
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
        admin_role = Role(name="administrator")
        patient_role = Role(name="patient")
        admin = User(email="admin@example.test")
        admin.set_password("admin-password")
        admin.roles.append(admin_role)
        patient = User(email="patient@example.test")
        patient.set_password("patient-password")
        patient.roles.append(patient_role)
        db.session.add_all([admin, patient])
        db.session.commit()

    return app


def login(client, email, password):
    return client.post(
        "/auth/login",
        data={"email": email, "password": password},
    )


def test_administrator_can_view_users_and_deactivate_account():
    app = make_admin_app()
    client = app.test_client()
    login(client, "admin@example.test", "admin-password")

    dashboard = client.get("/admin")
    assert dashboard.status_code == 200
    assert b"patient@example.test" in dashboard.data
    assert b"patient" in dashboard.data

    with app.app_context():
        patient_id = User.query.filter_by(email="patient@example.test").one().id

    response = client.post(f"/admin/users/{patient_id}/status")
    assert response.status_code == 302

    with app.app_context():
        assert db.session.get(User, patient_id).is_active is False

    patient_client = app.test_client()
    login_response = login(
        patient_client,
        "patient@example.test",
        "patient-password",
    )
    assert login_response.status_code == 200
    assert b"Invalid email or password." in login_response.data


def test_administrator_cannot_deactivate_own_account():
    app = make_admin_app()
    client = app.test_client()
    login(client, "admin@example.test", "admin-password")

    with app.app_context():
        admin_id = User.query.filter_by(email="admin@example.test").one().id

    response = client.post(f"/admin/users/{admin_id}/status", follow_redirects=True)

    assert response.status_code == 200
    assert b"cannot deactivate your own" in response.data
    with app.app_context():
        assert db.session.get(User, admin_id).is_active is True


def test_non_administrator_cannot_access_admin_management():
    app = make_admin_app()
    client = app.test_client()
    login(client, "patient@example.test", "patient-password")

    assert client.get("/admin").status_code == 403
