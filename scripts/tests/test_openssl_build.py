"""Build failures must remain visible even after verbose parallel compiler output."""
import contextlib
import importlib.util
import io
from pathlib import Path
import sys
import tempfile
import unittest

spec = importlib.util.spec_from_file_location(
    "run_openssl_build", Path(__file__).resolve().parents[1] / "run-openssl-build.py",
)
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


class OpenSSLBuildTests(unittest.TestCase):
    def run_child(self, code):
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / "build.log"
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                status = build.run_build([sys.executable, "-c", code], log)
            return status, output.getvalue(), log.read_text()

    def test_early_compiler_failure_survives_large_output(self):
        status, output, log = self.run_child(
            "import sys; print('gcc: fatal error: Killed signal terminated program cc1'); "
            "print('gcc compiling another object\\n' * 40000); sys.exit(2)"
        )
        self.assertEqual(status, 2)
        self.assertIn("fatal error: Killed", output)
        self.assertIn("fatal error: Killed", "\n".join(output.splitlines()[-2:]))
        self.assertIn("exit=2", output)
        self.assertIn("gcc compiling another object", log)
        self.assertLess(len(output), 50000)

    def test_failure_without_recognized_error_still_shows_tail(self):
        status, output, _ = self.run_child("import sys; print('unexpected build stop'); sys.exit(7)")
        self.assertEqual(status, 7)
        self.assertIn("unexpected build stop", output)

    def test_success_preserves_artifact_and_caps_parallelism(self):
        status, output, log = self.run_child(
            "import os; value = os.environ['DEB_BUILD_OPTIONS']; "
            "assert value in ('parallel=1', 'parallel=2'); print('package built')"
        )
        self.assertEqual(status, 0)
        self.assertIn("package built", log)
        self.assertIn("PASS", output)
