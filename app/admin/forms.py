from flask_wtf import FlaskForm
from wtforms import SubmitField


class AdminActionForm(FlaskForm):
    submit = SubmitField("Confirm")
