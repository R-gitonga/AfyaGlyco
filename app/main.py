from flask import Blueprint, abort, redirect, url_for
from flask_login import current_user, login_required



main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def index():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))
    return redirect(url_for("main.role_home"))


@main_bp.get("/dashboard")
@login_required
def role_home():
    if current_user.has_role("administrator"):
        return redirect(url_for("admin.dashboard"))
    if current_user.has_role("clinician"):
        return redirect(url_for("clinician.dashboard"))
    if current_user.has_role("patient"):
        return redirect(url_for("patient.dashboard"))
    abort(403)
