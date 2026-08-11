import logging
import os
import threading
import time
import uuid

from django.conf import settings
from django.db import OperationalError, connection
from django.http import HttpResponse

from gym.db_instrumentation import write_request_context
from gym.slow_requests import active_request_registry


logger = logging.getLogger("cermed.db_writes")
request_logger = logging.getLogger("cermed.request_timing")

WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
LOCK_ERROR_CODES = {1205: "lock_wait_timeout", 1213: "deadlock"}


def _user_details(request):
    user = getattr(request, "user", None)
    if user is None or not getattr(user, "is_authenticated", False):
        return None, "anonymous"

    username = user.get_username() if hasattr(user, "get_username") else str(user)
    return getattr(user, "pk", None), username


def _operational_error_code(exception):
    if exception.args and isinstance(exception.args[0], int):
        return exception.args[0]
    return None


class QueryTracker:
    def __init__(self, request, slow_query_ms):
        self.request = request
        self.slow_query_ms = slow_query_ms
        self.query_count = 0
        self.database_time_ms = 0.0

    def __call__(self, execute, sql, params, many, context):
        started_at = time.monotonic()
        try:
            return execute(sql, params, many, context)
        finally:
            duration_ms = (time.monotonic() - started_at) * 1000
            self.query_count += 1
            self.database_time_ms += duration_ms

            if duration_ms >= self.slow_query_ms:
                request_logger.warning(
                    "[DB-QUERY] slow_sql request_id=%s view=%s user_id=%s "
                    "duration_ms=%.2f sql=%s",
                    self.request.write_request_id,
                    getattr(self.request, "write_view_name", "unresolved"),
                    _user_details(self.request)[0],
                    duration_ms,
                    " ".join(sql.split())[:2000],
                )


class WriteDatabaseInstrumentationMiddleware:
    """Instrument all requests and turn write lock errors into retryable 503s."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.enabled = getattr(settings, "REQUEST_INSTRUMENTATION_ENABLED", True)
        self.slow_query_ms = getattr(settings, "DB_SLOW_QUERY_MS", 250)
        self.slow_request_ms = getattr(settings, "SLOW_REQUEST_LOG_MS", 2000)
        self.stack_after_ms = getattr(settings, "SLOW_REQUEST_STACK_MS", 10000)

    def __call__(self, request):
        if not self.enabled:
            return self.get_response(request)

        request.write_request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        request.write_view_name = "unresolved"
        request.write_started_at = time.monotonic()
        tracker = QueryTracker(request, self.slow_query_ms)

        user_id, username = _user_details(request)
        context_token = write_request_context.set(
            {
                "request_id": request.write_request_id,
                "view": request.write_view_name,
                "user_id": user_id,
            }
        )
        if request.method in WRITE_METHODS:
            logger.info(
                "[DB-WRITE] start request_id=%s method=%s path=%s user_id=%s username=%s",
                request.write_request_id,
                request.method,
                request.path,
                user_id,
                username,
            )

        active_request_registry.register(
            request.write_request_id,
            request.method,
            request.path,
            self.stack_after_ms,
        )

        response = None
        with connection.execute_wrapper(tracker):
            try:
                response = self.get_response(request)
                return response
            finally:
                duration_ms = (time.monotonic() - request.write_started_at) * 1000
                final_user_id, final_username = _user_details(request)
                active_request_registry.unregister(request.write_request_id)
                if duration_ms >= self.slow_request_ms:
                    request_logger.warning(
                        "[SLOW-REQUEST] finish request_id=%s method=%s path=%s view=%s "
                        "user_id=%s username=%s status=%s duration_ms=%.2f queries=%s db_time_ms=%.2f "
                        "pid=%s thread_id=%s",
                        request.write_request_id,
                        request.method,
                        request.path,
                        request.write_view_name,
                        final_user_id,
                        final_username,
                        getattr(response, "status_code", "exception"),
                        duration_ms,
                        tracker.query_count,
                        tracker.database_time_ms,
                        os.getpid(),
                        threading.get_ident(),
                    )
                if request.method in WRITE_METHODS:
                    logger.info(
                        "[DB-WRITE] finish request_id=%s method=%s path=%s view=%s "
                        "user_id=%s status=%s duration_ms=%.2f queries=%s "
                        "db_time_ms=%.2f autocommit=%s",
                        request.write_request_id,
                        request.method,
                        request.path,
                        request.write_view_name,
                        final_user_id,
                        getattr(response, "status_code", "exception"),
                        duration_ms,
                        tracker.query_count,
                        tracker.database_time_ms,
                        connection.get_autocommit(),
                    )
                write_request_context.reset(context_token)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not self.enabled:
            return None

        view_class = getattr(view_func, "view_class", None)
        if view_class is not None:
            view_name = f"{view_class.__module__}.{view_class.__name__}"
        else:
            view_name = f"{view_func.__module__}.{view_func.__name__}"

        request.write_view_name = view_name
        context = write_request_context.get()
        if context is not None:
            context["view"] = view_name
        active_request_registry.update_view(request.write_request_id, view_name)
        if request.method in WRITE_METHODS:
            logger.info(
                "[DB-WRITE] resolved request_id=%s view=%s",
                getattr(request, "write_request_id", "missing"),
                view_name,
            )
        return None

    def process_exception(self, request, exception):
        if request.method not in WRITE_METHODS or not isinstance(exception, OperationalError):
            return None

        error_code = _operational_error_code(exception)
        error_kind = LOCK_ERROR_CODES.get(error_code)
        if error_kind is None:
            logger.error(
                "[DB-WRITE] operational_error request_id=%s view=%s user_id=%s "
                "db_error_code=%s error=%s",
                getattr(request, "write_request_id", "missing"),
                getattr(request, "write_view_name", "unresolved"),
                _user_details(request)[0],
                error_code,
                exception,
            )
            return None

        logger.error(
            "[DB-WRITE] lock_error request_id=%s view=%s user_id=%s "
            "db_error_code=%s error_kind=%s error=%s",
            getattr(request, "write_request_id", "missing"),
            getattr(request, "write_view_name", "unresolved"),
            _user_details(request)[0],
            error_code,
            error_kind,
            exception,
        )
        response = HttpResponse(
            "La operacion no pudo completarse por contencion de base de datos. "
            "Espere un momento y vuelva a intentar.",
            status=503,
            content_type="text/plain; charset=utf-8",
        )
        response["Retry-After"] = "1"
        return response
