"""preflight 必须在别的 agent 的技能目录里也找得到技能。

v1.1.5 之前 ROOTS 只认 library / codex / dsh / agents 四个目录，
Claude Code、Cursor、OpenCode 的用户会看到"全缺"的假警报。
这些用例锁住根目录清单，以及 PAPERFLOW_SKILL_ROOTS 的扩展能力。
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
PREFLIGHT = os.path.join(SKILL, "scripts", "preflight.py")

EXPECTED_ROOTS = [
    "library",
    "codex",
    "dsh",
    "agents",
    "claude",
    "cursor",
    "opencode",
    "project-claude",
    "project-cursor",
]


def run(args, env_extra=None, cwd=None):
    env = os.environ.copy()
    env.pop("PAPERFLOW_SKILL_ROOTS", None)
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        [sys.executable, PREFLIGHT] + args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        cwd=cwd or SKILL,
    )


class RootCoverageTest(unittest.TestCase):
    def test_all_agent_roots_are_searched(self):
        """技能放在别的 agent 目录里也要被认出来。"""
        with tempfile.TemporaryDirectory() as tmp:
            for label in ("claude", "cursor", "opencode", "project-claude", "project-cursor"):
                root = os.path.join(tmp, label)
                os.makedirs(os.path.join(root, "grilling"), exist_ok=True)
                with open(os.path.join(root, "grilling", "SKILL.md"), "w", encoding="utf-8") as fh:
                    fh.write("---\nname: grilling\n---\n")
            env = {
                "PAPERFLOW_SKILL_ROOTS": os.pathsep.join(
                    os.path.join(tmp, label)
                    for label in ("claude", "cursor", "opencode", "project-claude", "project-cursor")
                )
            }
            proc = run(["--json", "--require", "grilling"], env_extra=env, cwd=tmp)
            data = json.loads(proc.stdout)
            self.assertEqual(data["missing_skills"], [])
            self.assertTrue(data["skills"][0]["ok"])

    def test_default_roots_list_is_complete(self):
        """根目录清单本身：缺一个就代表某类 agent 被漏掉。"""
        code = (
            "import sys, json; sys.path.insert(0, %r);"
            "import preflight; print(json.dumps([r[0] for r in preflight.ROOTS]))"
            % os.path.join(SKILL, "scripts")
        )
        out = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True, encoding="utf-8"
        )
        self.assertEqual(out.returncode, 0, out.stderr)
        labels = json.loads(out.stdout)
        for label in EXPECTED_ROOTS:
            self.assertIn(label, labels)

    def test_env_roots_are_appended(self):
        """PAPERFLOW_SKILL_ROOTS 可以追加自定义目录（os.pathsep 分隔）。"""
        with tempfile.TemporaryDirectory() as tmp:
            os.makedirs(os.path.join(tmp, "grilling"), exist_ok=True)
            with open(os.path.join(tmp, "grilling", "SKILL.md"), "w", encoding="utf-8") as fh:
                fh.write("---\nname: grilling\n---\n")
            proc = run(["--json", "--require", "grilling"], env_extra={"PAPERFLOW_SKILL_ROOTS": tmp})
            data = json.loads(proc.stdout)
            self.assertIn("env", data["skills"][0]["roots"])


if __name__ == "__main__":
    unittest.main()
