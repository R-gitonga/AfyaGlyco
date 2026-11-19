from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

from app.business_rules import MEDICATION_LABEL_MAX_LENGTH, REMINDER_SCHEDULE_MAX_LENGTH


class ClinicianNoteForm(FlaskForm):
    note = TextAreaField(
        "Feedback or follow-up note",
        validators=[DataRequired(), Length(max=2000)],
    )
    submit = SubmitField("Save note")


class MedicationReminderForm(FlaskForm):
    medication_label_demo = StringField(
        "Medication label for demonstration",
        validators=[DataRequired(), Length(max=MEDICATION_LABEL_MAX_LENGTH)],
        description="Use fictional or seeded content only; do not enter dosage instructions.",
    )
    schedule_description = TextAreaField(
        "Schedule description",
        validators=[DataRequired(), Length(max=REMINDER_SCHEDULE_MAX_LENGTH)],
        description="For example: morning reminder or evening reminder.",
    )
    is_active = BooleanField("Reminder is active", default=True)
    submit = SubmitField("Save reminder")


class DeleteReminderForm(FlaskForm):
    submit = SubmitField("Delete reminder")
