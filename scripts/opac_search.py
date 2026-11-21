#!/usr/bin/env python3
"""Search your library catalogue (opac) from the command line.

This is the *holdings* stage: it answers "does the library own this, where is
it shelved, is a copy available". It does NOT search journal databases
(CNKI / 万方 / IEEE / EBSCO) — those need your institutional login and cannot
be automated.

Usage:
  python scripts/opac_search.py --title "机器学习" --limit 10
  python scripts/opac_search.py --author "周志华"
  python scripts/opac_search.py --keyword "深度学习" --json
  python scripts/opac_search.py --isbn 9787302423287

Exit codes: 0 ok (including "0 results"), 2 network/usage error.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

CONFIG_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "institution.local.md"
)

BASE = ""
RSS = ""

MISSING_CONFIG = """\
还没有配置馆藏目录地址（OPAC base）。

本仓库不内置任何学校的端点。三选一：
  1) 跑 references/institution-setup.md 的首次配置，写入 institution.local.md
  2) 设环境变量：PAPERFLOW_OPAC_BASE=https://<你的 OPAC>/opac
  3) 临时传参：--base https://<你的 OPAC>/opac [--rss-path search_rss.php]

汇文系统（libopac）地址通常形如 https://libopac.<学校域名>/opac，RSS 在 search_rss.php；
其他系统（图创 / 超星 / Primo）通常没有 RSS，需要人工在浏览器查。"""


def read_config() -> dict:
    """key=value 行，来自本机的 institution.local.md（不提交）。"""
    out = {}
    if not os.path.isfile(CONFIG_FILE):
        return out
    with open(CONFIG_FILE, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            out[key.strip()] = val.strip()
    return out


def configure(cli_base=None, cli_rss=None) -> bool:
    """Resolve OPAC base: --base > env > institution.local.md. False if unset."""
    global BASE, RSS
    cfg = read_config()
    base = (cli_base or os.environ.get("PAPERFLOW_OPAC_BASE")
            or cfg.get("OPAC_BASE", "")).rstrip("/")
    if not base:
        return False
    BASE = base
    rss_path = (cli_rss or os.environ.get("PAPERFLOW_OPAC_RSS")
                or cfg.get("OPAC_RSS_PATH") or "search_rss.php").lstrip("/")
    RSS = f"{BASE}/{rss_path}"
    return True
UA = "plan-research-workflow/1.0 (catalogue holdings check)"

FIELD_LABELS = {
    "title": "题名",
    "author": "责任者",
    "keyword": "主题词",
    "isbn": "ISBN/ISSN",
    "callno": "索书号",
    "publisher": "出版社",
}


def fetch(url: str, timeout: int = 30) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/xml"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "replace")


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", text))).strip()


def search_rss(field: str, text: str, limit: int) -> tuple[list[dict], int]:
    params = {
        field: text,
        "doctype": "ALL",
        "lang_code": "ALL",
        "match_flag": "forward",
        "displaypg": "20",
        "showmode": "list",
        "orderby": "DESC",
        "sort": "CATA_DATE",
        "dept": "ALL",
    }
    xml = fetch(f"{RSS}?{urllib.parse.urlencode(params)}")
    items = re.findall(r"<item>(.*?)</item>", xml, re.S)
    rows = []
    for it in items:
        tm = re.search(r"<title>(.*?)</title>", it, re.S)
        dm = re.search(r"<description>(.*?)</description>", it, re.S)
        lm = re.search(r"<link>(.*?)</link>", it, re.S)
        title = _clean(tm.group(1)) if tm else ""
        title = re.sub(r"^\d+\s*[:：]\s*", "", title)
        desc = _clean(dm.group(1)) if dm else ""
        link = lm.group(1).strip() if lm else ""
        marc = re.search(r"marc_no=(\w+)", link)
        author = callno = pub = ""
        am = re.search(r"责任者[:：]\s*(.*?)(?=\s*索书号[:：]|$)", desc)
        cm = re.search(r"索书号[:：]\s*(.*?)(?=\s*出版信息[:：]|$)", desc)
        pm = re.search(r"出版信息[:：]\s*(.*)$", desc)
        if am:
            author = am.group(1).strip()
        if cm:
            callno = cm.group(1).strip()
        if pm:
            pub = pm.group(1).strip()
        rows.append({
            "title": title,
            "author": author,
            "publisher_year": pub,
            "callno": callno,
            "marc_no": marc.group(1) if marc else "",
            "url": f"{BASE}/item.php?marc_no={marc.group(1)}" if marc else "",
        })
    return rows[:limit], len(rows)


def search_html(field: str, text: str, limit: int) -> list[dict]:
    """Fallback: parse the HTML result list when RSS is unavailable."""
    params = {
        "strSearchType": field,
        "strText": text,
        "match_flag": "forward",
        "historycount": "1",
        "doctype": "ALL",
        "displaypg": "20",
        "sort": "CATA_DATE",
        "orderby": "desc",
        "showmode": "list",
        "dept": "ALL",
    }
    page = fetch(f"{BASE}/openlink.php?{urllib.parse.urlencode(params)}")
    rows = []
    for block in re.findall(r'<li class="book_list_info">(.*?)</li>', page, re.S):
        kind = re.search(r"<span>(.*?)</span>", block, re.S)
        link = re.search(r'href="item\.php\?marc_no=(\w+)[^"]*"\s*>(.*?)</a>', block, re.S)
        if not link:
            continue
        title = re.sub(r"^\d+\s*[.:：]\s*", "", _clean(link.group(2)))
        rest = _clean(re.sub(r"<h3>.*?</h3>", "", block, flags=re.S))
        callno = ""
        cm = re.search(r"([A-Z]{1,3}\d+(?:\.\d+)?/\d+)", rest)
        if cm:
            callno = cm.group(1)
        rows.append({
            "title": title,
            "author": "",
            "publisher_year": "",
            "callno": callno,
            "marc_no": link.group(1),
            "url": f"{BASE}/item.php?marc_no={link.group(1)}",
            "kind": _clean(kind.group(1)) if kind else "",
        })
        if len(rows) >= limit:
            break
    return rows


def render(rows: list[dict], total: int, field: str, text: str) -> str:
    if not rows:
        return (f"馆藏检索：{FIELD_LABELS.get(field, field)}={text} → 0 条。\n"
                "可能原因：词太窄、外文书写法不同，或该文献只有电子版（馆藏目录只收纸本与学位论文）。")
    head = f"馆藏检索：{FIELD_LABELS.get(field, field)}={text} → 共 {total} 条，显示 {len(rows)} 条\n"
    lines = [head]
    for i, r in enumerate(rows, 1):
        lines.append(f"{i:>2}. {r['title']}")
        bits = [x for x in [r.get("author"), r.get("publisher_year"), r.get("callno")] if x]
        if bits:
            lines.append("    " + " · ".join(bits))
        if r.get("url"):
            lines.append(f"    馆藏与借阅：{r['url']}")
        lines.append("")
    return "\n".join(lines).rstrip()


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description="Search library holdings (opac).")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--title")
    g.add_argument("--author")
    g.add_argument("--keyword")
    g.add_argument("--isbn")
    g.add_argument("--callno")
    g.add_argument("--publisher")
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--json", action="store_true")
    p.add_argument("--base", help="OPAC base, e.g. https://libopac.example.edu.cn/opac")
    p.add_argument("--rss-path", help="RSS 检索路径，默认 search_rss.php")
    args = p.parse_args(argv)

    if not configure(args.base, args.rss_path):
        print(MISSING_CONFIG, file=sys.stderr)
        return 2

    field, text = "", ""
    for name in FIELD_LABELS:
        val = getattr(args, name)
        if val:
            field, text = name, val
            break

    try:
        rows, total = search_rss(field, text, args.limit)
        if not rows and total == 0:
            rows = search_html(field, text, args.limit)
            total = len(rows)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        print(f"馆藏检索失败（网络）：{exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps({"field": field, "query": text, "total": total, "items": rows},
                         ensure_ascii=False, indent=2))
    else:
        print(render(rows, total, field, text))
    return 0


if __name__ == "__main__":
    sys.exit(main())
