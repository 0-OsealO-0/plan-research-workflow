#!/usr/bin/env python3
"""Search open bibliographic metadata (OpenAlex / Crossref).

This is the *metadata* stage of the literature chain: it finds candidate
papers, their DOIs, venues and years. It does NOT authenticate to any
library database and cannot fetch full text.

Usage:
  python scripts/search_meta.py "network traffic anomaly detection" --limit 10
  python scripts/search_meta.py "图神经网络" --source openalex --year-from 2020
  python scripts/search_meta.py --doi 10.1038/nature12373
  python scripts/search_meta.py "topic" --json

Exit codes: 0 ok, 2 network/usage error.
"""
from __future__ import annotations

import argparse
import io
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

UA = "plan-research-workflow/1.0 (literature metadata search)"
OPENALEX = "https://api.openalex.org"
CROSSREF = "https://api.crossref.org"


def fetch_json(url: str, timeout: int = 25) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", "replace"))


def _first_author(authorships) -> str:
    for a in authorships or []:
        name = (a.get("author") or {}).get("display_name")
        if name:
            return name
    return ""


def _venue(work) -> str:
    loc = work.get("primary_location") or {}
    src = loc.get("source") or {}
    return src.get("display_name") or ""


def search_openalex(query: str, limit: int, year_from: int | None, year_to: int | None,
                    mailto: str | None) -> list[dict]:
    params = {"search": query, "per-page": str(max(1, min(limit, 50)))}
    filters = []
    if year_from:
        filters.append(f"from_publication_date:{year_from}-01-01")
    if year_to:
        filters.append(f"to_publication_date:{year_to}-12-31")
    if filters:
        params["filter"] = ",".join(filters)
    if mailto:
        params["mailto"] = mailto
    data = fetch_json(f"{OPENALEX}/works?{urllib.parse.urlencode(params)}")
    out = []
    for w in data.get("results", []):
        out.append({
            "source": "openalex",
            "title": (w.get("display_name") or "").strip(),
            "year": w.get("publication_year"),
            "authors": _first_author(w.get("authorships")),
            "venue": _venue(w),
            "doi": (w.get("doi") or "").replace("https://doi.org/", ""),
            "cited_by": w.get("cited_by_count"),
            "type": w.get("type"),
        })
    return out


def search_crossref(query: str, limit: int, year_from: int | None, year_to: int | None,
                    mailto: str | None) -> list[dict]:
    params = {"query": query, "rows": str(max(1, min(limit, 50))),
              "select": "DOI,title,author,issued,container-title,type,is-referenced-by-count"}
    if year_from or year_to:
        lo = year_from or 1000
        hi = year_to or 3000
        params["filter"] = f"from-pub-date:{lo}-01-01,until-pub-date:{hi}-12-31"
    if mailto:
        params["mailto"] = mailto
    data = fetch_json(f"{CROSSREF}/works?{urllib.parse.urlencode(params)}")
    out = []
    for it in (data.get("message") or {}).get("items", []):
        authors = it.get("author") or []
        first = ""
        if authors:
            a = authors[0]
            first = (" ".join(x for x in [a.get("given"), a.get("family")] if x)).strip()
        parts = ((it.get("issued") or {}).get("date-parts") or [[None]])[0]
        out.append({
            "source": "crossref",
            "title": ((it.get("title") or [""])[0] or "").strip(),
            "year": parts[0] if parts else None,
            "authors": first,
            "venue": ((it.get("container-title") or [""])[0] or "").strip(),
            "doi": it.get("DOI") or "",
            "cited_by": it.get("is-referenced-by-count"),
            "type": it.get("type"),
        })
    return out


def lookup_doi(doi: str, mailto: str | None) -> dict | None:
    doi = doi.strip().replace("https://doi.org/", "")
    params = {"mailto": mailto} if mailto else {}
    try:
        w = fetch_json(f"{OPENALEX}/works/doi:{urllib.parse.quote(doi)}?{urllib.parse.urlencode(params)}")
        return {
            "source": "openalex",
            "title": (w.get("display_name") or "").strip(),
            "year": w.get("publication_year"),
            "authors": _first_author(w.get("authorships")),
            "venue": _venue(w),
            "doi": doi,
            "cited_by": w.get("cited_by_count"),
            "type": w.get("type"),
        }
    except (urllib.error.HTTPError, urllib.error.URLError):
        pass
    try:
        data = fetch_json(f"{CROSSREF}/works/{urllib.parse.quote(doi)}?{urllib.parse.urlencode(params)}")
        it = data.get("message") or {}
        parts = ((it.get("issued") or {}).get("date-parts") or [[None]])[0]
        authors = it.get("author") or []
        return {
            "source": "crossref",
            "title": ((it.get("title") or [""])[0] or "").strip(),
            "year": parts[0] if parts else None,
            "authors": (" ".join(x for x in [authors[0].get("given"), authors[0].get("family")] if x).strip()
                        if authors else ""),
            "venue": ((it.get("container-title") or [""])[0] or "").strip(),
            "doi": doi,
            "cited_by": it.get("is-referenced-by-count"),
            "type": it.get("type"),
        }
    except (urllib.error.HTTPError, urllib.error.URLError):
        return None


def render(rows: list[dict]) -> str:
    if not rows:
        return "没有结果。换关键词，或放宽 --year-from / --year-to。"
    lines = []
    for i, r in enumerate(rows, 1):
        head = f"{i:>2}. {r['title']}"
        meta = "    " + " · ".join(str(x) for x in [
            r.get("year") or "?",
            r.get("authors") or "?",
            r.get("venue") or "",
            f"被引 {r['cited_by']}" if r.get("cited_by") is not None else "",
        ] if x)
        doi = f"    DOI: {r['doi']}" if r.get("doi") else "    DOI: （无，不能进正文引用）"
        lines += [head, meta, doi, ""]
    return "\n".join(lines).rstrip() + (
        "\n\n提示：这些只是候选。要引用时必须先写进 citations.csv 并跑 verify_refs.py。")


def main(argv: list[str] | None = None) -> int:
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description="Search OpenAlex / Crossref for paper metadata.")
    p.add_argument("query", nargs="?", help="search terms")
    p.add_argument("--limit", type=int, default=10, help="results (default 10, max 50)")
    p.add_argument("--source", choices=["openalex", "crossref", "auto"], default="auto")
    p.add_argument("--year-from", type=int)
    p.add_argument("--year-to", type=int)
    p.add_argument("--doi", help="look up one DOI instead of searching")
    p.add_argument("--mailto", help="your email for the polite API pool")
    p.add_argument("--json", action="store_true")
    p.add_argument("--csv", dest="csv_out", help="把候选写成 citations.csv（自动编号 id，verified 留空）")
    args = p.parse_args(argv)

    try:
        if args.doi:
            row = lookup_doi(args.doi, args.mailto)
            rows = [row] if row else []
            if not row:
                print(f"DOI 查不到元数据：{args.doi}", file=sys.stderr)
        elif not args.query:
            p.print_help()
            return 2
        elif args.source == "crossref":
            rows = search_crossref(args.query, args.limit, args.year_from, args.year_to, args.mailto)
        elif args.source == "openalex":
            rows = search_openalex(args.query, args.limit, args.year_from, args.year_to, args.mailto)
        else:
            try:
                rows = search_openalex(args.query, args.limit, args.year_from, args.year_to, args.mailto)
            except (urllib.error.HTTPError, urllib.error.URLError):
                rows = []
            if not rows:
                rows = search_crossref(args.query, args.limit, args.year_from, args.year_to, args.mailto)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        print(f"检索失败（网络）：{exc}", file=sys.stderr)
        return 2

    if args.csv_out:
        import csv as _csv
        cols = ["id", "authors", "year", "title", "venue", "doi_or_url",
                "page", "verified_by", "verified_on", "supports", "type"]
        type_map = {"journal-article": "J", "proceedings-article": "C",
                    "book-chapter": "C", "book": "M", "dissertation": "D",
                    "posted-content": "EB-OL", "report": "R", "standard": "S"}
        with io.open(args.csv_out, "w", encoding="utf-8-sig", newline="") as fh:
            writer = _csv.DictWriter(fh, fieldnames=cols)
            writer.writeheader()
            for i, r in enumerate(rows, 1):
                writer.writerow({
                    "id": str(i),
                    "authors": r.get("authors") or "",
                    "year": r.get("year") or "",
                    "title": r.get("title") or "",
                    "venue": r.get("venue") or "",
                    "doi_or_url": r.get("doi") or "",
                    "page": "", "verified_by": "", "verified_on": "",
                    "supports": "",
                    "type": type_map.get(str(r.get("type") or ""), ""),
                })
        print("已写 %s（%d 行，id 自动编号，verified 为空；下一步跑 "
              "verify_refs.py --csv %s）" % (args.csv_out, len(rows), args.csv_out))
        return 0
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    else:
        print(render(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
