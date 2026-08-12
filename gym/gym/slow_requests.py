import logging
import os
import sys
import threading
import time
import traceback

from django.conf import settings


logger = logging.getLogger("cermed.request_timing")


class ActiveRequestRegistry:
    """Tracks active request threads and emits one stack snapshot when overdue."""

    def __init__(self):
        self._active = {}
        self._lock = threading.Lock()
        self._watchdog = None
        self._pid = None

    def register(self, request_id, method, path, stack_after_ms):
        if not getattr(settings, "SLOW_REQUEST_WATCHDOG_ENABLED", False):
            return

        pid = os.getpid()
        with self._lock:
            if self._pid != pid:
                self._active = {}
                self._watchdog = None
                self._pid = pid

            self._active[request_id] = {
                "pid": pid,
                "thread_id": threading.get_ident(),
                "method": method,
                "path": path,
                "view": "unresolved",
                "started_at": time.monotonic(),
                "stack_after_ms": stack_after_ms,
                "stack_logged": False,
            }
            if self._watchdog is None or not self._watchdog.is_alive():
                self._watchdog = threading.Thread(
                    target=self._run,
                    name="cermed-slow-request-watchdog",
                    daemon=True,
                )
                self._watchdog.start()

    def update_view(self, request_id, view_name):
        with self._lock:
            active_request = self._active.get(request_id)
            if active_request is not None:
                active_request["view"] = view_name

    def unregister(self, request_id):
        with self._lock:
            self._active.pop(request_id, None)

    def _run(self):
        while True:
            time.sleep(1)
            if self.emit_overdue_stacks() == 0:
                return

    def emit_overdue_stacks(self):
        now = time.monotonic()
        with self._lock:
            active_requests = list(self._active.items())

        for request_id, details in active_requests:
            elapsed_ms = (now - details["started_at"]) * 1000
            if details["stack_logged"] or elapsed_ms < details["stack_after_ms"]:
                continue

            frame = sys._current_frames().get(details["thread_id"])
            stack = (
                "".join(traceback.format_stack(frame, limit=80))
                if frame
                else "<thread frame unavailable>"
            )
            with self._lock:
                current = self._active.get(request_id)
                if current is None or current["stack_logged"]:
                    continue
                current["stack_logged"] = True

            logger.warning(
                "[SLOW-REQUEST] stack request_id=%s elapsed_ms=%.2f pid=%s "
                "thread_id=%s method=%s path=%s view=%s\n%s",
                request_id,
                elapsed_ms,
                details["pid"],
                details["thread_id"],
                details["method"],
                details["path"],
                details["view"],
                stack,
            )

        with self._lock:
            return len(self._active)


active_request_registry = ActiveRequestRegistry()

