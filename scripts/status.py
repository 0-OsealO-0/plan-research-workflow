#!/usr/bin/env python3
"""Keep a paper's run state across sessions, and version every overwrite.

A paper takes days. Without a state file, the next session cannot tell which
stage it is in, which steps were approved, or whether the file on disk is the
one the last step produced. This script keeps that in `paperflow/state.json`
and appends to `paperflow/runlog.md` (append-only, never rewritten).

Usage:
    python status.py init   [--dir DIR] [--title T] [--type course]
    python status.py show   [--dir DIR] [--json]
    python status.py start  --skill paper-writer [--deliverable draft_v1.md] [--dir DIR]
    python status.py done   --id 1 [--artifact draft_v1.md] [--gate "check.py exit 0"] [--note "..."] [--dir DIR]
    python status.py fail   --id 1 [--note "..."] [--dir DIR]
    python status.py decide --question "..." --choice "..." [--reason "..."] [--dir DIR]
    python status.py backup PATH
    python status.py note   "free text" [--dir DIR]

Exit codes:
    0  ok
    1  a recorded artifact changed or disappeared (show only)
    2  usage, missing state, or file error
"""

import argparse
import datetime
import hashlib
import io
import json
import os
import shutil
import sys

STATE_DIR = "paperflow"
STATE_FILE = "state.json"
LOG_FILE = "runlog.md"
BACKUP_DIR = "backups"


GLOSSARY_TEMPLATE = """# 术语表 — {title}

一个术语一行，写正文前先填，写完后按它校对。正文、图、表、图注必须用「术语」列的词；
「禁用近义词」里的词出现在正文里，check.py 会标出来。

| 术语 | 定义（一句话） | 禁用近义词 |
| --- | --- | --- |
| （示例）通道 | 乘客感知设计的媒介，本文固定为光、声、空间三种 | 模态、维度、途径 |
| （示例）线索 | 判断信任是否建立的维度，本文固定为可预期、可对话、可归属 | 要素、指标、层面 |

## 约定

- 术语表只列真正容易混用的词，列太多会让 check.py 误报。
- 术语一旦定下，改稿时只改用法，不改名字；确需改名，先改这张表。
"""


def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def project_dir(args):
    return os.path.abspath(args.dir or ".")


def paths(root):
    base = os.path.join(root, STATE_DIR)
    return {
        "base": base,
        "state": os.path.join(base, STATE_FILE),
        "log": os.path.join(base, LOG_FILE),
        "backups": os.path.join(base, BACKUP_DIR),
    }


def load_state(root):
    p = paths(root)
    if not os.path.isfile(p["state"]):
        return None
    with io.open(p["state"], encoding="utf-8") as fh:
        return json.load(fh)


def save_state(root, state):
    p = paths(root)
    state["updated"] = now()
    os.makedirs(p["base"], exist_ok=True)
    tmp = p["state"] + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(state, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    os.replace(tmp, p["state"])


def append_log(root, line):
    p = paths(root)
    os.makedirs(p["base"], exist_ok=True)
    with io.open(p["log"], "a", encoding="utf-8", newline="\n") as fh:
        fh.write(line.rstrip("\n") + "\n")


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def need_state(root):
    state = load_state(root)
    if state is None:
        print("ERROR: 没有找到 %s；先运行 status.py init" % paths(root)["state"], file=sys.stderr)
        sys.exit(2)
    return state


def relative(root, path):
    try:
        return os.path.relpath(os.path.abspath(path), root)
    except ValueError:
        return os.path.abspath(path)


def cmd_init(args):
    root = project_dir(args)
    p = paths(root)
    if os.path.isfile(p["state"]):
        print("已存在：%s（不覆盖）" % p["state"])
        return 0
    os.makedirs(p["base"], exist_ok=True)
    state = {
        "version": 1,
        "title": args.title or os.path.basename(root),
        "type": args.type,
        "scenario": args.scenario,
        "mode": args.mode,
        "stage": "planning",
        "chain": [],
        "decisions": [],
        "created": now(),
        "updated": now(),
    }
    save_state(root, state)
    if not os.path.isfile(p["log"]):
        with io.open(p["log"], "w", encoding="utf-8", newline="\n") as fh:
            fh.write("# Run Log — %s\n\n" % state["title"])
            fh.write("追加记录，不改写历史。每行：时间 · 事件 · 产物 · 结果。\n\n")
    append_log(root, "- %s · init · type=%s%s"
               % (now(), args.type, (" · scenario=" + args.scenario) if args.scenario else ""))
    # 术语表：写作前先建，避免"线索/通道"这类词在稿子里漂移
    gl = os.path.join(root, "术语表.md")
    if not os.path.isfile(gl):
        with io.open(gl, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(GLOSSARY_TEMPLATE.format(title=state["title"]))
        print("已创建：%s" % gl)
    print("已创建：%s" % p["state"])
    return 0


def cmd_show(args):
    root = project_dir(args)
    state = need_state(root)
    chain = state.get("chain", [])
    problems = 0
    lines = []
    lines.append("模式：%s" % state.get("mode", "未记录"))
    lines.append("论文：%s（%s）" % (state.get("title", ""), state.get("type", "")))
    if state.get("scenario"):
        lines.append("场景：%s" % state["scenario"])
    lines.append("阶段：%s" % state.get("stage", "unknown"))
    lines.append("链条：%d 步" % len(chain))
    for step in chain:
        status = step.get("status", "pending")
        label = "步骤 %s · %s" % (step.get("id"), step.get("skill", "?"))
        artifact = step.get("artifact") or step.get("deliverable") or ""
        detail = ""
        if artifact and step.get("sha256"):
            full = artifact if os.path.isabs(artifact) else os.path.join(root, artifact)
            if not os.path.isfile(full):
                detail = " [产物缺失]"
                problems += 1
            elif sha256(full) != step["sha256"]:
                detail = " [已被改动 sha256 不符]"
                problems += 1
            else:
                detail = " [未变]"
        lines.append("  [%s] %s → %s%s" % (status, label, artifact, detail))
    if state.get("decisions"):
        lines.append("决策：")
        for d in state["decisions"][-5:]:
            lines.append("  - %s：%s（%s）" % (d.get("when"), d.get("choice"), d.get("question")))
    pending = [s for s in chain if s.get("status") != "done"]
    if pending:
        lines.append("下一步：步骤 %s · %s" % (pending[0].get("id"), pending[0].get("skill")))
    elif chain:
        lines.append("下一步：链条已跑完，进入收尾检查")
    else:
        lines.append("下一步：还没有步骤，先提计划")

    if args.json:
        print(json.dumps({"state": state, "problems": problems}, ensure_ascii=False, indent=2))
    else:
        print("\n".join(lines))
    return 1 if problems else 0


def cmd_start(args):
    root = project_dir(args)
    state = need_state(root)
    chain = state.setdefault("chain", [])
    new_id = max([int(s.get("id", 0)) for s in chain] or [0]) + 1
    step = {
        "id": new_id,
        "skill": args.skill,
        "deliverable": args.deliverable or "",
        "status": "running",
        "artifact": "",
        "sha256": "",
        "gate": "",
        "started": now(),
    }
    chain.append(step)
    if args.stage:
        state["stage"] = args.stage
    elif state.get("stage") in ("planning", "unknown", ""):
        state["stage"] = "in progress"
    save_state(root, state)
    append_log(root, "- %s · step %d start · %s · %s" % (now(), new_id, args.skill, args.deliverable or "-"))
    print("步骤 %d 开始：%s" % (new_id, args.skill))
    return 0


def find_step(state, sid):
    for step in state.get("chain", []):
        if str(step.get("id")) == str(sid):
            return step
    return None


def cmd_done(args):
    root = project_dir(args)
    state = need_state(root)
    step = find_step(state, args.id)
    if step is None:
        print("ERROR: 没有步骤 %s" % args.id, file=sys.stderr)
        return 2
    artifact = args.artifact or step.get("deliverable") or ""
    digest = ""
    if artifact:
        full = artifact if os.path.isabs(artifact) else os.path.join(root, artifact)
        if os.path.isfile(full):
            digest = sha256(full)
            artifact_rel = relative(root, full)
        else:
            artifact_rel = artifact
    else:
        artifact_rel = ""
    step.update({
        "status": "done",
        "artifact": artifact_rel,
        "sha256": digest,
        "gate": args.gate or step.get("gate", ""),
        "finished": now(),
        "note": args.note or "",
    })
    save_state(root, state)
    append_log(root, "- %s · step %s done · %s → %s · sha256:%s · gate:%s"
               % (now(), step["id"], step["skill"], artifact_rel or "-",
                  digest[:12] or "-", args.gate or "-"))
    print("步骤 %s 完成：%s%s" % (step["id"], artifact_rel or step["skill"], " · sha256 " + digest[:12] if digest else ""))
    return 0


def cmd_fail(args):
    root = project_dir(args)
    state = need_state(root)
    step = find_step(state, args.id)
    if step is None:
        print("ERROR: 没有步骤 %s" % args.id, file=sys.stderr)
        return 2
    step.update({"status": "failed", "note": args.note or "", "finished": now()})
    save_state(root, state)
    append_log(root, "- %s · step %s FAILED · %s · %s" % (now(), step["id"], step["skill"], args.note or "-"))
    print("步骤 %s 标记失败" % step["id"])
    return 0


def cmd_decide(args):
    root = project_dir(args)
    state = need_state(root)
    state.setdefault("decisions", []).append({
        "when": now(),
        "question": args.question,
        "choice": args.choice,
        "reason": args.reason or "",
    })
    save_state(root, state)
    append_log(root, "- %s · decision · %s → %s · %s"
               % (now(), args.question, args.choice, args.reason or "-"))
    print("已记录决策")
    return 0


def cmd_note(args):
    root = project_dir(args)
    need_state(root)
    append_log(root, "- %s · note · %s" % (now(), args.text))
    print("已追加")
    return 0


def cmd_backup(args):
    target = os.path.abspath(args.path)
    if not os.path.isfile(target):
        print("ERROR: 文件不存在：%s" % target, file=sys.stderr)
        return 2
    root = os.path.dirname(target)
    p = paths(root)
    os.makedirs(p["backups"], exist_ok=True)
    base = os.path.basename(target)
    index = 1
    while True:
        candidate = os.path.join(p["backups"], "%s.%03d.bak" % (base, index))
        if not os.path.exists(candidate):
            break
        index += 1
    shutil.copy2(target, candidate)
    append_log(root, "- %s · backup · %s → %s"
               % (now(), base, os.path.relpath(candidate, root).replace("\\", "/")))
    print(candidate)
    return 0


def main():
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")

    ap = argparse.ArgumentParser()
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--dir", default=".")
    sub = ap.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", parents=[common])
    p_init.add_argument("--title", default="")
    p_init.add_argument("--type", default="course")
    p_init.add_argument("--scenario", default="", help="场景判定，如「课程报告」「开题申报书」")
    p_init.add_argument("--mode", default="execute", choices=["execute", "plan"])
    p_init.set_defaults(func=cmd_init)

    p_show = sub.add_parser("show", parents=[common])
    p_show.add_argument("--json", action="store_true")
    p_show.set_defaults(func=cmd_show)

    p_start = sub.add_parser("start", parents=[common])
    p_start.add_argument("--skill", required=True)
    p_start.add_argument("--deliverable", default="")
    p_start.add_argument("--stage", default="")
    p_start.set_defaults(func=cmd_start)

    p_done = sub.add_parser("done", parents=[common])
    p_done.add_argument("--id", required=True)
    p_done.add_argument("--artifact", default="")
    p_done.add_argument("--gate", default="")
    p_done.add_argument("--note", default="")
    p_done.set_defaults(func=cmd_done)

    p_fail = sub.add_parser("fail", parents=[common])
    p_fail.add_argument("--id", required=True)
    p_fail.add_argument("--note", default="")
    p_fail.set_defaults(func=cmd_fail)

    p_decide = sub.add_parser("decide", parents=[common])
    p_decide.add_argument("--question", required=True)
    p_decide.add_argument("--choice", required=True)
    p_decide.add_argument("--reason", default="")
    p_decide.set_defaults(func=cmd_decide)

    p_note = sub.add_parser("note", parents=[common])
    p_note.add_argument("text")
    p_note.set_defaults(func=cmd_note)

    p_backup = sub.add_parser("backup", parents=[common])
    p_backup.add_argument("path")
    p_backup.set_defaults(func=cmd_backup)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
