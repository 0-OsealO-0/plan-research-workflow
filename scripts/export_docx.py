#!/usr/bin/env python3
"""Export a Markdown paper to .docx with a school/journal template.

Usage:
    python scripts/export_docx.py paper.md
    python scripts/export_docx.py paper.md --template 课程论文模板.docx
    python scripts/export_docx.py paper.md --references-csv citations.csv
    python scripts/export_docx.py paper.md --title "..." --author "..." --course "..."

The template supplies page size, margins, headers/footers and styles. The
converter then appends the Markdown content using the template's own styles, so
a school .docx template keeps its look instead of being reformatted.

Supported Markdown subset: headings (#..####), paragraphs, bullet/numbered
lists, bold/italic/inline-code, pipe tables, fenced code blocks, blockquotes,
images (![alt](path)), horizontal rules (dropped).
"""

import argparse
import csv
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _runtime import ensure_docx  # noqa: E402

docx = ensure_docx()
from docx.shared import Cm, Pt  # noqa: E402
from docx.oxml import OxmlElement  # noqa: E402
from docx.oxml.ns import qn  # noqa: E402
from docx.enum.text import WD_ALIGN_PARAGRAPH  # noqa: E402

CJK = re.compile(r"[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]")
TOKEN = re.compile(r"(\*\*.+?\*\*|~~.+?~~|`[^`]+`|\*[^*\n]+?\*|\[[^\]]+\]\([^)]+\))")

HEADING_STYLES = [
    ["Title", "标题"],
    ["Heading 1", "标题 1", "heading 1"],
    ["Heading 2", "标题 2", "heading 2"],
    ["Heading 3", "标题 3", "heading 3"],
    ["Heading 4", "标题 4", "heading 4"],
]
BULLET_STYLES = [["List Bullet", "列表项目符号"], ["List Bullet 2", "列表项目符号 2"], ["List Bullet 3", "列表项目符号 3"]]
NUMBER_STYLES = [["List Number", "列表编号"]]
QUOTE_STYLES = [["Quote", "引用"], ["Intense Quote", "明显引用"]]
TABLE_STYLES = [["Table Grid", "网格型"], ["Light Grid Accent 1", "浅色网格强调 1"]]

TYPE_DEFAULT = "J"
TYPE_HINT = [
    ("会议", "C"), ("Proceedings", "C"), ("Conference", "C"), ("Symposium", "C"),
    ("学位论文", "D"), ("硕士", "D"), ("博士", "D"),
    ("标准", "S"), ("专利", "P"), ("报告", "R"), ("报纸", "N"),
    ("arXiv", "EB/OL"), ("预印本", "EB/OL"), ("网站", "EB/OL"),
]


def pick_style(doc, names, fallback=None):
    for name in names:
        try:
            return doc.styles[name]
        except KeyError:
            continue
    return fallback


def join_lines(lines):
    out = ""
    for line in lines:
        if not out:
            out = line
        elif CJK.search(out[-1:]) and CJK.search(line[:1]):
            out += line
        else:
            out += " " + line
    return out


def add_runs(paragraph, text):
    """Render **bold**, *italic*, `code`, ~~strike~~ and links."""
    pos = 0
    for m in TOKEN.finditer(text):
        if m.start() > pos:
            paragraph.add_run(text[pos:m.start()])
        tok = m.group(0)
        if tok.startswith("**"):
            paragraph.add_run(tok[2:-2]).bold = True
        elif tok.startswith("~~"):
            paragraph.add_run(tok[2:-2]).font.strike = True
        elif tok.startswith("`"):
            run = paragraph.add_run(tok[1:-1])
            run.font.name = "Consolas"
            run.font.size = Pt(9)
        elif tok.startswith("*"):
            paragraph.add_run(tok[1:-1]).italic = True
        else:  # [text](url)
            label, url = re.match(r"\[([^\]]+)\]\(([^)]+)\)", tok).groups()
            paragraph.add_run(label)
            if url != label:
                paragraph.add_run("（%s）" % url).font.size = Pt(9)
        pos = m.end()
    if pos < len(text):
        paragraph.add_run(text[pos:])


def add_paragraph(doc, text, style=None):
    p = doc.add_paragraph(style=style) if style is not None else doc.add_paragraph()
    add_runs(p, text)
    return p


def add_code_block(doc, lines):
    for line in lines:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(line if line else " ")
        run.font.name = "Consolas"
        run.font.size = Pt(9)


def add_table(doc, rows):
    header = [c.strip() for c in rows[0].strip().strip("|").split("|")]
    body = []
    for raw in rows[1:]:
        if re.match(r"^\s*\|?[\s:|-]+\|?\s*$", raw):
            continue
        body.append([c.strip() for c in raw.strip().strip("|").split("|")])
    ncols = max([len(header)] + [len(r) for r in body]) if body else len(header)
    table = doc.add_table(rows=1 + len(body), cols=ncols)
    style = pick_style(doc, TABLE_STYLES[0])
    if style is not None:
        table.style = style
    table.autofit = True
    for j in range(ncols):
        cell = table.rows[0].cells[j]
        cell.text = ""
        run = cell.paragraphs[0].add_run(header[j] if j < len(header) else "")
        run.bold = True
    for i, row in enumerate(body, start=1):
        for j in range(ncols):
            cell = table.rows[i].cells[j]
            cell.text = ""
            cell.paragraphs[0].add_run(row[j] if j < len(row) else "")
    doc.add_paragraph()


def add_image(doc, path, alt):
    if not os.path.isfile(path):
        add_paragraph(doc, "［缺图：%s］" % path)
        return
    try:
        shape = doc.add_picture(path, width=Cm(14))
        if alt:
            # alt 写进图片描述即可；Markdown 自带「图 N　…」图注，不再重复生成一段
            try:
                for doc_pr in shape._inline.docPr:
                    doc_pr.set("descr", alt)
                    doc_pr.set("title", alt)
            except Exception:
                pass
    except Exception as exc:  # unreadable image
        add_paragraph(doc, "［图片无法插入：%s（%s）］" % (path, exc))


def _norm_title(text):
    """去掉空白与常见标点，用于判断 Markdown 首行标题与 --title 是否同一句。"""
    text = re.sub(r"\s+", "", text or "")
    return re.sub(r"[「」『』《》〈〉“”‘’\"'：:，,。.]", "", text)


def first_md_heading(text):
    """返回 Markdown 里第一个标题的 (level, text)；首行不是标题时返回 None。"""
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        m = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if m:
            return len(m.group(1)), m.group(2).strip()
        return None
    return None


def parse_markdown(doc, text):
    lines = text.splitlines()
    i = 0
    buffer = []
    in_code = False
    code_lines = []

    def flush():
        nonlocal buffer
        if buffer:
            add_paragraph(doc, join_lines(buffer))
            buffer = []

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("```"):
            if in_code:
                add_code_block(doc, code_lines)
                code_lines = []
                in_code = False
            else:
                flush()
                in_code = True
            i += 1
            continue
        if in_code:
            code_lines.append(line)
            i += 1
            continue

        if not stripped:
            flush()
            i += 1
            continue

        m = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if m:
            flush()
            level = len(m.group(1))
            style = pick_style(doc, HEADING_STYLES[level - 1]) if level - 1 < len(HEADING_STYLES) else None
            p = doc.add_paragraph(style=style) if style is not None else doc.add_paragraph()
            add_runs(p, m.group(2))
            for _r in p.runs:
                _r.bold = True
            i += 1
            continue

        if stripped.startswith("|") and i + 1 < len(lines) and "|" in lines[i + 1]:
            flush()
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i])
                i += 1
            add_table(doc, rows)
            continue

        m = re.match(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$", line)
        if m:
            flush()
            indent = len(m.group(1))
            ordered = m.group(2)[0].isdigit()
            idx = min(indent // 2, 2)
            styles = NUMBER_STYLES if ordered else BULLET_STYLES
            names = styles[min(idx, len(styles) - 1)]
            style = pick_style(doc, names)
            p = doc.add_paragraph(style=style) if style is not None else doc.add_paragraph()
            add_runs(p, m.group(3))
            if style is None:  # template without list styles: fake the indent
                p.paragraph_format.left_indent = Cm(0.74 * (idx + 1))
                p.paragraph_format.first_line_indent = Cm(-0.5)
            i += 1
            continue

        if stripped.startswith(">"):
            flush()
            style = pick_style(doc, QUOTE_STYLES[0])
            add_paragraph(doc, stripped.lstrip("> ").strip(), style)
            i += 1
            continue

        m = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$", stripped)
        if m:
            flush()
            add_image(doc, m.group(2), m.group(1))
            i += 1
            continue

        if re.match(r"^(-{3,}|\*{3,}|_{3,})$", stripped):
            flush()
            i += 1
            continue

        buffer.append(stripped)
        i += 1

    flush()
    if in_code and code_lines:
        add_code_block(doc, code_lines)


# ---------------------------------------------------------------- references
def load_csv(path):
    with open(path, "r", encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    out = {}
    for row in rows:
        clean = {(k or "").strip().lower(): (v or "").strip() for k, v in row.items()}
        rid = clean.get("id", "")
        if rid:
            out[rid] = clean
    return out


def guess_type(row, default):
    explicit = (row.get("type") or "").strip().upper()
    if explicit:
        return explicit
    venue = row.get("venue", "") + " " + row.get("title", "")
    for needle, code in TYPE_HINT:
        if needle and needle.lower() in venue.lower():
            return code
    return default


def reference_line(rid, row, default_type):
    rtype = guess_type(row, default_type)
    authors = re.sub(r"\s*[;；]\s*", ", ", row.get("authors", "") or "［缺作者］")
    title = row.get("title", "") or "［缺题名］"
    # GB/T 7714: >3 authors keep the first three plus 等 / et al. (等 for Chinese).
    authors = authors.rstrip(".。 ")
    cjk = bool(re.search(r"[\u4e00-\u9fff]", authors + title))
    marker = "等" if cjk else "et al"
    names = [a.strip() for a in authors.split(",") if a.strip()]
    truncated = [a for a in names if not re.match(r"^(et\s+al\.?|等)$", a, re.I)]
    if len(truncated) > 3:
        truncated = truncated[:3]
    if len(truncated) < len(names):
        authors = ", ".join(truncated) + ", " + marker
    else:
        authors = ", ".join(truncated)
    venue = row.get("venue", "")
    year = row.get("year", "")
    page = row.get("page", "")
    doi = row.get("doi_or_url", "")
    place = row.get("place", "")
    publisher = row.get("publisher", "") or venue
    vol = row.get("volume_issue", "")
    accessed = row.get("accessed", "")

    if rtype == "J":
        tail = "%s, %s" % (venue, year) if venue else str(year)
        if vol:
            tail += ", %s" % vol
        if page:
            tail += ": %s" % page
        s = "%s. %s[J]. %s." % (authors, title, tail)
    elif rtype == "M":
        s = "%s. %s[M]. %s: %s, %s" % (authors, title, place or "［缺出版地］", publisher or "［缺出版社］", year)
        if page:
            s += ": %s" % page
        s += "."
    elif rtype == "C":
        s = "%s. %s[C]//%s. %s" % (authors, title, venue or "［缺会议名］", year)
        if page:
            s += ": %s" % page
        s += "."
    elif rtype == "D":
        s = "%s. %s[D]. %s: %s, %s." % (authors, title, place or "［缺城市］", publisher or "［缺学校］", year)
    elif rtype in ("S", "P", "R", "N"):
        s = "%s. %s[%s]. %s, %s." % (authors, title, rtype, venue, year)
    else:  # EB/OL and anything unknown
        url = doi or ""
        if url and not url.startswith("http"):
            url = "https://doi.org/" + url
        s = "%s. %s[EB/OL]. (%s). %s" % (authors, title, year, url or "［缺URL］")
        if accessed:
            s += "［%s］" % accessed
        s = s.rstrip()
        if not s.endswith("."):
            s += "."
    if doi and rtype != "EB/OL" and doi.startswith("10."):
        s = s.rstrip(".") + ". DOI: %s." % doi
    return "[%s] %s" % (rid, s)


def append_references(doc, csv_path, default_type):
    rows = load_csv(csv_path)

    def key(item):
        return (0, int(item[0])) if item[0].isdigit() else (1, item[0])

    heading_style = pick_style(doc, HEADING_STYLES[1])
    p = doc.add_paragraph(style=heading_style) if heading_style else doc.add_paragraph()
    add_runs(p, "参考文献")
    for _r in p.runs:
        _r.bold = True
    for rid, row in sorted(rows.items(), key=key):
        para = add_paragraph(doc, reference_line(rid, row, default_type))
        try:
            para.paragraph_format.left_indent = Cm(0.74)
            para.paragraph_format.first_line_indent = Cm(-0.74)
            para.paragraph_format.space_after = Pt(0)
        except Exception:
            pass
    return len(rows)


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass
    ap = argparse.ArgumentParser(description="Export Markdown to .docx (template aware).")
    ap.add_argument("source")
    ap.add_argument("--out", default="")
    ap.add_argument("--template", default="")
    ap.add_argument("--title", default="")
    ap.add_argument("--author", default="")
    ap.add_argument("--course", default="")
    ap.add_argument("--header", default="")
    ap.add_argument("--references-csv", default="")
    ap.add_argument("--references-mode", default="auto", choices=["auto", "append", "skip"],
                    help="auto: replace an existing 参考文献 section in the Markdown, "
                         "append when there is none; append: always add another section; skip: ignore the CSV")
    ap.add_argument("--default-type", default=TYPE_DEFAULT,
                    help="GB/T 7714 type code when the CSV has no type column (default J)")
    args = ap.parse_args(argv)

    if not os.path.isfile(args.source):
        sys.stderr.write("找不到源文件：%s\n" % args.source)
        return 2
    if args.template and not os.path.isfile(args.template):
        sys.stderr.write("找不到模板：%s\n" % args.template)
        return 2

    with open(args.source, "r", encoding="utf-8-sig") as fh:
        text = fh.read()

    if args.template:
        doc = docx.Document(args.template)
        # 模板自带封面时另起一页；空模板（只有样式）不留空白首页
        if any(par.text.strip() for par in doc.paragraphs):
            doc.add_page_break()
        doc.core_properties.title = args.title or doc.core_properties.title
    else:
        doc = docx.Document()

    md_head = first_md_heading(text)
    title_in_md = bool(args.title and md_head and md_head[0] == 1
                       and _norm_title(md_head[1]) == _norm_title(args.title))
    if args.title and title_in_md:
        print("提示：Markdown 首行已是同名标题，跳过 --title 注入（避免两个标题）")
    if args.title and not title_in_md:
        style = pick_style(doc, HEADING_STYLES[0])
        p = doc.add_paragraph(style=style) if style else doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_runs(p, args.title)
    for meta in (args.author, args.course):
        if meta:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            add_runs(p, meta)

    if args.header:
        for section in doc.sections:
            para = section.header.paragraphs[0]
            para.text = args.header

    for section in doc.sections:
        try:
            foot = section.footer.paragraphs[0]
        except Exception:
            continue
        if foot.text.strip():
            continue
        foot.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = foot.add_run()
        fld = OxmlElement("w:fldSimple")
        fld.set(qn("w:instr"), "PAGE")
        inner = OxmlElement("w:r")
        txt = OxmlElement("w:t")
        txt.text = "1"
        inner.append(txt)
        fld.append(inner)
        run._r.addnext(fld)

    body_text = text
    replaced_refs = False
    if args.references_csv and args.references_mode != "skip":
        head = re.search(
            r"(?m)^#{1,6}[ \t]*(参考文献|文献目录|references?|bibliography)[ \t]*$",
            text,
            re.IGNORECASE,
        )
        if head and args.references_mode in ("auto", "append"):
            body_text = text[: head.start()]
            replaced_refs = True

    parse_markdown(doc, body_text)
    nrefs = 0
    if args.references_csv and args.references_mode != "skip":
        nrefs = append_references(doc, args.references_csv, args.default_type)

    out = args.out or os.path.splitext(args.source)[0] + ".docx"
    if os.path.exists(out) and os.path.abspath(out) != os.path.abspath(args.source):
        sys.stderr.write("注意：覆盖已有文件 %s（请先运行 status.py backup）\n" % out)
    # 标题一律显式加粗：避免某段由不同路径生成时字重不一
    for _par in doc.paragraphs:
        try:
            _name = _par.style.name if _par.style is not None else ""
        except Exception:
            _name = ""
        if _name.startswith(("Title", "Heading", "标题")):
            for _r in _par.runs:
                _r.bold = True
    doc.save(out)
    paras = len(doc.paragraphs)
    print("已导出：%s" % out)
    print("段落 %d · 参考文献 %d%s · 模板：%s"
          % (paras, nrefs, "（替换了 Markdown 里的旧文献表）" if replaced_refs else "",
             args.template or "无（默认样式）"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
