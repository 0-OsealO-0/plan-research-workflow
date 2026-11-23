"""外部反馈 #4 / #5 的回归：重复 id 要可定位，import_refs 的三种空结果要分得开。

- verify_refs：CSV 里两行同 id 时，报告仍会输出两条相同的 [UNCHECKED] 1，
  读者分不清哪条是哪条；现在向 stderr 打警告，退出码不变（这不是核验失败）。
- import_refs：空文件 / 全部重复 / 全部缺题名 三种情况以前混成一句话（而且空文件 exit 0），
  现在分别是 exit 2 / exit 1 / exit 1，且消息进 stderr。
全部离线，不依赖网络与 pytest。
"""
import io
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
VERIFY = os.path.join(SKILL, "scripts", "verify_refs.py")
IMPORT = os.path.join(SKILL, "scripts", "import_refs.py")
PY = sys.executable

DUP_CSV = (
    "id,title,doi\n"
    "1,A,10.1016/j.lindif.2023.102274\n"
    "1,B,10.1111/bjet.13370\n"
)


def run(script, *args, cwd=None):
    return subprocess.run(
        [PY, script] + list(args),
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=cwd or os.path.dirname(SKILL),
    )


class DuplicateIdTest(unittest.TestCase):
    def test_duplicate_ids_are_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = os.path.join(tmp, "dup.csv")
            io.open(csv_path, "w", encoding="utf-8").write(DUP_CSV)
            proc = run(VERIFY, "--csv", csv_path, "--offline")
            self.assertIn("重复的 id", proc.stderr, proc.stderr)
            self.assertIn("1", proc.stderr)
            # 不是核验失败：条目仍被处理，退出码保持 3（--offline 未 opt-in）
            self.assertEqual(proc.returncode, 3, proc.stdout + proc.stderr)

    def test_unique_ids_are_not_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = os.path.join(tmp, "ok.csv")
            io.open(csv_path, "w", encoding="utf-8").write(
                "id,title,doi\n1,A,10.1016/j.lindif.2023.102274\n2,B,10.1111/bjet.13370\n"
            )
            proc = run(VERIFY, "--csv", csv_path, "--offline")
            self.assertNotIn("重复的 id", proc.stderr, proc.stderr)


class ImportRefsExitTest(unittest.TestCase):
    def _import(self, ris_text, existing_csv=None):
        tmp = tempfile.mkdtemp()
        ris = os.path.join(tmp, "in.ris")
        io.open(ris, "w", encoding="utf-8").write(ris_text)
        csv_path = os.path.join(tmp, "citations.csv")
        if existing_csv is not None:
            io.open(csv_path, "w", encoding="utf-8").write(existing_csv)
        proc = run(IMPORT, ris, "--csv", csv_path)
        return proc, csv_path

    def test_empty_ris_exits_2(self):
        proc, _ = self._import("")
        self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
        self.assertIn("没有任何条目", proc.stderr)

    def test_all_duplicate_exits_1(self):
        one = ("TY  - JOUR\nTI  - A\nDO  - 10.1016/j.lindif.2023.102274\nPY  - 2023\nER  -\n")
        existing = (
            "id,authors,year,title,venue,doi_or_url,page,verified_by,verified_on,supports,type\n"
            "1,X,2023,A,V,10.1016/j.lindif.2023.102274,,,,J\n"
        )
        proc, _ = self._import(one, existing)
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("重复", proc.stderr)

    def test_missing_title_exits_1(self):
        proc, _ = self._import("TY  - JOUR\nDO  - 10.1234/nope\nPY  - 2024\nER  -\n")
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("缺题名", proc.stderr)

    def test_new_record_still_imports(self):
        proc, csv_path = self._import(
            "TY  - JOUR\nTI  - Fresh\nDO  - 10.1234/fresh\nPY  - 2025\nER  -\n"
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        with io.open(csv_path, encoding="utf-8-sig") as fh:
            rows = fh.read()
        self.assertIn("Fresh", rows)


if __name__ == "__main__":
    unittest.main()
