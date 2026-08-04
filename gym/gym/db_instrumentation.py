import logging
import time
from contextlib import contextmanager
from contextvars import ContextVar

from django.conf import settings
from django.db import transaction


logger = logging.getLogger("cermed.db_writes")

write_request_context = ContextVar("write_request_context", default=None)


@contextmanager
def instrumented_atomic(operation):
    """Measure the exact scope of a critical explicit transaction."""
    started_at = time.monotonic()
    status = "rollback"
    try:
        with transaction.atomic():
            yield
        status = "commit"
    finally:
        if getattr(settings, "WRITE_DB_INSTRUMENTATION_ENABLED", True):
            context = write_request_context.get() or {}
            logger.info(
                "[DB-WRITE] transaction request_id=%s view=%s user_id=%s "
                "operation=%s status=%s duration_ms=%.2f",
                context.get("request_id", "outside_request"),
                context.get("view", "unresolved"),
                context.get("user_id"),
                operation,
                status,
                (time.monotonic() - started_at) * 1000,
            )
