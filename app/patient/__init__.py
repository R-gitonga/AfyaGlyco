from datetime import timezone
from decimal import Decimal

from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user
from sqlalchemy import select

from app import db
from app.auth.permissions import role_required
from app.models import GlucoseReading, PatientProfile
from app.patient.forms import GlucoseReadingForm


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
    readings = list(
        db.session.scalars(
            select(GlucoseReading)
            .where(GlucoseReading.patient_id == profile.id)
            .order_by(GlucoseReading.recorded_at.desc())
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
    )


@patient_bp.get("/readings/new")
@role_required("patient")
def new_reading():
    return render_template(
        "patient/reading_form.html",
        form=GlucoseReadingForm(),
    )


@patient_bp.post("/readings")
@role_required("patient")
def create_reading():
    form = GlucoseReadingForm()
    if not form.validate_on_submit():
        return render_template("patient/reading_form.html", form=form), 400

    reading = GlucoseReading(
        patient=_current_profile(),
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
    if reading is None:
        abort(404)
    return render_template("patient/reading_detail.html", reading=reading)
