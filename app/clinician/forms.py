"""Validated forms for clinician review and patient-register workflows."""

from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

from app.business_rules import (
    ACCOUNT_DISPLAY_NAME_MAX_LENGTH,
    ACCOUNT_PASSWORD_MIN_LENGTH,
    MEDICATION_LABEL_MAX_LENGTH,
    REMINDER_SCHEDULE_MAX_LENGTH,
)


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
        description="Use seeded content only; do not enter dosage instructions.",
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


class PatientRegistrationForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Length(max=255)])
    display_name = StringField(
        "Display name",
        validators=[DataRequired(), Length(max=ACCOUNT_DISPLAY_NAME_MAX_LENGTH)],
    )
    password = PasswordField(
        "Initial local password",
        validators=[DataRequired(), Length(min=ACCOUNT_PASSWORD_MIN_LENGTH, max=255)],
        description="demo account only; the password is hashed immediately.",
    )
    submit = SubmitField("Register patient")


class ExistingPatientForm(FlaskForm):
    patient_id = SelectField(
        "Unassigned patient account",
        choices=[],
        validators=[DataRequired()],
    )
    submit = SubmitField("Add patient to register")

    def set_patients(self, patients):
        self.patient_id.choices = [
            (str(patient.id), f"{patient.display_name} · {patient.user.email}")
            for patient in patients
        ]
