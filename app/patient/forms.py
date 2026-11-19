from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import DecimalField, IntegerField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.fields import DateTimeLocalField
from wtforms.fields.choices import SelectChoice
from wtforms.validators import DataRequired, InputRequired, Length, NumberRange

from app.business_rules import (
    EXERCISE_ACTIVITY_MAX_LENGTH,
    EXERCISE_DURATION_MINUTES_MAX,
    EXERCISE_DURATION_MINUTES_MIN,
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
        description="Describe the fictional meal without nutritional interpretation.",
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
