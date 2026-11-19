from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user
from sqlalchemy import select

from app import db
from app.auth.permissions import role_required
from app.business_rules import can_change_account_status
from app.models import User
from app.admin.forms import AdminActionForm


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.get("")
@role_required("administrator")
def dashboard():
    users = list(db.session.scalars(select(User).order_by(User.email.asc())))
    return render_template("dashboard/admin.html", users=users)


@admin_bp.post("/users/<int:user_id>/status")
@role_required("administrator")
def update_status(user_id):
    target = db.session.get(User, user_id)
    if target is None:
        abort(404)

    form = AdminActionForm()
    if not form.validate_on_submit():
        abort(400)

    if not can_change_account_status(current_user, target):
        flash("You cannot deactivate your own administrator account.", "error")
        return redirect(url_for("admin.dashboard"))

    target.is_active = not target.is_active
    db.session.commit()
    state = "activated" if target.is_active else "deactivated"
    flash(f"The account {target.email} was {state}.", "success")
    return redirect(url_for("admin.dashboard"))
