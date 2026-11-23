#!/usr/bin/env python3
"""Verify that citations in citations.csv point at the works they claim.

Each row with a DOI is resolved through doi.org content negotiation
(CSL-JSON), and the returned title, year, first author, venue, and page are
compared with the CSV. Rows with a plain URL are fetched and only their page
title is compared — enough to catch a dead or wrong link, not enough to prove
the entry.

This script proves reference existence and field agreement. It does not prove
that the work supports the sentence it is cited for; that stays manual.

Usage:
    python verify_refs.py [--csv citations.csv] [--timeout 20] [--delay 1.0]
                          [--only 3,5] [--json] [--out results.csv] [--strict]
                          [--offline]

Exit codes:
    0  every entry resolved and agreed (or has no identifier to resolve)
    1  at least one MISMATCH or UNREACHABLE entry (or PARTIAL with --strict)
    2  usage or file error
"""

import argparse
import csv
import io
import json
import re
import sys
import time
import urllib.error
import urllib.request

UA = "plan-research-workflow/1.0 (citation verification)"
DOI = re.compile(r"10\.\d{4,9}/[^\s,，;；]+")
URL = re.compile(r"https?://[^\s，。;；]+")
HTML_TITLE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)


def norm(text):
    text = (text or "").lower()
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[^\w\u4e00-\u9fff]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def title_matches(claimed, actual):
    a, b = norm(claimed), norm(actual)
    if not a or not b:
        return None
    if a in b or b in a:
        return True
    ta, tb = set(a.split()), set(b.split())
    if not ta or not tb:
        return False
    return len(ta & tb) / min(len(ta), len(tb)) >= 0.7


def year_of(payload):
    for key in ("issued", "published-print", "published-online", "created"):
        parts = (payload.get(key) or {}).get("date-parts") or []
        if parts and parts[0] and parts[0][0]:
            return str(parts[0][0])
    return ""


def family_names(payload):
    names = []
    for author in payload.get("author") or []:
        family = author.get("family") or author.get("name") or ""
        if family:
            names.append(norm(family))
    return names


def fetch_metadata(identifier, timeout):
    if DOI.search(identifier):
        doi = DOI.search(identifier).group(0).rstrip(".")
        url = "https://doi.org/" + doi
        accept = "application/vnd.citationstyles.csl+json"
    else:
        match = URL.search(identifier)
        if not match:
            return None, "no identifier"
        url = match.group(0)
        accept = "text/html"

    req = urllib.request.Request(
        url, headers={"Accept": accept, "User-Agent": UA}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read(400000)
            final = resp.geturl()
            ctype = resp.headers.get("Content-Type", "")
    except urllib.error.HTTPError as exc:
        return None, "HTTP %s" % exc.code
    except Exception as exc:  # network, DNS, TLS, timeout
        return None, "%s: %s" % (type(exc).__name__, exc)

    text = raw.decode("utf-8", "replace")
    if "json" in ctype or text.lstrip().startswith("{"):
        try:
            payload = json.loads(text)
        except ValueError:
            return None, "response was not valid JSON"
        return {"kind": "doi", "payload": payload, "final": final}, None
    title = HTML_TITLE.search(text)
    return {
        "kind": "url",
        "payload": {"title": title.group(1).strip() if title else ""},
        "final": final,
    }, None


def check_row(row, timeout):
    """Return (status, details list)."""
    claimed_title = row.get("title", "")
    claimed_year = (row.get("year", "") or "").strip()
    claimed_authors = row.get("authors", "") or ""
    claimed_venue = row.get("venue", "") or ""
    claimed_page = row.get("page", "") or ""
    identifier = (row.get("doi_or_url") or row.get("doi") or row.get("url") or "").strip()

    if identifier.upper().startswith("ISBN") or re.fullmatch(r"[0-9][0-9\-]{8,16}[0-9Xx]", identifier):
        if (row.get("venue") or "").strip() and (row.get("page") or "").strip():
            return "MANUAL", ["%s：图书按出版信息与页码人工核对，doi.org 不覆盖" % identifier]
        return "MANUAL", ["%s：需人工核对作者、出版者与页码" % identifier]

    if not identifier:
        if (row.get("venue") or "").strip() and (row.get("page") or "").strip():
            return "MANUAL", ["无 DOI/URL；专著/标准按出版信息与页码人工核对"]
        return "NO_ID", ["没有 DOI/URL，无法核验"]

    meta, err = fetch_metadata(identifier, timeout)
    if err:
        return "UNREACHABLE", [err]

    payload = meta["payload"]
    details = []
    bad = False

    if meta["kind"] == "url":
        actual_title = payload.get("title", "")
        if not actual_title:
            return "PARTIAL", ["页面可访问但取不到标题，需人工核对"]
        if title_matches(claimed_title, actual_title) is False:
            return "MISMATCH", ["页面标题与 CSV 题名不符：%s" % actual_title[:120]]
        return "OK", ["仅核对了页面可达与标题"]

    actual_title = payload.get("title") or ""
    if isinstance(actual_title, list):
        actual_title = actual_title[0] if actual_title else ""
    matched = title_matches(claimed_title, actual_title)
    if matched is False:
        bad = True
        details.append("题名不符：实际为「%s」" % actual_title[:160])

    actual_year = year_of(payload)
    if claimed_year and actual_year and claimed_year != actual_year:
        bad = True
        details.append("年份不符：CSV %s / DOI %s" % (claimed_year, actual_year))

    names = family_names(payload)
    if names and claimed_authors:
        first = names[0]
        if first not in norm(claimed_authors):
            bad = True
            details.append("第一作者不符：DOI 为「%s」" % first)

    venue = payload.get("container-title") or payload.get("publisher") or ""
    if isinstance(venue, list):
        venue = venue[0] if venue else ""
    if venue and claimed_venue and title_matches(claimed_venue, venue) is False:
        details.append("刊名/出版者不完全一致：DOI 为「%s」" % str(venue)[:100])

    page = payload.get("page") or ""
    if page and claimed_page and norm(page) != norm(claimed_page):
        details.append("页码不一致：CSV %s / DOI %s（格式差异可忽略）" % (claimed_page, page))

    if bad:
        return "MISMATCH", details
    if details:
        return "PARTIAL", details
    return "OK", details or ["题名、年份、作者一致"]


def load_rows(path, assign_ids=False):
    with io.open(path, encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        if not reader.fieldnames:
            raise ValueError("CSV 没有表头")
        fields = {name.strip().lower(): name for name in reader.fieldnames}
        has_id = "id" in fields
        if not has_id and not assign_ids:
            raise ValueError(
                "CSV 缺少必需的 id 列（用于在报告中定位每条引用）。"
                "请添加 id 列，或用 --assign-ids 自动编号。")
        rows, skipped = [], 0
        for raw in reader:
            rid = (raw.get(fields["id"], "") or "").strip() if has_id else ""
            if not rid and not has_id:
                rid = str(len(rows) + 1)
            if not rid:
                skipped += 1
                continue
            row = {key: (raw.get(fields[key], "") or "").strip() for key in fields}
            row["id"] = rid
            rows.append(row)
    seen_ids, dup_ids = set(), []
    for row in rows:
        if row["id"] in seen_ids:
            if row["id"] not in dup_ids:
                dup_ids.append(row["id"])
        else:
            seen_ids.add(row["id"])
    if dup_ids:
        shown = ", ".join(dup_ids[:6]) + (" 等" if len(dup_ids) > 6 else "")
        sys.stderr.write(
            "警告：CSV 中有 %d 个重复的 id（%s），报告里这些条目无法区分；"
            "建议给每行唯一的 id。\n" % (len(dup_ids), shown))
    if not has_id:
        sys.stderr.write("警告：CSV 缺少 id 列，已按行序自动编号 1..%d；"
                         "建议在源表中显式提供 id。\n" % len(rows))
    if skipped:
        sys.stderr.write("警告：%d 行因缺少 id 被跳过。\n" % skipped)
    return rows


def main():
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")

    ap = argparse.ArgumentParser(
        description="Verify that each citation in citations.csv really exists "
                    "and that its metadata matches the DOI record.",
        epilog="退出码：0 全部通过；1 有核验失败（MISMATCH/UNREACHABLE/NO_ID，"
               "--strict 时含 PARTIAL）；2 输入错误或没有任何行被核验；"
               "3 --offline 下存在未联网核验的条目（需 --allow-unchecked 才放行）。",
    )
    ap.add_argument("--csv", default="citations.csv")
    ap.add_argument("--timeout", type=float, default=20.0)
    ap.add_argument("--delay", type=float, default=1.0)
    ap.add_argument("--only", default="")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out", default="")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--assign-ids", action="store_true",
                    help="CSV 没有 id 列时按行序自动编号（会向 stderr 打印警告）")
    ap.add_argument("--allow-unchecked", action="store_true",
                    help="--offline 下允许把 UNCHECKED 当通过（默认 exit 3）")
    args = ap.parse_args()

    try:
        rows = load_rows(args.csv, args.assign_ids)
    except (OSError, ValueError) as exc:
        print("ERROR: %s" % exc, file=sys.stderr)
        return 2

    only = {x.strip() for x in args.only.split(",") if x.strip()}
    results = []
    for index, row in enumerate(rows):
        rid = row.get("id", "")
        if only and rid not in only:
            continue
        if args.offline:
            status, details = "UNCHECKED", ["--offline：未联网核验"]
        else:
            if index and args.delay:
                time.sleep(args.delay)
            status, details = check_row(row, args.timeout)
        results.append(
            {"id": rid, "status": status, "details": details,
             "title": row.get("title", ""), "doi_or_url": row.get("doi_or_url", "")}
        )

    if args.out:
        with io.open(args.out, "w", encoding="utf-8", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(["id", "status", "details", "title", "doi_or_url"])
            for entry in results:
                writer.writerow([entry["id"], entry["status"], " | ".join(entry["details"]),
                                 entry["title"], entry["doi_or_url"]])

    if not results:
        msg = "没有任何行被核验"
        if only:
            msg += "（--only %s 未命中任何 id）" % args.only
        else:
            msg += "（CSV 里没有可用行）"
        print("ERROR: " + msg, file=sys.stderr)
        return 2

    order = {"MISMATCH": 0, "UNREACHABLE": 1, "NO_ID": 2, "PARTIAL": 3, "MANUAL": 4, "OK": 5, "UNCHECKED": 6}
    results.sort(key=lambda entry: (order.get(entry["status"], 9), entry["id"]))

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print("verify_refs.py — %s  (%d entries)" % (args.csv, len(results)))
        for entry in results:
            print("[%s] %s" % (entry["status"], entry["id"]))
            for detail in entry["details"]:
                print("    - %s" % detail)
        counts = {}
        for entry in results:
            counts[entry["status"]] = counts.get(entry["status"], 0) + 1
        print("SUMMARY: " + ", ".join("%s=%d" % (k, counts[k]) for k in sorted(counts)))

    failing = {"MISMATCH", "UNREACHABLE", "NO_ID"}
    if args.strict:
        failing.add("PARTIAL")
    if any(entry["status"] in failing for entry in results):
        return 1
    unchecked = [e for e in results if e["status"] == "UNCHECKED"]
    if unchecked and not args.allow_unchecked:
        print("ERROR: %d 条未联网核验（--offline）。确认接受后再加 --allow-unchecked。"
              % len(unchecked), file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
