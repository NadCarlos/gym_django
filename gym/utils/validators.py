from datetime import date, datetime

from django.core.exceptions import ValidationError


MIN_VALID_DATE = date(1900, 1, 1)


def validate_date_not_before_1900(value):
    if value is None:
        return

    value_date = value.date() if isinstance(value, datetime) else value
    if value_date < MIN_VALID_DATE:
        raise ValidationError(
            "La fecha no puede ser anterior al 01/01/1900.",
            code="date_before_1900",
        )
