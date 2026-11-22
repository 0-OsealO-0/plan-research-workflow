#!/usr/bin/env python3
"""Consistency lint for the plan-research-workflow skill's own documentation.

The skill's rules live in SKILL.md and are restated in references/. Restating is
cheap and drifting is silent, so this script checks the few invariants that have
actually broken before:

  1. code fences are paired in every Markdown file,
  2. the verbatim correction sentence exists in exactly two places, word for word,
  3. every `references/...` and `scripts/...` path named in SKILL.md exists,
  4. the Quality Rules are numbered 1..N without gaps or repeats,
  5. every playbook heading has a `**Minimal:**` line (playbook 8 is the one
     documented exception: full managed project has no minimal chain),
  6. a "三条/四条硬规则" heading states the number of rules it actually lists.

Exit 0 = all checks pass, 1 = at least one problem (listed), 2 = usage error.
Standard library only.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SKILL = BASE / "SKILL.md"
REFS = BASE / "references"

CORRECTION_CORE = "如果你不是这个场景"
PATH_RE = re.compile(r"`((?:references|scripts)/[\w.\-]+)`")
RULE_RE = re.compile(r"^(\d+)\.\s")
PLAYBOOK_RE = re.compile(r"^## (\d+)\.\s")
HARD_RULES_RE = re.compile(r"^## \d+\.\s*[三四五六]条硬规则")
NUMERALS = {"三": 3, "四": 4, "五": 5, "六": 6}


def md_files() -> list[Path]:
    """SKILL.md, every references/*.md, and the top-level docs (README, QUICKSTART)."""
    top = [f for f in sorted(BASE.glob("*.md")) if f != SKILL]
    files = [SKILL] + sorted(REFS.glob("*.md")) + top
    return [f for f in files if f.is_file()]


def check_fences(path: Path) -> list[str]:
    n = sum(1 for line in path.read_text(encoding="utf-8").splitlines()
            if line.startswith("```"))
    if n % 2:
        return [f"{path.name}: fenced code blocks are unbalanced ({n} fence lines)"]
    return []


def check_correction_sentence(files: list[Path]) -> list[str]:
    found: list[tuple[str, str]] = []
    for f in files:
        for line in f.read_text(encoding="utf-8").splitlines():
            if CORRECTION_CORE in line:
                start = line.find("「如果你不是这个场景")
                end = line.find("」", start)
                if start >= 0 and end > start:
                    found.append((f.name, line[start:end + 1]))
    problems: list[str] = []
    if len(found) != 2:
        names = ", ".join(sorted({n for n, _ in found})) or "none"
        problems.append(
            f"correction sentence appears {len(found)} times (expected 2: SKILL.md "
            f"and routing-checklist.md); found in: {names}")
    variants = {text for _, text in found}
    if len(variants) > 1:
        problems.append("correction sentence is worded differently across files")
    return problems


def check_paths() -> list[str]:
    text = SKILL.read_text(encoding="utf-8")
    problems: list[str] = []
    for rel in sorted(set(PATH_RE.findall(text))):
        if not (BASE / rel).exists():
            problems.append(f"SKILL.md names {rel}, which does not exist")
    return problems


def check_rules() -> list[str]:
    lines = SKILL.read_text(encoding="utf-8").splitlines()
    start = next((i for i, l in enumerate(lines) if l.strip() == "## Quality Rules"), None)
    if start is None:
        return ["SKILL.md: no '## Quality Rules' section"]
    end = next((i for i, l in enumerate(lines[start + 1:], start + 1)
                if l.startswith("## ")), len(lines))
    numbers = [int(m.group(1)) for l in lines[start + 1:end]
               for m in [RULE_RE.match(l)] if m]
    if not numbers:
        return ["SKILL.md: Quality Rules section lists no numbered rules"]
    expected = list(range(1, len(numbers) + 1))
    if numbers != expected:
        return [f"SKILL.md: Quality Rules are numbered {numbers[:3]}...{numbers[-1]}, "
                f"expected 1..{len(numbers)} with no gap or repeat"]
    return []


def check_playbooks() -> list[str]:
    path = REFS / "workflow-playbooks.md"
    if not path.is_file():
        return ["references/workflow-playbooks.md is missing"]
    lines = path.read_text(encoding="utf-8").splitlines()
    problems: list[str] = []
    count = 0
    for i, line in enumerate(lines):
        m = PLAYBOOK_RE.match(line)
        if not m:
            continue
        count += 1
        number = int(m.group(1))
        window = "\n".join(lines[i + 1:i + 8])
        if number == 8:
            continue  # full managed project: deliberately no minimal chain
        if "**Minimal:**" not in window:
            problems.append(f"playbook {number} ({line[3:60].strip()}) has no **Minimal:** line")
    if count < 10:
        problems.append(f"workflow-playbooks.md has {count} numbered playbooks, expected at least 10")
    return problems


def check_hard_rule_headings() -> list[str]:
    problems: list[str] = []
    for path in sorted(REFS.glob("*.md")):
        lines = path.read_text(encoding="utf-8").splitlines()
        for i, line in enumerate(lines):
            if not HARD_RULES_RE.match(line):
                continue
            stated = NUMERALS[line[line.index("条硬规则") - 1]]
            items = 0
            for follow in lines[i + 1:]:
                if follow.startswith("## "):
                    break
                if RULE_RE.match(follow):
                    items += 1
            if items != stated:
                problems.append(f"{path.name}:{i + 1}: heading says {stated} rules, "
                                f"section lists {items}")
    return problems


def main() -> int:
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    files = md_files()
    if not files:
        print("no markdown files found next to scripts/", file=sys.stderr)
        return 2
    problems: list[str] = []
    for f in files:
        problems += check_fences(f)
    problems += check_correction_sentence(files)
    problems += check_paths()
    problems += check_rules()
    problems += check_playbooks()
    problems += check_hard_rule_headings()

    print(f"lint_docs: {len(files)} markdown files, "
          f"{len(problems)} problem{'s' if len(problems) != 1 else ''}")
    for p in problems:
        print(f"  [FAIL] {p}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
