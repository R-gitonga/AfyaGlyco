from datetime import timedelta

from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.fields import DateField
from wtforms.validators import Optional

from app.business_rules import REPORT_DATE_FORMAT, REPORT_MAX_DATE_RANGE_DAYS


class ReportFilterForm(FlaskForm):
    """Optional GET filters for a derived report.

    Reports do not change application state, so this form intentionally does
    not use CSRF validation. Mutation forms remain CSRF-protected elsewhere.
    """

    class Meta:
        csrf = False

    start_date = DateField(
        "Start date",
        format=REPORT_DATE_FORMAT,
        validators=[Optional()],
    )
    end_date = DateField(
        "End date",
        format=REPORT_DATE_FORMAT,
        validators=[Optional()],
    )
    submit = SubmitField("Apply dates")

    def validate(self, extra_validators=None):
        is_valid = super().validate(extra_validators=extra_validators)
        has_start = self.start_date.data is not None
        has_end = self.end_date.data is not None

        if has_start != has_end:
            message = "Enter both a start date and an end date."
            if not has_start:
                self.start_date.errors.append(message)
            if not has_end:
                self.end_date.errors.append(message)
            is_valid = False

        if has_start and has_end:
            if self.start_date.data > self.end_date.data:
                self.end_date.errors.append("End date must be on or after the start date.")
                is_valid = False
            elif (
                self.end_date.data - self.start_date.data
            ) > timedelta(days=REPORT_MAX_DATE_RANGE_DAYS - 1):
                self.end_date.errors.append(
                    f"Choose a date range of {REPORT_MAX_DATE_RANGE_DAYS} days or less."
                )
                is_valid = False

        return is_valid
