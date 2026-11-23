from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import (
    DecimalField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.fields import DateTimeLocalField
from wtforms.fields.choices import SelectChoice
from wtforms.validators import DataRequired, InputRequired, Length, NumberRange

from app.business_rules import (
    EXERCISE_ACTIVITY_MAX_LENGTH,
    EXERCISE_DURATION_MINUTES_MAX,
    EXERCISE_DURATION_MINUTES_MIN,
    MEDICATION_EVENT_CONTEXT_MAX_LENGTH,
    MEDICATION_EVENT_STATUS_CHOICES,
    MEAL_DESCRIPTION_MAX_LENGTH,
    MEAL_TYPE_CHOICES,
)


class GlucoseReadingForm(FlaskForm):
    value_demo = DecimalField(
        "Recorded demo value",
        places=2,
        rounding=None,
        validators=[InputRequired(), NumberRange(min=0)],
    )
    recorded_at = DateTimeLocalField(
        "Date and time recorded",
        format="%Y-%m-%dT%H:%M",
        default=lambda: datetime.now().replace(second=0, microsecond=0),
        validators=[DataRequired()],
    )
    reading_context = StringField(
        "Context (optional)",
        validators=[Length(max=80)],
        description="For example: before breakfast or demo entry.",
    )
    submit = SubmitField("Save reading")


class MealLogForm(FlaskForm):
    meal_type = SelectField(
        "Meal type",
        choices=[SelectChoice(value, label) for value, label in MEAL_TYPE_CHOICES],
        validators=[DataRequired()],
    )
    description = TextAreaField(
        "Meal description",
        validators=[DataRequired(), Length(max=MEAL_DESCRIPTION_MAX_LENGTH)],
        description="Describe the meal without nutritional interpretation.",
    )
    recorded_at = DateTimeLocalField(
        "Date and time recorded",
        format="%Y-%m-%dT%H:%M",
        default=lambda: datetime.now().replace(second=0, microsecond=0),
        validators=[DataRequired()],
    )
    submit = SubmitField("Save meal")


class ExerciseLogForm(FlaskForm):
    activity_type = StringField(
        "Activity type",
        validators=[DataRequired(), Length(max=EXERCISE_ACTIVITY_MAX_LENGTH)],
        description="For example: walking or stretching.",
    )
    duration_minutes = IntegerField(
        "Duration in minutes",
        validators=[
            InputRequired(),
            NumberRange(
                min=EXERCISE_DURATION_MINUTES_MIN,
                max=EXERCISE_DURATION_MINUTES_MAX,
            ),
        ],
    )
    recorded_at = DateTimeLocalField(
        "Date and time recorded",
        format="%Y-%m-%dT%H:%M",
        default=lambda: datetime.now().replace(second=0, microsecond=0),
        validators=[DataRequired()],
    )
    submit = SubmitField("Save exercise")


class DeleteRecordForm(FlaskForm):
    submit = SubmitField("Delete record")


class MedicationEventForm(FlaskForm):
    reminder_id = SelectField("Reminder", choices=[])
    status = SelectField(
        "Event status",
        choices=[
            SelectChoice(value, label)
            for value, label in MEDICATION_EVENT_STATUS_CHOICES
        ],
        validators=[DataRequired()],
    )
    recorded_at = DateTimeLocalField(
        "Date and time recorded",
        format="%Y-%m-%dT%H:%M",
        default=lambda: datetime.now().replace(second=0, microsecond=0),
        validators=[DataRequired()],
    )
    context = TextAreaField(
        "Optional context",
        validators=[Length(max=MEDICATION_EVENT_CONTEXT_MAX_LENGTH)],
        description="Record only what you entered; the system does not interpret it.",
    )
    submit = SubmitField("Save medication event")

    def set_reminders(self, reminders):
        self.reminder_id.choices = [("", "No linked reminder")] + [
            (str(reminder.id), reminder.medication_label_demo)
            for reminder in reminders
        ]
