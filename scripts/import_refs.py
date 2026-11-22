#!/usr/bin/env python3
"""Import exported reference files (RIS / BibTeX / CSL-JSON) into citations.csv.

This is the *intake* stage: databases export references in their own formats;
this script turns them into rows of the citation contract so that
`verify_refs.py` can then check each one against the DOI registry.

Imported rows are intentionally written as **unverified** (`verified_by` empty):
an export is metadata, not proof. Run verify_refs.py, then fill verified_by.

Usage:
  python scripts/import_refs.py refs.ris --csv citations.csv --dry-run
  python scripts/import_refs.py cnki.ris wanfang.ris ieee.bib --csv citations.csv
  python scripts/import_refs.py refs.json --csv citations.csv --start-id 12

Exit codes: 0 ok, 1 no importable records, 2 usage/file error.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys

FIELDS = ["id", "authors", "year", "title", "venue", "doi_or_url", "page",
          "verified_by", "verified_on", "supports", "type"]

RIS_TYPE = {
    "JOUR": "J", "JFULL": "J", "MGZN": "J", "BOOK": "M", "CHAP": "M",
    "CONF": "C", "CPAPER": "C", "THES": "D", "RPRT": "R", "STAND": "S",
    "PAT": "P", "NEWS": "N", "ELEC": "EB/OL", "WEB": "EB/OL", "GEN": "M",
}
BIB_TYPE = {
    "article": "J", "book": "M", "inbook": "M", "incollection": "M",
    "inproceedings": "C", "conference": "C", "proceedings": "C",
    "phdthesis": "D", "mastersthesis": "D", "techreport": "R",
    "standard": "S", "patent": "P", "misc": "EB/OL", "online": "EB/OL",
}
CSL_TYPE = {
    "article-journal": "J", "article-magazine": "J", "article-newspaper": "N",
    "book": "M", "chapter": "M", "paper-conference": "C", "thesis": "D",
    "report": "R", "webpage": "EB/OL", "patent": "P", "standard": "S",
}

CJK = re.compile(r"[\u3400-\u9fff]")


def read_text(path: str) -> str:
    raw = open(path, "rb").read()
    for enc in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", "replace")


def norm_authors(pairs: list[str]) -> str:
    """Normalize to `Zhang S; Li Y` (CJK names kept whole)."""
    out = []
    for raw in pairs:
        name = re.sub(r"\s+", " ", raw.replace("\n", " ")).strip().strip(".")
        if not name or name.lower() in ("and", "et al", "et al."):
            continue
        if CJK.search(name):
            out.append(name.replace(",", " ").strip())
            continue
        if "," in name:
            family, given = [p.strip() for p in name.split(",", 1)]
        else:
            bits = name.split()
            if len(bits) == 1:
                out.append(bits[0])
                continue
            family, given = bits[-1], " ".join(bits[:-1])
        initials = "".join(w[0].upper() for w in re.split(r"[\s.\-]+", given) if w)
        out.append(f"{family} {initials}".strip())
    return "; ".join(out)


def norm_page(sp: str, ep: str = "") -> str:
    sp, ep = (sp or "").strip(), (ep or "").strip()
    if sp and ep and sp != ep:
        return f"{sp}-{ep}"
    return sp or ep


# ---------------------------------------------------------------- RIS
def parse_ris(text: str) -> list[dict]:
    recs, cur, last = [], {}, None
    for line in text.splitlines():
        m = re.match(r"^([A-Z][A-Z0-9])  - ?(.*)$", line.rstrip())
        if m:
            tag, val = m.group(1), m.group(2).strip()
            last = tag
            if tag == "ER":
                if cur:
                    recs.append(cur)
                cur, last = {}, None
                continue
            cur.setdefault(tag, []).append(val)
        elif last and line.strip():
            cur[last][-1] += " " + line.strip()
    if cur:
        recs.append(cur)
    rows = []
    for r in recs:
        get = lambda k: (r.get(k) or [""])[0]
        rows.append({
            "type": RIS_TYPE.get(get("TY").upper(), "M"),
            "authors": norm_authors(r.get("AU") or r.get("A1") or []),
            "year": (re.search(r"\d{4}", get("PY") or get("Y1") or "") or [""])[0]
                    if re.search(r"\d{4}", get("PY") or get("Y1") or "") else "",
            "title": get("TI") or get("T1"),
            "venue": get("T2") or get("JO") or get("JF") or get("BT") or get("PB"),
            "doi_or_url": get("DO") or get("UR"),
            "page": norm_page(get("SP"), get("EP")),
        })
    return rows


# ---------------------------------------------------------------- BibTeX
def parse_bib(text: str) -> list[dict]:
    rows = []
    for m in re.finditer(r"@(\w+)\s*[{(]", text):
        kind = m.group(1).lower()
        if kind in ("comment", "string", "preamble"):
            continue
        i, depth = m.end(), 1
        while i < len(text) and depth:
            if text[i] in "{(":
                depth += 1
            elif text[i] in "})":
                depth -= 1
            i += 1
        body = text[m.end():i - 1]
        fields = {}
        for fm in re.finditer(r"(\w+)\s*=\s*(\{(?:[^{}]|\{[^{}]*\})*\}|\"[^\"]*\"|[^,]+)", body):
            key = fm.group(1).lower()
            val = fm.group(2).strip()
            if val.startswith("{") and val.endswith("}"):
                val = val[1:-1]
            elif val.startswith('"') and val.endswith('"'):
                val = val[1:-1]
            fields[key] = re.sub(r"\s+", " ", val).strip()
        authors = [a for a in re.split(r"\s+and\s+", fields.get("author", "")) if a.strip()]
        rows.append({
            "type": BIB_TYPE.get(kind, "M"),
            "authors": norm_authors(authors),
            "year": fields.get("year", ""),
            "title": fields.get("title", ""),
            "venue": fields.get("journal") or fields.get("booktitle")
                     or fields.get("publisher") or fields.get("school") or "",
            "doi_or_url": fields.get("doi") or fields.get("url") or "",
            "page": norm_page(*fields.get("pages", "").split("--")) if "--" in fields.get("pages", "") else fields.get("pages", ""),
        })
    return rows


# ---------------------------------------------------------------- CSL-JSON
def parse_csl(text: str) -> list[dict]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return []
    if isinstance(data, dict):
        data = data.get("items") or [data]
    rows = []
    for it in data:
        if not isinstance(it, dict):
            continue
        authors = []
        for a in it.get("author") or []:
            if isinstance(a, dict):
                if a.get("family") and a.get("given"):
                    authors.append(f"{a['family']}, {a['given']}")
                else:
                    authors.append(a.get("family") or a.get("literal") or "")
            elif isinstance(a, str):
                authors.append(a)
        year = ""
        issued = ((it.get("issued") or {}).get("date-parts") or [[None]])[0]
        if issued and issued[0]:
            year = str(issued[0])
        elif it.get("year"):
            year = str(it["year"])
        rows.append({
            "type": CSL_TYPE.get(it.get("type", ""), "M"),
            "authors": norm_authors(authors),
            "year": year,
            "title": it.get("title", ""),
            "venue": it.get("container-title") or it.get("publisher") or it.get("publisher-place") or "",
            "doi_or_url": it.get("DOI") or it.get("URL") or "",
            "page": it.get("page", ""),
        })
    return rows


def parse_file(path: str) -> list[dict]:
    text = read_text(path)
    ext = os.path.splitext(path)[1].lower()
    if ext == ".bib" or re.search(r"^@\w+\s*[{(]", text, re.M):
        return parse_bib(text)
    if ext == ".json" or text.lstrip().startswith(("[", "{")):
        rows = parse_csl(text)
        if rows:
            return rows
    return parse_ris(text)


def load_csv(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return [r for r in csv.DictReader(fh) if (r.get("id") or "").strip()]


def norm_doi(value: str) -> str:
    v = (value or "").strip().lower()
    v = re.sub(r"^https?://(dx\.)?doi\.org/", "", v)
    return v


def main(argv: list[str] | None = None) -> int:
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description="Import RIS/BibTeX/CSL-JSON into citations.csv")
    p.add_argument("files", nargs="+")
    p.add_argument("--csv", default="citations.csv")
    p.add_argument("--start-id", type=int)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args(argv)

    existing = load_csv(args.csv)
    seen_dois = {norm_doi(r.get("doi_or_url", "")) for r in existing if r.get("doi_or_url")}
    seen_titles = {(r.get("title", "").strip().lower(), (r.get("year") or "").strip()) for r in existing}
    next_id = args.start_id or (max((int(r["id"]) for r in existing if r["id"].isdigit()), default=0) + 1)

    imported, skipped = [], []
    for path in args.files:
        if not os.path.exists(path):
            print(f"文件不存在：{path}", file=sys.stderr)
            return 2
        for rec in parse_file(path):
            doi = norm_doi(rec.get("doi_or_url", ""))
            key = (rec.get("title", "").strip().lower(), str(rec.get("year", "")).strip())
            if (doi and doi in seen_dois) or (key in seen_titles):
                skipped.append(rec)
                continue
            if not rec.get("title"):
                skipped.append(rec)
                continue
            row = {
                "id": str(next_id),
                "authors": rec.get("authors", ""),
                "year": str(rec.get("year", "")),
                "title": rec.get("title", ""),
                "venue": rec.get("venue", ""),
                "doi_or_url": rec.get("doi_or_url", ""),
                "page": rec.get("page", ""),
                "verified_by": "",
                "verified_on": "",
                "supports": "",
                "type": rec.get("type", ""),
            }
            imported.append(row)
            if doi:
                seen_dois.add(doi)
            seen_titles.add(key)
            next_id += 1

    if not imported:
        print(f"没有可导入的新记录（{len(skipped)} 条重复或缺题名）。")
        return 1 if skipped else 0

    if args.dry_run:
        print(f"[dry-run] 将导入 {len(imported)} 条到 {args.csv}，跳过 {len(skipped)} 条重复：")
    else:
        new_file = not os.path.exists(args.csv)
        with open(args.csv, "a", newline="", encoding="utf-8-sig") as fh:
            writer = csv.DictWriter(fh, fieldnames=FIELDS)
            if new_file:
                writer.writeheader()
            writer.writerows(imported)
        print(f"已导入 {len(imported)} 条到 {args.csv}，跳过 {len(skipped)} 条重复：")

    for r in imported:
        print(f"  [{r['id']}] {r['year']} {r['authors'][:28]:28} {r['title'][:48]}  ({r['type']})")
    print("\n下一步（必做）：这些行都是未核验状态。逐条核验：")
    print(f"  python scripts/verify_refs.py --csv {args.csv} --only {imported[0]['id']}")
    print("  核验通过后再填 verified_by / verified_on / supports；未通过就删掉这条。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
