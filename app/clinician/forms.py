from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class ClinicianNoteForm(FlaskForm):
    note = TextAreaField(
        "Feedback or follow-up note",
        validators=[DataRequired(), Length(max=2000)],
    )
    submit = SubmitField("Save note")
