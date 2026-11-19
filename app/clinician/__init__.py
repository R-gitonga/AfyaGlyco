from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy import select

from app import db
from app.auth.permissions import role_required
from app.clinician.forms import (
    ClinicianNoteForm,
    DeleteReminderForm,
    MedicationReminderForm,
)
from app.business_rules import can_perform
from app.models import (
    ClinicianNote,
    ExerciseLog,
    GlucoseReading,
    MealLog,
    MedicationEvent,
    MedicationReminder,
    PatientProfile,
)
from app.reporting import build_patient_report
from app.reporting_forms import ReportFilterForm


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


def _delete_reminder_forms(reminders):
    return {reminder.id: DeleteReminderForm() for reminder in reminders}


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
    reminders = list(
        db.session.scalars(
            select(MedicationReminder)
            .where(MedicationReminder.patient_id == patient.id)
            .order_by(MedicationReminder.created_at.desc())
        )
    )
    medication_events = list(
        db.session.scalars(
            select(MedicationEvent)
            .where(MedicationEvent.patient_id == patient.id)
            .order_by(MedicationEvent.recorded_at.desc())
        )
    )
    return render_template(
        "clinician/patient_review.html",
        patient=patient,
        readings=readings,
        meals=meals,
        exercises=exercises,
        reminders=reminders,
        medication_events=medication_events,
        notes=notes,
        form=ClinicianNoteForm(),
        delete_reminder_forms=_delete_reminder_forms(reminders),
    )


@clinician_bp.get("/patients/<int:patient_id>/reports")
@role_required("clinician")
def report_summary(patient_id):
    patient = _assigned_patient(patient_id)
    if not can_perform(
        current_user, "patient_report", "read", patient_profile=patient
    ):
        abort(404)
    form = ReportFilterForm(request.args)
    report = None
    status_code = 200
    if form.validate():
        report = build_patient_report(
            patient,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
        )
    elif request.args:
        status_code = 400
    return render_template(
        "clinician/report.html",
        patient=patient,
        form=form,
        report=report,
    ), status_code


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
        reminders = list(
            db.session.scalars(
                select(MedicationReminder)
                .where(MedicationReminder.patient_id == patient.id)
                .order_by(MedicationReminder.created_at.desc())
            )
        )
        medication_events = list(
            db.session.scalars(
                select(MedicationEvent)
                .where(MedicationEvent.patient_id == patient.id)
                .order_by(MedicationEvent.recorded_at.desc())
            )
        )
        return render_template(
            "clinician/patient_review.html",
            patient=patient,
            readings=readings,
            meals=meals,
            exercises=exercises,
            reminders=reminders,
            medication_events=medication_events,
            notes=notes,
            form=form,
            delete_reminder_forms=_delete_reminder_forms(reminders),
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


def _assigned_reminder(patient, reminder_id):
    reminder = db.session.scalar(
        select(MedicationReminder).where(
            MedicationReminder.id == reminder_id,
            MedicationReminder.patient_id == patient.id,
        )
    )
    if reminder is None:
        abort(404)
    return reminder


@clinician_bp.get("/patients/<int:patient_id>/reminders/new")
@role_required("clinician")
def new_reminder(patient_id):
    patient = _assigned_patient(patient_id)
    if not can_perform(
        current_user, "medication_reminder", "create", patient_profile=patient
    ):
        abort(404)
    return render_template(
        "clinician/reminder_form.html",
        patient=patient,
        form=MedicationReminderForm(),
        editing=False,
        reminder_id=None,
    )


@clinician_bp.post("/patients/<int:patient_id>/reminders")
@role_required("clinician")
def create_reminder(patient_id):
    patient = _assigned_patient(patient_id)
    if not can_perform(
        current_user, "medication_reminder", "create", patient_profile=patient
    ):
        abort(404)
    form = MedicationReminderForm()
    if not form.validate_on_submit():
        return render_template(
            "clinician/reminder_form.html",
            patient=patient,
            form=form,
            editing=False,
            reminder_id=None,
        ), 400
    reminder = MedicationReminder(
        patient=patient,
        configuring_clinician=current_user,
        medication_label_demo=form.medication_label_demo.data.strip(),
        schedule_description=form.schedule_description.data.strip(),
        is_active=bool(form.is_active.data),
    )
    db.session.add(reminder)
    db.session.commit()
    flash("The fictional medication reminder was saved.", "success")
    return redirect(url_for("clinician.patient_review", patient_id=patient.id))


@clinician_bp.get("/patients/<int:patient_id>/reminders/<int:reminder_id>")
@role_required("clinician")
def reminder_detail(patient_id, reminder_id):
    patient = _assigned_patient(patient_id)
    if not can_perform(
        current_user, "medication_reminder", "read", patient_profile=patient
    ):
        abort(404)
    reminder = _assigned_reminder(patient, reminder_id)
    return render_template(
        "clinician/reminder_detail.html",
        patient=patient,
        reminder=reminder,
        delete_form=DeleteReminderForm(),
    )


@clinician_bp.route(
    "/patients/<int:patient_id>/reminders/<int:reminder_id>/edit",
    methods=["GET", "POST"],
)
@role_required("clinician")
def edit_reminder(patient_id, reminder_id):
    patient = _assigned_patient(patient_id)
    if not can_perform(
        current_user, "medication_reminder", "update", patient_profile=patient
    ):
        abort(404)
    reminder = _assigned_reminder(patient, reminder_id)
    form = MedicationReminderForm(obj=reminder)
    if request.method == "POST":
        if not form.validate_on_submit():
            return render_template(
                "clinician/reminder_form.html",
                patient=patient,
                form=form,
                editing=True,
                reminder_id=reminder.id,
            ), 400
        reminder.medication_label_demo = form.medication_label_demo.data.strip()
        reminder.schedule_description = form.schedule_description.data.strip()
        reminder.is_active = bool(form.is_active.data)
        db.session.commit()
        flash("The fictional medication reminder was updated.", "success")
        return redirect(
            url_for(
                "clinician.reminder_detail",
                patient_id=patient.id,
                reminder_id=reminder.id,
            )
        )
    return render_template(
        "clinician/reminder_form.html",
        patient=patient,
        form=form,
        editing=True,
        reminder_id=reminder.id,
    )


@clinician_bp.post(
    "/patients/<int:patient_id>/reminders/<int:reminder_id>/delete"
)
@role_required("clinician")
def delete_reminder(patient_id, reminder_id):
    patient = _assigned_patient(patient_id)
    if not can_perform(
        current_user, "medication_reminder", "delete", patient_profile=patient
    ):
        abort(404)
    reminder = _assigned_reminder(patient, reminder_id)
    form = DeleteReminderForm()
    if not form.validate_on_submit():
        abort(400)
    db.session.delete(reminder)
    db.session.commit()
    flash("The fictional medication reminder was deleted.", "success")
    return redirect(url_for("clinician.patient_review", patient_id=patient.id))
