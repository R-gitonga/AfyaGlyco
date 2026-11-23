from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app import db
from app.auth.forms import BootstrapAdminForm, LoginForm
from app.auth.services import (
    BootstrapUnavailable,
    bootstrap_available,
    create_initial_administrator,
)
from app.models import User


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.role_home"))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = User.query.filter_by(email=email).first()
        if user and user.is_active and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for("main.role_home"))

        flash("Invalid email or password.", "error")

    return render_template(
        "auth/login.html",
        form=form,
        bootstrap_available=bootstrap_available(),
    )


@auth_bp.route("/bootstrap-admin", methods=["GET", "POST"])
def bootstrap_admin():
    """Create and sign in the first administrator for an empty database."""

    if not bootstrap_available():
        abort(404)

    form = BootstrapAdminForm()
    if form.validate_on_submit():
        try:
            administrator = create_initial_administrator(
                form.email.data,
                form.display_name.data,
                form.password.data,
            )
        except BootstrapUnavailable:
            db.session.rollback()
            abort(404)

        login_user(administrator)
        flash("Your administrator account is ready.", "success")
        return redirect(url_for("main.role_home"))

    return render_template("auth/bootstrap_admin.html", form=form)


@auth_bp.post("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been signed out.", "success")
    return redirect(url_for("auth.login"))
