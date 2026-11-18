from pathlib import Path

from flask import Flask, jsonify
from flask_migrate import Migrate, upgrade
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy

from config import Config


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
csrf = CSRFProtect()

# Import models after db is created so Flask-Migrate can discover their tables.
from app import models  # noqa: E402,F401


@login_manager.user_loader
def load_user(user_id):
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return None
    return db.session.get(models.User, user_id)


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    from app.auth import auth_bp
    from app.admin import admin_bp
    from app.clinician import clinician_bp
    from app.main import main_bp
    from app.patient import patient_bp
    from app.seed import register_seed_command

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(clinician_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(patient_bp)
    register_seed_command(app)

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

