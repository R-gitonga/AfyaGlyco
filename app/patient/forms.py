from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import DecimalField, StringField, SubmitField
from wtforms.fields import DateTimeLocalField
from wtforms.validators import DataRequired, InputRequired, Length, NumberRange


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
