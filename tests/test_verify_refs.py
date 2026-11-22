#!/usr/bin/env python3
"""Regression tests for scripts/verify_refs.py (no network access).

Run from the skill root:
    python -m unittest discover -s tests -v

The case that motivated these tests: a CSV without an `id` column used to be
read as "0 entries", print an empty SUMMARY and exit 0 — i.e. a citation
checker that silently certifies an unchecked reference list.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "verify_refs.py"

HEADER = "id,authors,year,title,venue,doi_or_url,page\n"
ROW = ("1,Someone A,2020,Some title,Some venue,"
       "10.1016/j.lindif.2023.102274,1-10\n")


def run(csv_text: str, *args: str) -> subprocess.CompletedProcess:
    with tempfile.TemporaryDirectory() as tmp:
        path = pathlib.Path(tmp) / "cases.csv"
        path.write_text(csv_text, encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--csv", str(path), *args],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )


class FailClosedTests(unittest.TestCase):
    def test_missing_id_column_exits_2(self) -> None:
        r = run("title,doi\nSome title,10.1016/j.lindif.2023.102274\n")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("id", r.stderr)

    def test_header_only_exits_2(self) -> None:
        r = run(HEADER)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("没有任何行被核验", r.stderr)

    def test_only_matching_nothing_exits_2(self) -> None:
        r = run(HEADER + ROW, "--only", "99")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("--only", r.stderr)

    def test_assign_ids_autofills_and_warns(self) -> None:
        r = run("title,doi\nSome title,10.1016/j.lindif.2023.102274\n",
                "--assign-ids", "--offline")
        self.assertIn("自动编号", r.stderr)
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)  # UNCHECKED

    def test_offline_unchecked_needs_opt_in(self) -> None:
        r = run(HEADER + ROW, "--offline")
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertIn("--allow-unchecked", r.stderr)

    def test_offline_with_opt_in_exits_0(self) -> None:
        r = run(HEADER + ROW, "--offline", "--allow-unchecked")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_missing_file_exits_2(self) -> None:
        r = subprocess.run(
            [sys.executable, str(SCRIPT), "--csv", "no_such_file.csv"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)

    def test_isbn_row_is_manual_not_unreachable(self) -> None:
        row = ("1,Zhu G,2025,Tan mei,中国长安出版传媒有限公司,"
               "ISBN 978-7-5107-1166-4,154\n")
        r = run(HEADER + row)  # no network call is attempted for ISBN
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("MANUAL", r.stdout)

    def test_help_documents_exit_codes(self) -> None:
        r = subprocess.run([sys.executable, str(SCRIPT), "--help"],
                           capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        self.assertEqual(r.returncode, 0)
        self.assertIn("退出码", r.stdout)


if __name__ == "__main__":
    unittest.main()
