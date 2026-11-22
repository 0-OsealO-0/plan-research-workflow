#!/usr/bin/env python3
"""Deterministic pre-submission checks for a paper draft.

Checks only what a machine can check. Judgement calls stay with the reviewer
(see the "Deterministic Checks" section of SKILL.md).

Usage:
    python check.py <file.md> [--type course|imrad|lab|proposal|thesis|generic]
                              [--min-words N] [--max-words N]
                              [--citations-csv citations.csv] [--json]

Exit codes:
    0  no CRITICAL findings (warnings allowed)
    1  at least one CRITICAL finding
    2  usage or file error
"""

import argparse
import csv
import io
import json
import os
import re
import sys

CITATION = re.compile(r"\[(\d+(?:\s*[,，、\-–]\s*\d+)*)\]")
REF_HEAD = re.compile(
    r"^[ \t]{0,3}#{1,6}[ \t]*(参考文献|文献目录|references?|bibliography)[ \t]*$",
    re.IGNORECASE | re.MULTILINE,
)
REF_ENTRY = re.compile(r"^[ \t]*\[(\d+)\]", re.MULTILINE)
CAP_START = re.compile(
    r"^[ \t]*(图|表|Figure|Fig\.?|Table)[ \t]*(\d+)(.*)$", re.IGNORECASE
)
CAP_REF = re.compile(r"(图|表|Figure|Fig\.?|Table)[ \t]*(\d+)", re.IGNORECASE)
REF_WORDS = re.compile(r"见|展示|所示|如(图|表)|下表|上图")
HEADING = re.compile(r"^[ \t]{0,3}#{1,6}[ \t]*(.+?)[ \t]*$", re.MULTILINE)
CJK = re.compile(r"[\u4e00-\u9fff]")
WORD = re.compile(r"[A-Za-z][A-Za-z'\-]*")
EM_DASH = re.compile(r"[—–]{1,2}")

DOI = re.compile(r"10\.\d{4,9}/[^\s,，;；]+")
URL = re.compile(r"https?://[^\s，。;；]+")
YEAR = re.compile(r"(?:19|20)\d{2}")
PAGES = re.compile(r"\d+\s*[-–—~]\s*\d+|\d+\s*页|p{1,2}\.\s*\d+|[:：]\s*\d{1,5}\s*(?:[.。]|$)", re.IGNORECASE)
REF_TYPE = re.compile(r"\[([A-Z]{1,3}(?:/[A-Z]{2})?)\]")

PLACEHOLDERS = [
    ("TODO", r"TODO"),
    ("TBD", r"TBD"),
    ("XXX", r"XXX+"),
    ("待补", r"\[待补\]"),
    ("待填", r"\[待填\]"),
    ("填写处", r"\[填写"),
    ("待补充", r"待补充"),
    ("lorem", r"lorem ipsum"),
    ("模板变量", r"\{\{[^}]*\}\}"),
]

BANNED_CRITICAL = [
    ("遗憾的是", r"遗憾的是"),
    ("令人遗憾", r"令人遗憾"),
    ("效果有限", r"效果有限"),
    ("存在严重不足", r"存在严重(的)?不足"),
    ("有明显短板", r"有明显短板"),
    ("未达预期", r"未能达到预期"),
    ("unfortunately", r"\bunfortunately\b"),
    ("limited effectiveness", r"\blimited effectiveness\b"),
    ("severe shortcomings", r"\bsevere (shortcomings?|limitations?)\b"),
    ("fails to", r"\bfails? to\b"),
]

BANNED_WARN = [
    ("仅（非“仅当/仅在”）", r"(?<![不])仅(?![当在])"),
    ("有待进一步", r"有待进一步"),
    ("值得商榷", r"值得商榷"),
    ("尚不清楚", r"尚不清楚"),
    ("不可否认", r"不可否认"),
    ("it is worth noting", r"\bit is worth noting\b"),
    ("in conclusion", r"\bin conclusion\b"),
    ("综上所述", r"综上所述"),
    ("总而言之", r"总而言之"),
]

SECTIONS = {
    "course": ["摘要|Abstract", "引言|Introduction", "结论|Conclusion|小结"],
    "imrad": [
        "摘要|Abstract", "引言|Introduction", "方法|Method",
        "结果|Result", "结论|讨论|Conclusion|Discussion",
    ],
    "lab": ["目的|Objective", "方法|原理|步骤|Method", "结果|数据|Result", "讨论|结论|Discussion|Conclusion"],
    "proposal": ["问题|Question", "方法|方案|Method", "计划|时间|Timeline", "预期|成果|Outcome"],
    "thesis": ["摘要|Abstract", "引言|绪论|Introduction", "结论|Conclusion", "参考文献|References"],
    "generic": [],
}


def parse_citations(text):
    nums = set()
    for m in CITATION.finditer(text):
        for part in re.split(r"[,，、]", m.group(1)):
            part = part.strip()
            if re.search(r"[\-–]", part):
                a, b = re.split(r"[\-–]", part)
                if a.strip().isdigit() and b.strip().isdigit():
                    lo, hi = int(a), int(b)
                    if 0 < hi - lo < 200:
                        nums.update(range(lo, hi + 1))
            elif part.isdigit():
                nums.add(int(part))
    return nums


def strip_code(text):
    return re.sub(r"```.*?```", "", text, flags=re.DOTALL)


def count_words(text):
    return len(CJK.findall(text)) + len(WORD.findall(text))


def headings(text):
    return [h.strip() for h in HEADING.findall(text)]


def split_entries(ref_part):
    entries = []
    cur = None
    for line in ref_part.splitlines():
        m = REF_ENTRY.match(line)
        if m:
            if cur:
                entries.append(cur)
            cur = {"id": int(m.group(1)), "text": line}
        elif cur is not None:
            cur["text"] += "\n" + line
    if cur:
        entries.append(cur)
    return entries


def validate_entries(entries):
    crit, warn = [], []
    for e in entries:
        text = e["text"]
        eid = e["id"]
        if not YEAR.search(text):
            warn.append("[ref] [%d] 缺出版年" % eid)
        if not REF_TYPE.search(text):
            warn.append("[ref] [%d] 缺文献类型标识（[J]/[M]/[D]/[C]/[S]/[P]/[N]/[EB/OL]）" % eid)
        has_id = bool(DOI.search(text) or URL.search(text) or PAGES.search(text))
        if not has_id:
            warn.append("[ref] [%d] 缺 DOI/URL/页码，无法核对出处" % eid)
        if REF_TYPE.search(text) and "EB" in REF_TYPE.search(text).group(1) and not URL.search(text):
            warn.append("[ref] [%d] 标注为电子资源但没有 URL" % eid)
    return crit, warn


def load_citations_csv(path):
    rows = {}
    with io.open(path, encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        if not reader.fieldnames:
            raise ValueError("CSV 没有表头")
        fields = {name.strip().lower(): name for name in reader.fieldnames}
        vname_key = fields.get("verified_by")
        vflag_key = fields.get("verified")
        for row in reader:
            raw_id = row.get(fields.get("id", "id"), "").strip()
            if not raw_id:
                continue
            try:
                eid = int(re.sub(r"\D", "", raw_id) or "-1")
            except ValueError:
                continue
            vname = (row.get(vname_key, "") if vname_key else "").strip()
            vflag = (row.get(vflag_key, "") if vflag_key else "").strip().lower()
            verified = "y" if (vname and vname.lower() not in ("n", "no", "未核验")) else vflag
            rows[eid] = verified
    return rows


def read_docx_text(path):
    """Flatten a .docx to Markdown-ish text: headings keep their level, tables
    become pipe rows, so the same checks apply to a Word submission."""
    import importlib
    import os as _os

    _ = importlib
    sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
    from _runtime import ensure_docx

    docx = ensure_docx()
    doc = docx.Document(path)
    out = []
    for p in doc.paragraphs:
        text = (p.text or "").strip()
        if not text:
            continue
        name = (p.style.name or "") if p.style is not None else ""
        level = 0
        if name.startswith("Heading") or name.startswith("标题"):
            digits = re.findall(r"\d", name)
            level = int(digits[-1]) if digits else 1
        elif text in ("参考文献", "文献目录", "References", "Bibliography"):
            level = 2
        out.append(("#" * min(level, 4) + " " + text) if level else text)
    for table in doc.tables:
        out.append("")
        for row in table.rows:
            cells = [(c.text or "").strip().replace("\n", " ") for c in row.cells]
            out.append("| " + " | ".join(cells) + " |")
        out.append("")
    return "\n".join(out)


GLOSSARY_NAME = "术语表.md"
PARAM_HEADERS = ("参数", "参数名", "项目")
VALUE_HEADERS = ("设定值", "取值", "设定")
RANGE_MARKS = ("–", "-", "~", "～", "至", "到")
PARAM_NUM = re.compile(r"\d+(?:\.\d+)?")


def load_glossary(path):
    """读同目录 术语表.md 的「术语」与「禁用近义词」两列。"""
    folder = os.path.dirname(os.path.abspath(path))
    gp = os.path.join(folder, GLOSSARY_NAME)
    if not os.path.isfile(gp):
        return []
    try:
        raw = io.open(gp, encoding="utf-8").read()
    except OSError:
        return []
    rows = []
    for line in raw.splitlines():
        text = line.strip()
        if not text.startswith("|"):
            continue
        cells = [x.strip() for x in text.strip("|").split("|")]
        if len(cells) < 3:
            continue
        if set("".join(cells)) <= set("-: "):
            continue
        term, banned_cell = cells[0], cells[2]
        if term in ("术语", "术语名") or not term:
            continue
        banned = [b for b in re.split(r"[,，、/;；\s]+", banned_cell) if b and b != term]
        if banned:
            rows.append((term, banned))
    return rows


def check_glossary(path, body):
    """禁用近义词出现在正文 → WARN，并指向术语表指定的说法。"""
    crit, warn = [], []
    for term, banned in load_glossary(path):
        for word in banned:
            count = body.count(word)
            if count:
                warn.append("[term] 禁用近义词「%s」出现 %d 次（术语表指定用「%s」）"
                            % (word, count, term))
    return crit, warn


def load_param_rows(body):
    """取「参数 | 设定值」类表格的行，只保留单值（区间不查）。"""
    rows, header = [], None
    for line in body.splitlines():
        text = line.strip()
        if not text.startswith("|"):
            if header is not None:
                header = None
            continue
        cells = [x.strip() for x in text.strip("|").split("|")]
        if set("".join(cells)) <= set("-: "):
            continue
        if header is None:
            header = cells
            continue
        if len(cells) != len(header):
            continue
        rec = dict(zip(header, cells))
        name = next((rec.get(h) for h in PARAM_HEADERS if rec.get(h)), "")
        val = next((rec.get(h) for h in VALUE_HEADERS if rec.get(h)), "")
        if not name or not val:
            continue
        if any(mark in val for mark in RANGE_MARKS):
            continue
        if not PARAM_NUM.search(val):
            continue
        rows.append((name, PARAM_NUM.search(val).group(0)))
    return rows


def check_numbers(body):
    """正文里同一参数的数值必须与参数表一致（窄口径：只查单值参数）。"""
    warn = []
    for name, expected in load_param_rows(body):
        seen = set()
        for line in body.splitlines():
            if line.strip().startswith("|"):
                continue
            start = 0
            while True:
                idx = line.find(name, start)
                if idx < 0:
                    break
                start = idx + len(name)
                window = line[idx + len(name): idx + len(name) + 24]
                hit = PARAM_NUM.search(window)
                if not hit:
                    continue
                found = hit.group(0)
                if found != expected and found not in seen:
                    seen.add(found)
                    warn.append("[number] 参数「%s」表内为 %s，正文出现 %s"
                                % (name, expected, found))
    return warn


def check(path, ftype, min_words, max_words, citations_csv):
    crit, warn = [], []

    if path.lower().endswith(".docx"):
        try:
            raw = read_docx_text(path)
        except SystemExit:
            raise
        except Exception as exc:
            return None, "无法读取 docx（%s）：%s" % (path, exc)
    else:
        try:
            raw = io.open(path, encoding="utf-8").read()
        except UnicodeDecodeError:
            try:
                raw = io.open(path, encoding="utf-8-sig").read()
            except OSError as exc:
                return None, str(exc)
        except OSError as exc:
            return None, str(exc)

    body = strip_code(raw)

    gcrit, gwarn = check_glossary(path, body)
    crit.extend(gcrit)
    warn.extend(gwarn)
    warn.extend(check_numbers(body))

    fences = raw.count("```")
    if fences % 2:
        crit.append("[fence] 代码围栏不配对：%d 个 ```" % fences)

    for label, pat in PLACEHOLDERS:
        hits = re.findall(pat, raw, flags=re.IGNORECASE)
        if hits:
            crit.append("[placeholder] 残留占位符「%s」×%d" % (label, len(hits)))

    head = REF_HEAD.search(body)
    if head:
        cite_part = body[: head.start()]
        ref_part = body[head.end():]
        entries = split_entries(ref_part)
        ids = [e["id"] for e in entries]
        dup = sorted({n for n in ids if ids.count(n) > 1})
        if dup:
            crit.append("[ref] 参考文献编号重复：%s" % dup)
        cited = parse_citations(cite_part)
        listed = set(ids)
        missing = sorted(cited - listed)
        orphan = sorted(listed - cited)
        if missing:
            crit.append("[citation] 正文引用但文献表缺失：%s" % missing)
        if orphan:
            warn.append("[citation] 文献表有条目未被正文引用：%s" % orphan)
        if cited and not entries:
            crit.append("[ref] 有引用标记但文献表为空")
        entry_crit, entry_warn = validate_entries(entries)
        crit.extend(entry_crit)
        warn.extend(entry_warn)
    else:
        cited = parse_citations(body)
        entries = []
        ids = []
        if cited:
            warn.append("[ref] 正文有引用标记但找不到参考文献节")

    if cited and not citations_csv:
        warn.append("[csv] 正文有引用但未提供 citations.csv，引用事实未核对")

    if citations_csv:
        try:
            csv_rows = load_citations_csv(citations_csv)
        except (OSError, ValueError) as exc:
            return None, "citations.csv 读取失败：%s" % exc
        cited = parse_citations(body[: head.start()] if head else body)
        absent = sorted(cited - set(csv_rows))
        if absent:
            crit.append("[csv] 正文引用了 citations.csv 中不存在的编号：%s" % absent)
        extra = sorted(set(csv_rows) - cited)
        if extra:
            warn.append("[csv] citations.csv 有条目未被正文引用：%s" % extra)
        unverified = sorted(i for i in cited & set(csv_rows) if csv_rows[i] != "y")
        if unverified:
            warn.append("[csv] 引用的条目未核验（verified != y）：%s" % unverified)
        if len(csv_rows) != len(ids):
            warn.append(
                "[csv] citations.csv 条目数（%d）与文献表条目数（%d）不一致"
                % (len(csv_rows), len(ids))
            )

    caption_nums, caption_idx = set(), set()
    body_lines = body.splitlines()
    for i, line in enumerate(body_lines):
        m = CAP_START.match(line)
        if not m:
            continue
        num = int(m.group(2))
        tail = m.group(3)
        if tail[:3].strip()[:1] in (":", "：") or (
            len(line.strip()) <= 80 and not REF_WORDS.search(line)
        ):
            caption_nums.add(num)
            caption_idx.add(i)

    non_caption = "\n".join(l for i, l in enumerate(body_lines) if i not in caption_idx)
    refs = {int(num) for _kind, num in CAP_REF.findall(non_caption)}

    if caption_nums:
        no_caption = sorted(refs - caption_nums)
        if no_caption:
            warn.append("[figure] 正文引用了没有图/表标题的编号：%s" % no_caption)
        never = sorted(caption_nums - refs)
        if never:
            warn.append("[figure] 图/表有标题但正文未引用：%s" % never)
    elif refs:
        warn.append(
            "[figure] 正文引用了图/表编号（%s）但未检测到图/表标题；"
            "若用 Word 图注可忽略" % sorted(refs)
        )

    for label, pat in BANNED_CRITICAL:
        hits = re.findall(pat, body, flags=re.IGNORECASE)
        if hits:
            crit.append("[defensive] 自我削弱措辞「%s」×%d" % (label, len(hits)))
    for label, pat in BANNED_WARN:
        hits = re.findall(pat, body, flags=re.IGNORECASE)
        if hits:
            warn.append("[tone] 需人工判断「%s」×%d" % (label, len(hits)))

    dashes = len(EM_DASH.findall(body))
    if dashes > 3:
        warn.append("[tone] 破折号 %d 处，检查是否当连接词使用" % dashes)

    have = headings(body)
    for group in SECTIONS.get(ftype, []):
        alts = [a.strip() for a in group.split("|")]
        if not any(any(a.lower() in h.lower() for a in alts) for h in have):
            crit.append("[section] 缺少章节：%s" % group)

    words = count_words(body)
    if min_words and words < min_words:
        warn.append("[length] 字数 %d < 下限 %d" % (words, min_words))
    if max_words and words > max_words:
        warn.append("[length] 字数 %d > 上限 %d" % (words, max_words))

    return {
        "path": os.path.abspath(path),
        "type": ftype,
        "words": words,
        "critical": crit,
        "warn": warn,
    }, None


def main():
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")

    ap = argparse.ArgumentParser(
        description="Structural self-check for a Markdown or .docx draft.",
        epilog="退出码：0 无 CRITICAL（可能仍有 WARN）；1 有 CRITICAL；"
               "2 用法或文件读取错误（含 .docx 无法解析）。"
               "WARN 不改变退出码，需自行判断。")
    ap.add_argument("file")
    ap.add_argument("--type", default="course", choices=sorted(SECTIONS))
    ap.add_argument("--min-words", type=int, default=0)
    ap.add_argument("--max-words", type=int, default=0)
    ap.add_argument("--citations-csv", default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    result, err = check(
        args.file, args.type, args.min_words, args.max_words, args.citations_csv
    )
    if err:
        print("ERROR: %s" % err, file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("check.py — %s" % result["path"])
        print("type=%s  words=%d" % (result["type"], result["words"]))
        for label, items in (("CRITICAL", result["critical"]), ("WARN", result["warn"])):
            print("%s: %d" % (label, len(items)))
            for item in items:
                print("  - %s" % item)
        verdict = "FAIL" if result["critical"] else "PASS"
        print("RESULT: %s (%d critical, %d warn)" % (verdict, len(result["critical"]), len(result["warn"])))

    return 1 if result["critical"] else 0


if __name__ == "__main__":
    sys.exit(main())
