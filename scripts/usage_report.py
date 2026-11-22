#!/usr/bin/env python3
"""Skill-usage ledger for one paper project.

Answers one question before a deliverable leaves the room: which skills actually
ran on this manuscript, which of the applicable ones never ran, and what each one
was supposed to catch. A missing skill is not a defect by itself — it is a
question the user is entitled to see before an export.

Usage:
    python scripts/usage_report.py [--root .] [--required a,b,c] [--json]

Reads   <root>/paperflow/state.json and <root>/paperflow/runlog.md
Exit    0 = every required skill appears in the run log
        1 = at least one required skill never ran (blocks the export gate)
        2 = usage / missing state error
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# (skill, what it is there to catch)
APPLICABLE = [
    ("deep-research", "文献覆盖与来源可靠性；没有它，现状一节靠记忆写"),
    ("idea-evaluator", "选题是否值得做；五维评估与致命缺陷"),
    ("tech-paper-template", "论证骨架先立后写；避免边写边想"),
    ("intro-drafter", "引言六段式（背景—局限—缺口—挑战—方案—贡献）"),
    ("paper-writer", "把材料写成稿；主张与证据对齐"),
    ("grilling", "红队：替代方案未排除、参数无出处、主张不可证伪"),
    ("academic-paper-reviewer", "五席位评审（含 Devil's Advocate）出成文报告"),
    ("anti-defensive-writing", "叙事立场：不主动示弱、不写工作汇报"),
    ("paper-polish", "语法、语气与证据强度校准（不越权改事实）"),
    ("lieflat-less-ai-tone", "白名单式去 AI 腔；只改命中的句子"),
    ("research-paper-writing", "章节推进与主张—支撑对齐（长文）"),
    ("pre-submission-reviewer", "交稿前五维审查（逻辑、细节、语法、格式、图）"),
    ("figure-designer", "图的设计范式与自审（图例、坐标、诚实呈现）"),
    ("scientific-visualization", "配色/对比度/导出尺寸的可发表级规范"),
    ("matplotlib", "绘图实现与导出控制"),
    ("statistical-analysis", "有数据时的检验选择与报告"),
    ("exploratory-data-analysis", "数据剖面、缺失与泄漏审计"),
    ("uncertainty-and-units", "单位与不确定度传播"),
    ("rebuttal-guidance", "审稿意见的回应策略"),
    ("drawio-reconstruction", "把参考图重建成可编辑图"),
    ("sr-screener", "系统综述的筛选与 PRISMA 计数"),
]

# 别名：运行记录里可能写的是中文或简称，只要命中任一别名就算跑过。
ALIASES = {
    "paper-polish": ["paper-polish", "润色", "polish"],
    "lieflat-less-ai-tone": ["lieflat", "去 ai 味", "去ai味", "中文去 ai"],
    "grilling": ["grilling", "红队"],
    "paper-writer": ["paper-writer", "初稿", "写作"],
    "anti-defensive-writing": ["anti-defensive", "防御性"],
    "academic-paper-reviewer": ["academic-paper-reviewer", "评审报告"],
    "pre-submission-reviewer": ["pre-submission-reviewer", "交稿审查"],
    "verify_refs": ["verify_refs"],
    "check": ["check.py", "自检"],
}

# Skills that must appear in the run log for a paper that leaves this room.
DEFAULT_REQUIRED = [
    "paper-writer",
    "grilling",
    "paper-polish",
    "lieflat-less-ai-tone",
    "verify_refs",
    "check",
]


def load_text(root: Path) -> str:
    parts = []
    runlog = root / "paperflow" / "runlog.md"
    if runlog.is_file():
        parts.append(runlog.read_text(encoding="utf-8", errors="replace"))
    state = root / "paperflow" / "state.json"
    if state.is_file():
        try:
            data = json.loads(state.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}
        for step in data.get("steps", []):
            parts.append(json.dumps(step, ensure_ascii=False))
    return "\n".join(parts).lower()


def main() -> int:
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Report which skills ran on this paper.")
    ap.add_argument("--root", default=".", help="项目根目录（含 paperflow/）")
    ap.add_argument("--required", default="", help="逗号分隔，覆盖默认必需清单")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    root = Path(args.root)
    if not (root / "paperflow").is_dir():
        print(f"没有找到 {root / 'paperflow'}：这个项目还没初始化状态文件（status.py init）。")
        return 2

    text = load_text(root)
    if not text.strip():
        print("paperflow/ 里还没有 runlog 或 state：先跑 status.py init/start/done。")
        return 2

    required = [x.strip() for x in args.required.split(",") if x.strip()] or DEFAULT_REQUIRED
    rows = []
    for skill, purpose in APPLICABLE:
        needles = ALIASES.get(skill, [skill])
        ran = any(n.lower() in text for n in needles)
        rows.append({"skill": skill, "purpose": purpose, "ran": ran,
                     "required": skill in required})

    missing_required = [r["skill"] for r in rows if r["required"] and not r["ran"]]

    if args.json:
        print(json.dumps({"rows": rows, "missing_required": missing_required},
                         ensure_ascii=False, indent=2))
    else:
        print(f"项目：{root.resolve()}")
        print(f"运行记录来源：paperflow/state.json + paperflow/runlog.md")
        print()
        print(f"{'技能':<26}{'状态':<6}它负责挡住什么")
        for r in rows:
            mark = "已跑" if r["ran"] else ("缺（必需）" if r["required"] else "未跑")
            print(f"{r['skill']:<26}{mark:<8}{r['purpose']}")
        print()
        if missing_required:
            print("导出前必须补齐：")
            for s in missing_required:
                print(f"  - {s}")
            if "grilling" in missing_required:
                print("先补红队（grilling）：攻击主张链，再按结论改正文。")
            elif "paper-polish" in missing_required:
                print("补 paper-polish：红队已跑，但正文没经过独立润色——红队给的问题会没人系统修。")
            print("若某个技能确实跑过只是没记录，用 `status.py note` 补一行，不要造假。")
        else:
            print("必需环节都在运行记录里。未跑的可选技能，请对用户说明为什么这次不需要。")

    return 1 if missing_required else 0


if __name__ == "__main__":
    sys.exit(main())
