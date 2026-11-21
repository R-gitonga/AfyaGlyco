"""Patient routes for self-monitoring records, profile metadata, and reports."""

from datetime import timezone
from decimal import Decimal

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy import select

from app import db
from app.auth.permissions import role_required
from app.business_rules import can_manage_patient_registration, can_perform, normalize_recorded_at
from app.models import (
    ExerciseLog,
    GlucoseReading,
    MealLog,
    MedicationEvent,
    MedicationReminder,
    PatientProfile,
)
from app.patient.forms import (
    DeleteRecordForm,
    ExerciseLogForm,
    GlucoseReadingForm,
    MealLogForm,
    MedicationEventForm,
)
from app.reporting import build_patient_report
from app.reporting_forms import ReportFilterForm


patient_bp = Blueprint("patient", __name__, url_prefix="/patient")


def _current_profile():
    profile = PatientProfile.query.filter_by(user_id=current_user.id).first()
    if profile is None:
        abort(404)
    return profile


def _as_utc(value):
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _chart_bars(readings):
    """Build an accessible, non-clinical visual summary for recent entries."""
    if not readings:
        return []

    values = [Decimal(reading.value_demo) for reading in readings]
    maximum = max(values)
    minimum = min(values)
    span = maximum - minimum
    if span == 0:
        span = Decimal("1")

    bars = []
    for reading, value in zip(readings, values):
        height = 28 + int(((value - minimum) / span) * 62)
        bars.append(
            {
                "height": height,
                "label": reading.recorded_at.strftime("%d %b"),
                "value": f"{value:.2f}",
            }
        )
    return bars


@patient_bp.get("")
@role_required("patient")
def dashboard():
    profile = _current_profile()
    if not can_perform(
        current_user, "patient_profile", "read", patient_profile=profile
    ):
        abort(404)
    readings = list(
        db.session.scalars(
            select(GlucoseReading)
            .where(GlucoseReading.patient_id == profile.id)
            .order_by(GlucoseReading.recorded_at.desc())
        )
    )

    meals = list(
        db.session.scalars(
            select(MealLog)
            .where(MealLog.patient_id == profile.id)
            .order_by(MealLog.recorded_at.desc())
        )
    )
    exercises = list(
        db.session.scalars(
            select(ExerciseLog)
            .where(ExerciseLog.patient_id == profile.id)
            .order_by(ExerciseLog.recorded_at.desc())
        )
    )
    reminders = list(
        db.session.scalars(
            select(MedicationReminder)
            .where(MedicationReminder.patient_id == profile.id)
            .order_by(MedicationReminder.created_at.desc())
        )
    )
    medication_events = list(
        db.session.scalars(
            select(MedicationEvent)
            .where(MedicationEvent.patient_id == profile.id)
            .order_by(MedicationEvent.recorded_at.desc())
        )
    )
    recent_readings = readings[:5]
    chart_readings = list(reversed(readings[:7]))
    return render_template(
        "dashboard/patient.html",
        profile=profile,
        readings=recent_readings,
        chart_bars=_chart_bars(chart_readings),
        notes=profile.clinician_notes[:3],
        meals=meals[:3],
        exercises=exercises[:3],
        meal_count=len(meals),
        exercise_count=len(exercises),
        reminders=reminders[:3],
        medication_events=medication_events[:3],
        reminder_count=len(reminders),
        medication_event_count=len(medication_events),
    )


@patient_bp.get("/reports")
@role_required("patient")
def report_summary():
    profile = _current_profile()
    if not can_perform(
        current_user, "patient_report", "read", patient_profile=profile
    ):
        abort(404)
    form = ReportFilterForm(request.args)
    report = None
    status_code = 200
    if form.validate():
        report = build_patient_report(
            profile,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
        )
    elif request.args:
        status_code = 400
    return render_template(
        "patient/report.html",
        profile=profile,
        form=form,
        report=report,
    ), status_code


@patient_bp.get("/profile")
@role_required("patient")
def profile_summary():
    profile = _current_profile()
    if not can_manage_patient_registration(
        current_user, "read", patient_profile=profile
    ):
        abort(404)
    return render_template("patient/profile.html", profile=profile)


@patient_bp.get("/readings/new")
@role_required("patient")
def new_reading():
    return render_template(
        "patient/reading_form.html",
        form=GlucoseReadingForm(),
        editing=False,
        record_id=None,
    )


@patient_bp.post("/readings")
@role_required("patient")
def create_reading():
    profile = _current_profile()
    if not can_perform(
        current_user, "glucose_reading", "create", patient_profile=profile
    ):
        abort(403)
    form = GlucoseReadingForm()
    if not form.validate_on_submit():
        return render_template(
            "patient/reading_form.html",
            form=form,
            editing=False,
            record_id=None,
        ), 400

    reading = GlucoseReading(
        patient=profile,
        value_demo=form.value_demo.data,
        recorded_at=_as_utc(form.recorded_at.data),
        reading_context=form.reading_context.data.strip() or None,
    )
    db.session.add(reading)
    db.session.commit()
    flash("Your fictional glucose reading was recorded.", "success")
    return redirect(url_for("patient.dashboard"))


@patient_bp.get("/readings")
@role_required("patient")
def reading_history():
    profile = _current_profile()
    if not can_perform(
        current_user, "glucose_reading", "read", patient_profile=profile
    ):
        abort(404)
    readings = list(
        db.session.scalars(
            select(GlucoseReading)
            .where(GlucoseReading.patient_id == profile.id)
            .order_by(GlucoseReading.recorded_at.desc())
        )
    )
    return render_template("patient/readings.html", readings=readings)


@patient_bp.get("/readings/<int:reading_id>")
@role_required("patient")
def reading_detail(reading_id):
    profile = _current_profile()
    reading = db.session.scalar(
        select(GlucoseReading).where(
            GlucoseReading.id == reading_id,
            GlucoseReading.patient_id == profile.id,
        )
    )
    if reading is None or not can_perform(
        current_user, "glucose_reading", "read", patient_profile=profile
    ):
        abort(404)
    return render_template(
        "patient/reading_detail.html",
        reading=reading,
        delete_form=DeleteRecordForm(),
    )


@patient_bp.route("/readings/<int:reading_id>/edit", methods=["GET", "POST"])
@role_required("patient")
def edit_reading(reading_id):
    profile = _current_profile()
    reading = _owned_record(GlucoseReading, reading_id, profile)
    if reading is None:
        abort(404)
    if not can_perform(
        current_user, "glucose_reading", "update", patient_profile=profile
    ):
        abort(403)
    form = GlucoseReadingForm(obj=reading)
    if request.method == "POST":
        if not form.validate_on_submit():
            return render_template(
                "patient/reading_form.html",
                form=form,
                editing=True,
                record_id=reading.id,
            ), 400
        reading.value_demo = form.value_demo.data
        reading.recorded_at = normalize_recorded_at(form.recorded_at.data)
        reading.reading_context = form.reading_context.data.strip() or None
        db.session.commit()
        flash("Your fictional glucose reading was updated.", "success")
        return redirect(url_for("patient.reading_detail", reading_id=reading.id))
    return render_template(
        "patient/reading_form.html",
        form=form,
        editing=True,
        record_id=reading.id,
    )


@patient_bp.post("/readings/<int:reading_id>/delete")
@role_required("patient")
def delete_reading(reading_id):
    profile = _current_profile()
    reading = _owned_record(GlucoseReading, reading_id, profile)
    if reading is None:
        abort(404)
    if not can_perform(
        current_user, "glucose_reading", "delete", patient_profile=profile
    ):
        abort(403)
    form = DeleteRecordForm()
    if not form.validate_on_submit():
        abort(400)
    db.session.delete(reading)
    db.session.commit()
    flash("The fictional glucose reading was deleted.", "success")
    return redirect(url_for("patient.reading_history"))


def _owned_record(model, record_id, profile):
    return db.session.scalar(
        select(model).where(
            model.id == record_id,
            model.patient_id == profile.id,
        )
    )


@patient_bp.get("/meals")
@role_required("patient")
def meal_history():
    profile = _current_profile()
    meals = list(
        db.session.scalars(
            select(MealLog)
            .where(MealLog.patient_id == profile.id)
            .order_by(MealLog.recorded_at.desc())
        )
    )
    return render_template("patient/meals.html", meals=meals)


@patient_bp.get("/meals/new")
@role_required("patient")
def new_meal():
    return render_template(
        "patient/meal_form.html", form=MealLogForm(), editing=False, record_id=None
    )


@patient_bp.post("/meals")
@role_required("patient")
def create_meal():
    profile = _current_profile()
    if not can_perform(
        current_user, "meal_log", "create", patient_profile=profile
    ):
        abort(403)
    form = MealLogForm()
    if not form.validate_on_submit():
        return render_template(
            "patient/meal_form.html", form=form, editing=False, record_id=None
        ), 400

    meal = MealLog(
        patient=profile,
        meal_type=form.meal_type.data,
        description=form.description.data.strip(),
        recorded_at=normalize_recorded_at(form.recorded_at.data),
    )
    db.session.add(meal)
    db.session.commit()
    flash("Your fictional meal entry was recorded.", "success")
    return redirect(url_for("patient.meal_history"))


@patient_bp.get("/meals/<int:meal_id>")
@role_required("patient")
def meal_detail(meal_id):
    profile = _current_profile()
    meal = _owned_record(MealLog, meal_id, profile)
    if meal is None or not can_perform(
        current_user, "meal_log", "read", patient_profile=profile
    ):
        abort(404)
    return render_template(
        "patient/meal_detail.html",
        meal=meal,
        delete_form=DeleteRecordForm(),
    )


@patient_bp.route("/meals/<int:meal_id>/edit", methods=["GET", "POST"])
@role_required("patient")
def edit_meal(meal_id):
    profile = _current_profile()
    meal = _owned_record(MealLog, meal_id, profile)
    if meal is None:
        abort(404)
    if not can_perform(
        current_user, "meal_log", "update", patient_profile=profile
    ):
        abort(403)
    form = MealLogForm(obj=meal)
    if request.method == "POST":
        if not form.validate_on_submit():
            return render_template(
                "patient/meal_form.html",
                form=form,
                editing=True,
                record_id=meal.id,
            ), 400
        meal.meal_type = form.meal_type.data
        meal.description = form.description.data.strip()
        meal.recorded_at = normalize_recorded_at(form.recorded_at.data)
        db.session.commit()
        flash("Your fictional meal entry was updated.", "success")
        return redirect(url_for("patient.meal_detail", meal_id=meal.id))
    return render_template(
        "patient/meal_form.html",
        form=form,
        editing=True,
        record_id=meal.id,
    )


@patient_bp.post("/meals/<int:meal_id>/delete")
@role_required("patient")
def delete_meal(meal_id):
    profile = _current_profile()
    meal = _owned_record(MealLog, meal_id, profile)
    if meal is None:
        abort(404)
    if not can_perform(
        current_user, "meal_log", "delete", patient_profile=profile
    ):
        abort(403)
    form = DeleteRecordForm()
    if not form.validate_on_submit():
        abort(400)
    db.session.delete(meal)
    db.session.commit()
    flash("The fictional meal entry was deleted.", "success")
    return redirect(url_for("patient.meal_history"))


@patient_bp.get("/exercise")
@role_required("patient")
def exercise_history():
    profile = _current_profile()
    exercises = list(
        db.session.scalars(
            select(ExerciseLog)
            .where(ExerciseLog.patient_id == profile.id)
            .order_by(ExerciseLog.recorded_at.desc())
        )
    )
    return render_template("patient/exercise.html", exercises=exercises)


@patient_bp.get("/exercise/new")
@role_required("patient")
def new_exercise():
    return render_template(
        "patient/exercise_form.html",
        form=ExerciseLogForm(),
        editing=False,
        record_id=None,
    )


@patient_bp.post("/exercise")
@role_required("patient")
def create_exercise():
    profile = _current_profile()
    if not can_perform(
        current_user, "exercise_log", "create", patient_profile=profile
    ):
        abort(403)
    form = ExerciseLogForm()
    if not form.validate_on_submit():
        return render_template(
            "patient/exercise_form.html",
            form=form,
            editing=False,
            record_id=None,
        ), 400

    exercise = ExerciseLog(
        patient=profile,
        activity_type=form.activity_type.data.strip(),
        duration_minutes=form.duration_minutes.data,
        recorded_at=normalize_recorded_at(form.recorded_at.data),
    )
    db.session.add(exercise)
    db.session.commit()
    flash("Your fictional exercise entry was recorded.", "success")
    return redirect(url_for("patient.exercise_history"))


@patient_bp.get("/exercise/<int:exercise_id>")
@role_required("patient")
def exercise_detail(exercise_id):
    profile = _current_profile()
    exercise = _owned_record(ExerciseLog, exercise_id, profile)
    if exercise is None or not can_perform(
        current_user, "exercise_log", "read", patient_profile=profile
    ):
        abort(404)
    return render_template(
        "patient/exercise_detail.html",
        exercise=exercise,
        delete_form=DeleteRecordForm(),
    )


@patient_bp.route("/exercise/<int:exercise_id>/edit", methods=["GET", "POST"])
@role_required("patient")
def edit_exercise(exercise_id):
    profile = _current_profile()
    exercise = _owned_record(ExerciseLog, exercise_id, profile)
    if exercise is None:
        abort(404)
    if not can_perform(
        current_user, "exercise_log", "update", patient_profile=profile
    ):
        abort(403)
    form = ExerciseLogForm(obj=exercise)
    if request.method == "POST":
        if not form.validate_on_submit():
            return render_template(
                "patient/exercise_form.html",
                form=form,
                editing=True,
                record_id=exercise.id,
            ), 400
        exercise.activity_type = form.activity_type.data.strip()
        exercise.duration_minutes = form.duration_minutes.data
        exercise.recorded_at = normalize_recorded_at(form.recorded_at.data)
        db.session.commit()
        flash("Your fictional exercise entry was updated.", "success")
        return redirect(
            url_for("patient.exercise_detail", exercise_id=exercise.id)
        )
    return render_template(
        "patient/exercise_form.html",
        form=form,
        editing=True,
        record_id=exercise.id,
    )


@patient_bp.post("/exercise/<int:exercise_id>/delete")
@role_required("patient")
def delete_exercise(exercise_id):
    profile = _current_profile()
    exercise = _owned_record(ExerciseLog, exercise_id, profile)
    if exercise is None:
        abort(404)
    if not can_perform(
        current_user, "exercise_log", "delete", patient_profile=profile
    ):
        abort(403)
    form = DeleteRecordForm()
    if not form.validate_on_submit():
        abort(400)
    db.session.delete(exercise)
    db.session.commit()
    flash("The fictional exercise entry was deleted.", "success")
    return redirect(url_for("patient.exercise_history"))


def _patient_reminders(profile):
    return list(
        db.session.scalars(
            select(MedicationReminder)
            .where(MedicationReminder.patient_id == profile.id)
            .order_by(MedicationReminder.created_at.desc())
        )
    )


def _medication_event_form(profile, event=None):
    reminders = _patient_reminders(profile)
    form = MedicationEventForm(obj=event)
    form.set_reminders(reminders)
    if event is not None and request.method == "GET":
        form.reminder_id.data = str(event.reminder_id or "")
    return form


@patient_bp.get("/reminders")
@role_required("patient")
def reminder_history():
    profile = _current_profile()
    if not can_perform(
        current_user, "medication_reminder", "read", patient_profile=profile
    ):
        abort(404)
    return render_template(
        "patient/reminders.html", reminders=_patient_reminders(profile)
    )


@patient_bp.get("/reminders/<int:reminder_id>")
@role_required("patient")
def reminder_detail(reminder_id):
    profile = _current_profile()
    reminder = _owned_record(MedicationReminder, reminder_id, profile)
    if reminder is None or not can_perform(
        current_user, "medication_reminder", "read", patient_profile=profile
    ):
        abort(404)
    return render_template("patient/reminder_detail.html", reminder=reminder)


@patient_bp.get("/medication-events")
@role_required("patient")
def medication_event_history():
    profile = _current_profile()
    if not can_perform(
        current_user, "medication_event", "read", patient_profile=profile
    ):
        abort(404)
    events = list(
        db.session.scalars(
            select(MedicationEvent)
            .where(MedicationEvent.patient_id == profile.id)
            .order_by(MedicationEvent.recorded_at.desc())
        )
    )
    return render_template("patient/medication_events.html", events=events)


@patient_bp.get("/medication-events/new")
@role_required("patient")
def new_medication_event():
    profile = _current_profile()
    if not can_perform(
        current_user, "medication_event", "create", patient_profile=profile
    ):
        abort(403)
    return render_template(
        "patient/medication_event_form.html",
        form=_medication_event_form(profile),
        editing=False,
        record_id=None,
    )


@patient_bp.post("/medication-events")
@role_required("patient")
def create_medication_event():
    profile = _current_profile()
    if not can_perform(
        current_user, "medication_event", "create", patient_profile=profile
    ):
        abort(403)
    form = _medication_event_form(profile)
    if not form.validate_on_submit():
        return render_template(
            "patient/medication_event_form.html",
            form=form,
            editing=False,
            record_id=None,
        ), 400

    reminder_id = int(form.reminder_id.data) if form.reminder_id.data else None
    event = MedicationEvent(
        patient=profile,
        reminder_id=reminder_id,
        status=form.status.data,
        recorded_at=normalize_recorded_at(form.recorded_at.data),
        context=form.context.data.strip() or None,
    )
    db.session.add(event)
    db.session.commit()
    flash("Your fictional medication event was recorded.", "success")
    return redirect(url_for("patient.medication_event_history"))


@patient_bp.get("/medication-events/<int:event_id>")
@role_required("patient")
def medication_event_detail(event_id):
    profile = _current_profile()
    event = _owned_record(MedicationEvent, event_id, profile)
    if event is None or not can_perform(
        current_user, "medication_event", "read", patient_profile=profile
    ):
        abort(404)
    return render_template(
        "patient/medication_event_detail.html",
        event=event,
        delete_form=DeleteRecordForm(),
    )


@patient_bp.route("/medication-events/<int:event_id>/edit", methods=["GET", "POST"])
@role_required("patient")
def edit_medication_event(event_id):
    profile = _current_profile()
    event = _owned_record(MedicationEvent, event_id, profile)
    if event is None:
        abort(404)
    if not can_perform(
        current_user, "medication_event", "update", patient_profile=profile
    ):
        abort(403)
    form = _medication_event_form(profile, event=event)
    if request.method == "POST":
        if not form.validate_on_submit():
            return render_template(
                "patient/medication_event_form.html",
                form=form,
                editing=True,
                record_id=event.id,
            ), 400
        event.reminder_id = int(form.reminder_id.data) if form.reminder_id.data else None
        event.status = form.status.data
        event.recorded_at = normalize_recorded_at(form.recorded_at.data)
        event.context = form.context.data.strip() or None
        db.session.commit()
        flash("Your fictional medication event was updated.", "success")
        return redirect(
            url_for("patient.medication_event_detail", event_id=event.id)
        )
    return render_template(
        "patient/medication_event_form.html",
        form=form,
        editing=True,
        record_id=event.id,
    )


@patient_bp.post("/medication-events/<int:event_id>/delete")
@role_required("patient")
def delete_medication_event(event_id):
    profile = _current_profile()
    event = _owned_record(MedicationEvent, event_id, profile)
    if event is None:
        abort(404)
    if not can_perform(
        current_user, "medication_event", "delete", patient_profile=profile
    ):
        abort(403)
    form = DeleteRecordForm()
    if not form.validate_on_submit():
        abort(400)
    db.session.delete(event)
    db.session.commit()
    flash("The fictional medication event was deleted.", "success")
    return redirect(url_for("patient.medication_event_history"))
