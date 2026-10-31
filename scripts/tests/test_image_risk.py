"""Security gate contract: risk acceptance must never become a blanket bypass."""
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from check_image_risk import evaluate, read_policy


class RiskPolicyTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 31, tzinfo=timezone.utc)
        self.match = {
            "vulnerability": {"id": "CVE-example", "namespace": "debian:13",
                "severity": "High", "fix": {"state": "wont-fix", "versions": []}},
            "artifact": {"type": "deb", "name": "example", "version": "1.0"},
        }
        self.report = {
            "descriptor": {"name": "grype", "db": {"status": {
                "valid": True, "built": self.now.isoformat()}}},
            "source": {"type": "image", "target": {
                "imageID": "sha256:example", "architecture": "amd64"}},
            "matches": [self.match],
        }
        self.rule = {"vulnerability": "CVE-example", "namespace": "debian:13",
            "scope": "image", "roles": ["web"], "package_type": "deb",
            "packages": {"example": "1.0"}, "fix_states": ["wont-fix"],
            "reason": "Explicit release risk acceptance"}
        self.policy = {"rules": [self.rule]}

    def check(self, role="web", scope="image", sbom=None):
        return evaluate(self.report, self.policy, role, "sha256:example", scope, self.now, sbom)

    def test_exact_reviewed_finding_passes_without_mutating_evidence(self):
        original = copy.deepcopy(self.report)
        self.assertEqual(tuple(map(len, self.check())), (1, 0))
        self.assertEqual(self.report, original)

    def test_new_identity_always_blocks(self):
        for section, field, value in [
            ("artifact", "name", "new"), ("artifact", "version", "1.1"),
            ("artifact", "type", "rpm"), ("vulnerability", "id", "CVE-new"),
            ("vulnerability", "namespace", "other"),
        ]:
            with self.subTest(field=field):
                original = self.match[section][field]
                self.match[section][field] = value
                self.assertEqual(len(self.check()[1]), 1)
                self.match[section][field] = original

    def test_critical_unknown_and_invalid_severity_never_pass(self):
        for severity in ["Critical", "Unknown"]:
            self.match["vulnerability"]["severity"] = severity
            self.assertEqual(len(self.check()[1]), 1)
        self.match["vulnerability"]["severity"] = "invalid"
        with self.assertRaises(ValueError): self.check()

    def test_available_fix_blocks(self):
        self.match["vulnerability"]["fix"]["versions"] = ["1.1"]
        self.assertIn("fix available", self.check()[1][0])
        self.match["vulnerability"]["fix"] = {"state": "fixed", "versions": []}
        self.assertIn("fix available", self.check()[1][0])

    def test_changed_fix_status_blocks(self):
        self.match["vulnerability"]["fix"]["state"] = "unknown"
        self.assertEqual(len(self.check()[1]), 1)

    def test_known_exploitation_blocks(self):
        self.match["vulnerability"]["knownExploited"] = [{"cve": "CVE-example"}]
        self.assertIn("known exploitation", self.check()[1][0])

    def test_roles_are_not_interchangeable(self):
        self.assertEqual(len(self.check(role="mysql")[1]), 1)
        self.assertEqual(len(self.check(role="nginx")[1]), 1)

    def test_invalid_database_age_or_scanner_is_rejected(self):
        db = self.report["descriptor"]["db"]["status"]
        for change in [{"valid": False}, {"built": "2026-10-01T00:00:00Z"},
                       {"built": "2026-11-01T00:00:00Z"}]:
            original = db.copy()
            db.update(change)
            with self.assertRaises(ValueError): self.check()
            db.update(original)
        self.report["descriptor"]["name"] = "other"
        with self.assertRaises(ValueError): self.check()

    def test_wrong_image_or_architecture_is_rejected(self):
        for field, value in [("imageID", "sha256:other"), ("architecture", "arm64")]:
            original = self.report["source"]["target"][field]
            self.report["source"]["target"][field] = value
            with self.assertRaises(ValueError): self.check()
            self.report["source"]["target"][field] = original

    def test_missing_or_invalid_match_list_is_rejected(self):
        self.report["matches"] = None
        with self.assertRaises(ValueError): self.check()
        del self.report["matches"]
        with self.assertRaises(KeyError): self.check()

    def test_clean_report_passes_without_hiding_matches(self):
        self.report["matches"] = []
        self.assertEqual(self.check(), ([], []))

    def test_native_report_requires_matching_image_and_inventory(self):
        self.report["source"] = {"type": "sbom-file", "target": "/sbom.json"}
        self.rule["scope"] = "python-expat"
        self.rule["packages"] = {"expat": "1.0"}
        self.match["artifact"]["name"] = "expat"
        sbom = {"metadata": {"properties": [
            {"name": "cermed:image-id", "value": "sha256:example"},
            {"name": "cermed:architecture", "value": "amd64"}]},
            "components": [{"name": "expat", "version": "1.0"}]}
        self.assertEqual(len(self.check(scope="python-expat", sbom=sbom)[0]), 1)
        sbom["components"][0]["version"] = "different"
        self.assertEqual(len(self.check(scope="python-expat", sbom=sbom)[1]), 1)
        sbom["metadata"]["properties"][0]["value"] = "sha256:other"
        with self.assertRaises(ValueError): self.check(scope="python-expat", sbom=sbom)

    def test_runtime_changes_require_a_new_review(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            runtime = root / "Dockerfile"
            runtime.write_text("reviewed runtime")
            policy = {"schema": 1, "acceptance": "approved", "rules": [self.rule],
                "reviewed_files": {"Dockerfile": hashlib.sha256(runtime.read_bytes()).hexdigest()}}
            path = root / "policy.json"
            path.write_text(json.dumps(policy))
            read_policy(path, root)
            runtime.write_text("different runtime")
            with self.assertRaisesRegex(ValueError, "Runtime changed"):
                read_policy(path, root)


if __name__ == "__main__":
    unittest.main()
