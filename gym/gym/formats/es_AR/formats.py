"""Preserve input formats used before Django removed USE_L10N=False.

Root templates use localize off for their existing unlocalized output. Explicit
floatformat filters retain Django's Spanish decimal/grouping conventions.
"""

from django.conf.global_settings import (  # noqa: F401
    DATE_INPUT_FORMATS,
    DATETIME_INPUT_FORMATS,
    TIME_INPUT_FORMATS,
)

DATE_FORMAT = "d/m/Y"
TIME_FORMAT = "H:i"
DATETIME_FORMAT = "d/m/Y H:i:s"
