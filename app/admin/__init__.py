"""Administrator routes for managing demo accounts, organizations, and assignments."""

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy import select

from app import db
from app.auth.permissions import role_required
from app.business_rules import (
    can_change_account_status,
    can_manage_clinician_account,
    can_manage_organization,
    can_manage_patient_assignment,
)
from app.models import Organization, PatientProfile, Role, User
from app.admin.forms import (
    AdminActionForm,
    ClinicianEditForm,
    ClinicianRegistrationForm,
    OrganizationForm,
    PatientAssignmentForm,
)


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.get("")
@role_required("administrator")
def dashboard():
    users = list(db.session.scalars(select(User).order_by(User.email.asc())))
    organizations = list(
        db.session.scalars(select(Organization).order_by(Organization.name.asc()))
    )
    return render_template(
        "dashboard/admin.html", users=users, organizations=organizations
    )


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


def _active_organizations():
    return list(
        db.session.scalars(
            select(Organization)
            .where(Organization.is_active.is_(True))
            .order_by(Organization.name.asc())
        )
    )


def _clinician_users():
    return list(
        db.session.scalars(
            select(User)
            .join(User.roles)
            .where(Role.name == "clinician")
            .order_by(User.email.asc())
        )
    )


def _patient_profile(patient_id):
    patient = db.session.get(PatientProfile, patient_id)
    if patient is None:
        abort(404)
    return patient


@admin_bp.get("/organizations")
@role_required("administrator")
def organizations():
    if not can_manage_organization(current_user, "read"):
        abort(403)
    records = list(
        db.session.scalars(select(Organization).order_by(Organization.name.asc()))
    )
    return render_template("admin/organizations.html", organizations=records)


@admin_bp.route("/organizations/new", methods=["GET", "POST"])
@role_required("administrator")
def new_organization():
    if not can_manage_organization(current_user, "create"):
        abort(403)
    form = OrganizationForm()
    if form.validate_on_submit():
        name = form.name.data.strip()
        if Organization.query.filter_by(name=name).first() is not None:
            form.name.errors.append("An organization with this name already exists.")
        else:
            db.session.add(
                Organization(
                    name=name,
                    organization_type=form.organization_type.data,
                )
            )
            db.session.commit()
            flash("The organization was created.", "success")
            return redirect(url_for("admin.organizations"))
    return render_template("admin/organization_form.html", form=form, editing=False)


@admin_bp.route("/organizations/<int:organization_id>/edit", methods=["GET", "POST"])
@role_required("administrator")
def edit_organization(organization_id):
    if not can_manage_organization(current_user, "update"):
        abort(403)
    organization = db.session.get(Organization, organization_id)
    if organization is None:
        abort(404)
    form = OrganizationForm(obj=organization)
    if form.validate_on_submit():
        name = form.name.data.strip()
        duplicate = db.session.scalar(
            select(Organization).where(
                Organization.name == name,
                Organization.id != organization.id,
            )
        )
        if duplicate is not None:
            form.name.errors.append("An organization with this name already exists.")
        else:
            organization.name = name
            organization.organization_type = form.organization_type.data
            db.session.commit()
            flash("The organization was updated.", "success")
            return redirect(url_for("admin.organizations"))
    return render_template(
        "admin/organization_form.html", form=form, editing=True, organization=organization
    )


@admin_bp.post("/organizations/<int:organization_id>/status")
@role_required("administrator")
def update_organization_status(organization_id):
    if not can_manage_organization(current_user, "update"):
        abort(403)
    organization = db.session.get(Organization, organization_id)
    if organization is None:
        abort(404)
    form = AdminActionForm()
    if not form.validate_on_submit():
        abort(400)
    organization.is_active = not organization.is_active
    db.session.commit()
    state = "activated" if organization.is_active else "deactivated"
    flash(f"The organization {organization.name} was {state}.", "success")
    return redirect(url_for("admin.organizations"))


@admin_bp.get("/clinicians")
@role_required("administrator")
def clinicians():
    if not can_manage_clinician_account(current_user, "read"):
        abort(403)
    return render_template("admin/clinicians.html", clinicians=_clinician_users())


@admin_bp.route("/clinicians/new", methods=["GET", "POST"])
@role_required("administrator")
def new_clinician():
    if not can_manage_clinician_account(current_user, "create"):
        abort(403)
    form = ClinicianRegistrationForm()
    organizations = _active_organizations()
    form.set_organizations(organizations)
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        organization = db.session.get(Organization, int(form.organization_id.data))
        if User.query.filter_by(email=email).first() is not None:
            form.email.errors.append("An account with this email already exists.")
        elif organization is None or not organization.is_active:
            form.organization_id.errors.append("Choose an active organization.")
        else:
            role = db.session.scalar(select(Role).where(Role.name == "clinician"))
            if role is None:
                role = Role(name="clinician")
                db.session.add(role)
            clinician = User(
                email=email,
                display_name=form.display_name.data.strip(),
                organization=organization,
            )
            clinician.set_password(form.password.data)
            clinician.roles.append(role)
            db.session.add(clinician)
            db.session.commit()
            flash("The clinician account was created.", "success")
            return redirect(url_for("admin.clinicians"))
    return render_template("admin/clinician_form.html", form=form, editing=False)


@admin_bp.route("/clinicians/<int:user_id>/edit", methods=["GET", "POST"])
@role_required("administrator")
def edit_clinician(user_id):
    if not can_manage_clinician_account(current_user, "update"):
        abort(403)
    clinician = db.session.get(User, user_id)
    if clinician is None or not clinician.has_role("clinician"):
        abort(404)
    form = ClinicianEditForm(obj=clinician)
    organizations = _active_organizations()
    form.set_organizations(organizations)
    if request.method == "GET":
        form.email.data = clinician.email
        form.display_name.data = clinician.display_name or clinician.email
        form.organization_id.data = str(clinician.organization_id or "")
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        organization = db.session.get(Organization, int(form.organization_id.data))
        duplicate = db.session.scalar(
            select(User).where(User.email == email, User.id != clinician.id)
        )
        if duplicate is not None:
            form.email.errors.append("An account with this email already exists.")
        elif organization is None or not organization.is_active:
            form.organization_id.errors.append("Choose an active organization.")
        else:
            clinician.email = email
            clinician.display_name = form.display_name.data.strip()
            clinician.organization = organization
            db.session.commit()
            flash("The clinician account was updated.", "success")
            return redirect(url_for("admin.clinicians"))
    return render_template(
        "admin/clinician_form.html", form=form, editing=True, clinician=clinician
    )


@admin_bp.post("/clinicians/<int:user_id>/status")
@role_required("administrator")
def update_clinician_status(user_id):
    if not can_manage_clinician_account(current_user, "update"):
        abort(403)
    clinician = db.session.get(User, user_id)
    if clinician is None or not clinician.has_role("clinician"):
        abort(404)
    form = AdminActionForm()
    if not form.validate_on_submit():
        abort(400)
    clinician.is_active = not clinician.is_active
    db.session.commit()
    state = "activated" if clinician.is_active else "deactivated"
    flash(f"The clinician account {clinician.email} was {state}.", "success")
    return redirect(url_for("admin.clinicians"))


@admin_bp.get("/patients")
@role_required("administrator")
def patients():
    if not can_manage_patient_assignment(current_user, "read"):
        abort(403)
    records = list(
        db.session.scalars(
            select(PatientProfile).order_by(PatientProfile.display_name.asc())
        )
    )
    assignment_forms = {}
    for patient in records:
        form = PatientAssignmentForm()
        clinicians = list(
            db.session.scalars(
                select(User)
                .join(User.roles)
                .where(
                    Role.name == "clinician",
                    User.is_active.is_(True),
                    User.organization_id == patient.organization_id,
                )
                .order_by(User.email.asc())
            )
        )
        form.set_clinicians(clinicians)
        form.clinician_id.data = str(patient.assigned_clinician_id or "")
        assignment_forms[patient.id] = form
    return render_template(
        "admin/patients.html", patients=records, assignment_forms=assignment_forms
    )


@admin_bp.post("/patients/<int:patient_id>/assignment")
@role_required("administrator")
def update_patient_assignment(patient_id):
    patient = _patient_profile(patient_id)
    if not can_manage_patient_assignment(current_user, "update", patient):
        abort(403)
    form = PatientAssignmentForm()
    clinicians = list(
        db.session.scalars(
            select(User)
            .join(User.roles)
            .where(
                Role.name == "clinician",
                User.is_active.is_(True),
                User.organization_id == patient.organization_id,
            )
            .order_by(User.email.asc())
        )
    )
    form.set_clinicians(clinicians)
    if not form.validate_on_submit():
        abort(400)
    clinician = None
    if form.clinician_id.data:
        clinician = db.session.get(User, int(form.clinician_id.data))
        if (
            clinician is None
            or not clinician.is_active
            or not clinician.has_role("clinician")
            or clinician.organization_id != patient.organization_id
        ):
            abort(404)
    patient.assigned_clinician = clinician
    db.session.commit()
    flash("The patient assignment was updated.", "success")
    return redirect(url_for("admin.patients"))
