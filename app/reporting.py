from collections import Counter
from datetime import datetime, time, timedelta, timezone
from decimal import Decimal

from sqlalchemy import select

from app import db
from app.business_rules import MEDICATION_EVENT_STATUS_CHOICES
from app.models import (
    ExerciseLog,
    GlucoseReading,
    MealLog,
    MedicationEvent,
    MedicationReminder,
)


def _period_bounds(start_date=None, end_date=None):
    if start_date is None or end_date is None:
        return None, None
    start = datetime.combine(start_date, time.min, tzinfo=timezone.utc)
    end = datetime.combine(
        end_date + timedelta(days=1), time.min, tzinfo=timezone.utc
    )
    return start, end


def _records_for(model, patient_id, recorded_field, start, end):
    statement = select(model).where(model.patient_id == patient_id)
    if start is not None and end is not None:
        statement = statement.where(
            recorded_field >= start,
            recorded_field < end,
        )
    return list(db.session.scalars(statement.order_by(recorded_field.asc())))


def _trend_bars(readings):
    if not readings:
        return []

    values = [Decimal(reading.value_demo) for reading in readings]
    minimum = min(values)
    span = max(values) - minimum or Decimal("1")
    return [
        {
            "height": 28 + int(((value - minimum) / span) * 62),
            "label": reading.recorded_at.strftime("%d %b"),
            "value": f"{value:.2f}",
        }
        for reading, value in zip(readings, values)
    ]


def build_patient_report(patient_profile, *, start_date=None, end_date=None):
    """Build a read-only summary from records already scoped to one patient."""
    start, end = _period_bounds(start_date, end_date)
    readings = _records_for(
        GlucoseReading,
        patient_profile.id,
        GlucoseReading.recorded_at,
        start,
        end,
    )
    meals = _records_for(
        MealLog,
        patient_profile.id,
        MealLog.recorded_at,
        start,
        end,
    )
    exercises = _records_for(
        ExerciseLog,
        patient_profile.id,
        ExerciseLog.recorded_at,
        start,
        end,
    )
    medication_events = _records_for(
        MedicationEvent,
        patient_profile.id,
        MedicationEvent.recorded_at,
        start,
        end,
    )
    reminders = list(
        db.session.scalars(
            select(MedicationReminder)
            .where(MedicationReminder.patient_id == patient_profile.id)
            .order_by(MedicationReminder.created_at.desc())
        )
    )

    status_counts = Counter(event.status for event in medication_events)
    status_summary = [
        {
            "label": label,
            "value": status_counts.get(value, 0),
        }
        for value, label in MEDICATION_EVENT_STATUS_CHOICES
    ]
    recorded_times = [
        record.recorded_at
        for records in (readings, meals, exercises, medication_events)
        for record in records
    ]
    return {
        "readings": readings,
        "meals": meals,
        "exercises": exercises,
        "medication_events": medication_events,
        "reminders": reminders,
        "trend_bars": _trend_bars(readings),
        "status_summary": status_summary,
        "counts": {
            "readings": len(readings),
            "meals": len(meals),
            "exercises": len(exercises),
            "medication_events": len(medication_events),
        },
        "reminder_count": len(reminders),
        "active_reminder_count": sum(1 for reminder in reminders if reminder.is_active),
        "first_recorded_at": min(recorded_times) if recorded_times else None,
        "last_recorded_at": max(recorded_times) if recorded_times else None,
        "has_records": bool(recorded_times),
        "start_date": start_date,
        "end_date": end_date,
    }
