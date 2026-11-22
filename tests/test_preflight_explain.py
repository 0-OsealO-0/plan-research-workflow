#!/usr/bin/env python3
"""Regression tests for `preflight.py --explain` (no network).

The question these guard: when a partner skill is missing, does the tool tell the
caller what it is for and how to get it — and does it avoid claiming it installed
anything on its own?
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "preflight.py"
DEPS = ROOT / "references" / "skill-dependencies.json"


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args],
                          capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


class ExplainTests(unittest.TestCase):
    def test_explain_prints_role_install_and_cost(self) -> None:
        r = run("--require", "definitely-not-installed-skill-xyz", "--explain")
        self.assertEqual(r.returncode, 1)
        out = r.stdout
        self.assertIn("作用", out)
        self.assertIn("安装", out)
        self.assertIn("缺失时", out)

    def test_explain_states_consent_rule(self) -> None:
        r = run("--require", "definitely-not-installed-skill-xyz", "--explain")
        self.assertIn("先让用户确认", r.stdout)
        self.assertIn("skill-inspector", r.stdout)

    def test_default_hint_points_at_explain(self) -> None:
        r = run("--require", "definitely-not-installed-skill-xyz")
        self.assertIn("--explain", r.stdout)
        self.assertIn("never install silently", r.stdout)

    def test_manifest_covers_default_skills(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        import preflight  # noqa: E402

        data = json.loads(DEPS.read_text(encoding="utf-8"))
        missing = [s for s in preflight.DEFAULT_SKILLS if s not in data]
        self.assertEqual(missing, [], "manifest missing: %s" % missing)
        for name in preflight.DEFAULT_SKILLS:
            entry = data[name]
            self.assertTrue(entry.get("role"), name)
            self.assertTrue(entry.get("fallback"), name)

    def test_json_missing_entries_carry_role(self) -> None:
        r = run("--require", "definitely-not-installed-skill-xyz", "--json")
        payload = json.loads(r.stdout)
        self.assertEqual(r.returncode, 1)
        self.assertTrue(payload["missing_skills"])
        self.assertIn("role", payload["missing_skills"][0])


if __name__ == "__main__":
    unittest.main()
