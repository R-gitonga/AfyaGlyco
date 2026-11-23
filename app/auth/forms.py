from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length


class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[DataRequired(), Length(max=255)],
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(max=255)],
    )
    submit = SubmitField("Sign in")


class BootstrapAdminForm(FlaskForm):
    """Validate the one-time first-administrator setup form."""

    email = StringField(
        "Administrator email",
        validators=[DataRequired(), Length(max=255)],
    )
    display_name = StringField(
        "Display name",
        validators=[DataRequired(), Length(max=120)],
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=12, max=255)],
    )
    confirm_password = PasswordField(
        "Confirm password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match."),
        ],
    )
    submit = SubmitField("Create administrator")
