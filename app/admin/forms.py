"""CSRF-protected forms used by administrator management pages."""

from flask_wtf import FlaskForm
from wtforms import PasswordField, SelectField, StringField, SubmitField
from wtforms.fields.choices import SelectChoice
from wtforms.validators import DataRequired, Length

from app.business_rules import (
    ACCOUNT_DISPLAY_NAME_MAX_LENGTH,
    ACCOUNT_PASSWORD_MIN_LENGTH,
    ORGANIZATION_NAME_MAX_LENGTH,
    ORGANIZATION_TYPE_CHOICES,
)


class AdminActionForm(FlaskForm):
    submit = SubmitField("Confirm")


class OrganizationForm(FlaskForm):
    name = StringField(
        "Organization name",
        validators=[DataRequired(), Length(max=ORGANIZATION_NAME_MAX_LENGTH)],
    )
    organization_type = SelectField(
        "Organization type",
        choices=[SelectChoice(value, label) for value, label in ORGANIZATION_TYPE_CHOICES],
        validators=[DataRequired()],
    )
    submit = SubmitField("Save organization")


class ClinicianRegistrationForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Length(max=255)])
    display_name = StringField(
        "Display name",
        validators=[DataRequired(), Length(max=ACCOUNT_DISPLAY_NAME_MAX_LENGTH)],
    )
    password = PasswordField(
        "Initial local password",
        validators=[DataRequired(), Length(min=ACCOUNT_PASSWORD_MIN_LENGTH, max=255)],
        description="Fictional demo account only; the password is hashed immediately.",
    )
    organization_id = SelectField(
        "Organization",
        choices=[],
        validators=[DataRequired()],
    )
    submit = SubmitField("Register clinician")

    def set_organizations(self, organizations):
        self.organization_id.choices = [
            (str(organization.id), organization.name) for organization in organizations
        ]


class ClinicianEditForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Length(max=255)])
    display_name = StringField(
        "Display name",
        validators=[DataRequired(), Length(max=ACCOUNT_DISPLAY_NAME_MAX_LENGTH)],
    )
    organization_id = SelectField(
        "Organization",
        choices=[],
        validators=[DataRequired()],
    )
    submit = SubmitField("Save clinician")

    def set_organizations(self, organizations):
        self.organization_id.choices = [
            (str(organization.id), organization.name) for organization in organizations
        ]


class PatientAssignmentForm(FlaskForm):
    clinician_id = SelectField(
        "Assigned clinician",
        choices=[],
    )
    submit = SubmitField("Save assignment")

    def set_clinicians(self, clinicians):
        self.clinician_id.choices = [("", "Unassigned")] + [
            (str(clinician.id), clinician.email) for clinician in clinicians
        ]
