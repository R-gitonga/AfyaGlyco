from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user
from sqlalchemy import select

from app import db
from app.auth.permissions import role_required
from app.clinician.forms import ClinicianNoteForm
from app.business_rules import can_perform
from app.models import (
    ClinicianNote,
    ExerciseLog,
    GlucoseReading,
    MealLog,
    PatientProfile,
)


clinician_bp = Blueprint("clinician", __name__, url_prefix="/clinician")


def _assigned_patient(patient_id):
    patient = db.session.scalar(
        select(PatientProfile).where(
            PatientProfile.id == patient_id,
        )
    )
    if patient is None or not can_perform(
        current_user, "patient_profile", "read", patient_profile=patient
    ):
        abort(404)
    return patient


@clinician_bp.get("")
@role_required("clinician")
def dashboard():
    patients = list(
        db.session.scalars(
            select(PatientProfile)
            .where(PatientProfile.assigned_clinician_id == current_user.id)
            .order_by(PatientProfile.display_name.asc())
        )
    )
    return render_template("dashboard/clinician.html", patients=patients)


@clinician_bp.get("/patients/<int:patient_id>")
@role_required("clinician")
def patient_review(patient_id):
    patient = _assigned_patient(patient_id)
    if not can_perform(
        current_user, "meal_log", "read", patient_profile=patient
    ) or not can_perform(
        current_user, "exercise_log", "read", patient_profile=patient
    ):
        abort(404)
    readings = list(
        db.session.scalars(
            select(GlucoseReading)
            .where(GlucoseReading.patient_id == patient.id)
            .order_by(GlucoseReading.recorded_at.desc())
        )
    )
    notes = list(
        db.session.scalars(
            select(ClinicianNote)
            .where(ClinicianNote.patient_id == patient.id)
            .order_by(ClinicianNote.created_at.desc())
        )
    )
    meals = list(
        db.session.scalars(
            select(MealLog)
            .where(MealLog.patient_id == patient.id)
            .order_by(MealLog.recorded_at.desc())
        )
    )
    exercises = list(
        db.session.scalars(
            select(ExerciseLog)
            .where(ExerciseLog.patient_id == patient.id)
            .order_by(ExerciseLog.recorded_at.desc())
        )
    )
    return render_template(
        "clinician/patient_review.html",
        patient=patient,
        readings=readings,
        meals=meals,
        exercises=exercises,
        notes=notes,
        form=ClinicianNoteForm(),
    )


@clinician_bp.post("/patients/<int:patient_id>/notes")
@role_required("clinician")
def add_note(patient_id):
    patient = _assigned_patient(patient_id)
    if not can_perform(
        current_user, "clinician_note", "create", patient_profile=patient
    ):
        abort(404)
    form = ClinicianNoteForm()
    is_valid = form.validate_on_submit()
    note_text = (form.note.data or "").strip()
    if not is_valid or not note_text:
        if not note_text and "Enter a note." not in form.note.errors:
            form.note.errors.append("Enter a note.")
        readings = list(
            db.session.scalars(
                select(GlucoseReading)
                .where(GlucoseReading.patient_id == patient.id)
                .order_by(GlucoseReading.recorded_at.desc())
            )
        )
        notes = list(
            db.session.scalars(
                select(ClinicianNote)
                .where(ClinicianNote.patient_id == patient.id)
                .order_by(ClinicianNote.created_at.desc())
            )
        )
        meals = list(
            db.session.scalars(
                select(MealLog)
                .where(MealLog.patient_id == patient.id)
                .order_by(MealLog.recorded_at.desc())
            )
        )
        exercises = list(
            db.session.scalars(
                select(ExerciseLog)
                .where(ExerciseLog.patient_id == patient.id)
                .order_by(ExerciseLog.recorded_at.desc())
            )
        )
        return render_template(
            "clinician/patient_review.html",
            patient=patient,
            readings=readings,
            meals=meals,
            exercises=exercises,
            notes=notes,
            form=form,
        ), 400

    db.session.add(
        ClinicianNote(
            patient=patient,
            author=current_user,
            note=note_text,
        )
    )
    db.session.commit()
    flash("Your clinician-authored note was saved.", "success")
    return redirect(url_for("clinician.patient_review", patient_id=patient.id))
