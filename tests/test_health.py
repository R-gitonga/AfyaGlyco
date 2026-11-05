from app import create_app


def test_health_check():
    app = create_app(
        {
            "TESTING": True,
            "AUTO_MIGRATE": False,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
        }
    )

    response = app.test_client().get("/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"

