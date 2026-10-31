#!/usr/bin/env python3
"""Fail closed on findings outside the explicitly reviewed release risk policy."""
import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

SEVERITIES = {"Negligible", "Low", "Medium", "High", "Critical", "Unknown"}


def timestamp(value):
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("Timezone required")
    return result


def read_policy(path, root):
    policy = json.loads(path.read_text())
    if policy["schema"] != 1 or not policy["acceptance"] or not policy["rules"]:
        raise ValueError("Missing reviewed policy")
    if not policy["reviewed_files"]:
        raise ValueError("Missing runtime configuration binding")
    for name, expected in policy["reviewed_files"].items():
        file = (root / name).resolve()
        if not file.is_relative_to(root.resolve()):
            raise ValueError("Policy file outside repository")
        if hashlib.sha256(file.read_bytes()).hexdigest() != expected:
            raise ValueError(f"Runtime changed; review policy again: {name}")
    for rule in policy["rules"]:
        if not rule["reason"] or not rule["packages"]:
            raise ValueError("Incomplete risk rule")
        if not set(rule["roles"]) <= {"web", "nginx"}:
            raise ValueError("Unreviewed role")
        if rule["scope"] not in {"image", "python-expat"}:
            raise ValueError("Unreviewed scope")
    return policy


def evaluate(report, policy, role, image_id, scope, now, sbom=None):
    descriptor = report["descriptor"]
    db = descriptor["db"]["status"]
    if descriptor["name"] != "grype" or db["valid"] is not True:
        raise ValueError("Invalid scanner database")
    age = now - timestamp(db["built"])
    if not -timedelta(hours=1) <= age <= timedelta(days=5):
        raise ValueError("Stale or future scanner database")
    source = report["source"]
    if scope == "image":
        if source["type"] != "image" or source["target"]["imageID"] != image_id:
            raise ValueError("Report belongs to another image")
        if source["target"]["architecture"] != "amd64":
            raise ValueError("Architecture not reviewed")
    elif scope == "python-expat":
        if source != {"type": "sbom-file", "target": "/sbom.json"} or sbom is None:
            raise ValueError("Missing native SBOM evidence")
        properties = {p["name"]: p["value"] for p in sbom["metadata"]["properties"]}
        if properties["cermed:image-id"] != image_id:
            raise ValueError("SBOM belongs to another image")
        if properties["cermed:architecture"] != "amd64":
            raise ValueError("Architecture not reviewed")
        if len(sbom["components"]) != 1 or sbom["components"][0]["name"] != "expat":
            raise ValueError("Unexpected native SBOM")
    else:
        raise ValueError("Unknown report scope")
    if not isinstance(report["matches"], list):
        raise ValueError("Missing match list")
    accepted, blocked = [], []
    for match in report["matches"]:
        vulnerability, artifact = match["vulnerability"], match["artifact"]
        severity = vulnerability["severity"]
        if severity not in SEVERITIES:
            raise ValueError("Unknown severity value")
        if severity not in {"High", "Critical", "Unknown"}:
            continue
        finding = f'{vulnerability["id"]} {artifact["name"]}={artifact["version"]} ({severity})'
        fix = vulnerability["fix"]
        if not isinstance(fix["versions"], list):
            raise ValueError("Invalid fix data")
        rule = next((r for r in policy["rules"] if
            role in r["roles"] and scope == r["scope"]
            and vulnerability["id"] == r["vulnerability"]
            and vulnerability["namespace"] == r["namespace"]
            and artifact["type"] == r["package_type"]
            and r["packages"].get(artifact["name"]) == artifact["version"]), None)
        if severity != "High":
            reason = "Critical/Unknown is never accepted"
        elif fix["versions"] or fix["state"] == "fixed":
            reason = "fix available; update required"
        elif vulnerability.get("knownExploited"):
            reason = "known exploitation requires review"
        elif rule is None:
            reason = "not in the reviewed release policy"
        elif fix["state"] not in rule["fix_states"]:
            reason = "fix assessment changed"
        elif scope == "python-expat" and artifact["version"] != sbom["components"][0]["version"]:
            reason = "report and native inventory disagree"
        else:
            accepted.append(finding)
            continue
        blocked.append(f"{finding}: {reason}")
    return accepted, blocked


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--role", choices=["web", "nginx", "mysql"], required=True)
    parser.add_argument("--image-id", required=True)
    parser.add_argument("--scope", choices=["image", "python-expat"], required=True)
    parser.add_argument("--sbom", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        policy = read_policy(args.policy, root)
        accepted, blocked = evaluate(
            json.loads(args.report.read_text()), policy, args.role, args.image_id,
            args.scope, datetime.now(timezone.utc),
            json.loads(args.sbom.read_text()) if args.sbom else None,
        )
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        print(f"BLOCKED: invalid evidence or policy: {error}", file=sys.stderr)
        return 2
    result = "BLOCKED" if blocked else "PASS"
    summary = f"{result} {args.role}/{args.scope}: {len(accepted)} accepted residual High matches; {len(blocked)} blockers."
    print(summary)
    for finding in blocked:
        print("  BLOCKED:", finding)
    if accepted:
        print("  ACCEPTED CVEs:", ", ".join(sorted({x.split()[0] for x in accepted})))
        print("  Residual risk remains. Findings are preserved in the report, not fixed or hidden.")
    if path := os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(path, "a") as stream:
            stream.write(f"\n- {summary} Full report: {args.report.name}\n")
    return 1 if blocked else 0


if __name__ == "__main__":
    sys.exit(main())
