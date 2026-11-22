#!/usr/bin/env python3
"""Check that a skill chain can actually run in this session.

A chain that names a skill nothing installed will fail halfway through, after
the expensive steps have already run. Run this before approving a step plan.

Usage:
    python preflight.py [--require a,b,c] [--all] [--json] [--check-network]
                        [--timeout 8]

Exit codes:
    0  every required skill is installed and the local scripts are present
    1  at least one required skill is missing
    2  usage error
"""

import argparse
import json
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(HERE)

HOME = os.path.expanduser("~")

# Where installed skills live on this machine. Override or extend with
# PAPERFLOW_SKILL_ROOTS (os.pathsep-separated) when the layout differs.
ROOTS = [
    ("library", os.path.join(HOME, ".skills-manager", "skills")),
    ("codex", os.path.join(HOME, ".codex", "skills")),
    ("dsh", os.path.join(HOME, ".dsh", "skills")),
    ("agents", os.path.join(HOME, ".agents", "skills")),
]
for _extra in filter(None, os.environ.get("PAPERFLOW_SKILL_ROOTS", "").split(os.pathsep)):
    ROOTS.append(("env", _extra))

DEFAULT_SKILLS = [
    "academic-paper",
    "academic-paper-reviewer",
    "academic-pipeline",
    "anti-defensive-writing",
    "anti-defensive-writing-en",
    "benchmark-paper-template",
    "deep-research",
    "drawio-reconstruction",
    "exploratory-data-analysis",
    "figure-designer",
    "idea-evaluator",
    "intro-drafter",
    "lieflat-less-ai-tone",
    "matplotlib",
    "paper-polish",
    "paper-writer",
    "pre-submission-reviewer",
    "rebuttal-guidance",
    "research-paper-writing",
    "sr-screener",
    "statistical-analysis",
    "sympy",
    "tech-paper-template",
    "uncertainty-and-units",
    "vibe-research-workflow",
]

SCRIPTS = ["check.py", "verify_refs.py", "export_docx.py", "_runtime.py",
           "status.py", "search_meta.py", "opac_search.py", "import_refs.py", "usage_report.py",
           "lint_docs.py"]


def locate(name):
    found = []
    for label, root in ROOTS:
        path = os.path.join(root, name, "SKILL.md")
        if os.path.isfile(path):
            found.append(label)
    return found


def check_scripts():
    missing = [s for s in SCRIPTS if not os.path.isfile(os.path.join(HERE, s))]
    return missing


def check_network(timeout):
    url = "https://doi.org/10.1038/nature12373"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.citationstyles.csl+json",
            "User-Agent": "plan-research-workflow/1.0 (preflight)",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return True, "doi.org ok (HTTP %s)" % resp.status
    except Exception as exc:
        return False, "%s: %s" % (type(exc).__name__, exc)


def main():
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")

    ap = argparse.ArgumentParser()
    ap.add_argument("--require", default="")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--check-network", action="store_true")
    ap.add_argument("--timeout", type=float, default=8.0)
    args = ap.parse_args()

    if args.require.strip():
        skills = [s.strip() for s in args.require.split(",") if s.strip()]
    elif args.all:
        skills = DEFAULT_SKILLS
    else:
        skills = DEFAULT_SKILLS

    rows = []
    for name in skills:
        roots = locate(name)
        rows.append({"skill": name, "roots": roots, "ok": bool(roots)})

    missing_scripts = check_scripts()
    network = None
    if args.check_network:
        ok, detail = check_network(args.timeout)
        network = {"ok": ok, "detail": detail}

    missing = [r["skill"] for r in rows if not r["ok"]]
    failed = bool(missing) or bool(missing_scripts) or (
        network is not None and not network["ok"]
    )

    if args.json:
        print(json.dumps({
            "skills": rows,
            "missing_skills": missing,
            "missing_scripts": missing_scripts,
            "network": network,
            "ok": not failed,
        }, ensure_ascii=False, indent=2))
    else:
        print("preflight.py — %s" % SKILL_ROOT)
        print("python %s" % sys.version.split()[0])
        if missing_scripts:
            print("scripts: MISSING %s" % ", ".join(missing_scripts))
        else:
            print("scripts: all %d ok" % len(SCRIPTS))
        if network is not None:
            print("network: %s" % ("ok — " + network["detail"] if network["ok"] else "FAILED — " + network["detail"]))
        print("")
        for row in rows:
            if row["ok"]:
                print("[ok]      %-28s %s" % (row["skill"], ",".join(row["roots"])))
            else:
                print("[missing] %-28s not found in library/codex/dsh/agents" % row["skill"])
        print("")
        if missing:
            print("MISSING: %d skill(s). Choose a substitute from the degradation order in" % len(missing))
            print("references/skill-catalog.md and state what is lost; do not skip silently.")
        else:
            print("ALL REQUIRED SKILLS PRESENT")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
