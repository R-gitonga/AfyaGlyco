from pathlib import Path

from flask import Flask, jsonify
from flask_migrate import Migrate, upgrade
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from config import Config


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = "auth.login"


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    @app.get("/health")
    def health_check():
        return jsonify(status="ok", service="afyaglyco")

    # Apply committed migrations automatically when the application starts.
    # Tests can disable this with TESTING=True, and developers can disable it
    # temporarily with AUTO_MIGRATE=0.
    migrations_dir = Path(app.root_path).parent / "migrations"
    if app.config.get("AUTO_MIGRATE") and not app.config.get("TESTING") and migrations_dir.exists():
        with app.app_context():
            upgrade()

    return app

