# 文献获取：三阶段与可配置入口

文献工作分三层，能自动化的只有前两层的一部分：

| 阶段 | 工具 | 需要机构登录 | 能给什么 |
|---|---|---|---|
| 元数据 | `scripts/search_meta.py`（OpenAlex + Crossref） | 否 | 题名、作者、年份、刊名、DOI、被引 |
| 馆藏 | `scripts/opac_search.py`（你的 OPAC，需配置） | 否（多数 OPAC 公开可查） | 纸本馆藏、索书号、可借复本、学位论文 |
| 全文 | 机构数据库（CNKI / 万方 / WoS / IEEE / EBSCO） | 是 | PDF |

全文下载**不做自动化**：它需要你的账号、且几乎都受批量下载条款限制。自己的导出文件交给
`import_refs.py` 变成 `citations.csv`，这是唯一进得去正文的通道。

---

## 入口配置

本仓库不内置任何学校的端点。首次使用先跑 `references/institution-setup.md`，把入口写进
`institution.local.md`（不提交）：

| 键 | 用途 | 示例 |
|---|---|---|
| `OPAC_BASE` | 馆藏目录根地址 | `https://libopac.<学校域名>/opac` |
| `OPAC_RSS_PATH` | RSS 检索路径（汇文系统才有） | `search_rss.php` |
| `REMOTE_ACCESS` | 校外访问方式 | `vpn` / `webvpn` / `atrust` / `ezproxy` / `none` |
| `DATABASES` | 常用数据库 | `CNKI,万方,Web of Science` |

环境变量 `PAPERFLOW_OPAC_BASE` / `PAPERFLOW_OPAC_RSS` 优先于文件；命令行 `--base` 优先于两者。

没配置时 `opac_search.py` 会打印怎么配，并以退出码 2 结束——它不会退回某个学校的默认值。

---

## 常见 OPAC 系统怎么认

打开图书馆首页、搜一本书，看地址栏：

| 系统 | 特征 | 自动化 |
|---|---|---|
| 汇文 libopac | 路径含 `/opac/openlink.php`，另有 `search_rss.php` 返回 RSS | 本脚本支持 |
| 图创 / 超星 / 其他 | 路径含 `/opac/`、`/search`，结果为 JS 渲染 | 一般不支持，人工查 |
| Primo / Alma | 域名含 `primo`、`exlibrisgroup` | 有公开 API 但要机构 key |
| EBSCO Discovery | 域名含 `search.ebscohost.com` | 需机构认证 |

判断方法：把检索结果页的 HTML 保存下来，`grep` 书名。能 grep 到就是服务端渲染，可以写解析；
grep 不到就是 JS 渲染，别浪费时间。

---

## 校外访问的四种方式

| 方式 | 表现 | 注意 |
|---|---|---|
| 校园 VPN | 连上后整机走校内 IP | 命令行工具的流量也会走 VPN |
| WebVPN | 网址被改写成 `https://<xxx>-<域名>.webvpn...` 形式 | 有些资源不支持 WebVPN |
| aTrust（深信服） | 本机客户端按域名转发，系统代理设置不变 | 命令行拿不到校内 IP，浏览器内正常 |
| EZproxy | 网址前缀变成 `https://<域名>.libproxy...` | 通常能直接下载 PDF |

前三者都需要**人在浏览器里登录**。agent 不要代填账号密码，也不要去解验证码；需要时请用户
自己完成，然后把导出的 RIS/BibTeX 文件交给 `import_refs.py`。

---

## 命令

```text
# 元数据（无需配置，需要网络）
python <skill>/scripts/search_meta.py "network anomaly detection" --limit 5
python <skill>/scripts/search_meta.py --doi 10.1038/nature12373

# 馆藏（需 OPAC_BASE；汇文系统才有 RSS）
python <skill>/scripts/opac_search.py --title "机器学习" --limit 10
python <skill>/scripts/opac_search.py --isbn 9787302423287 --base https://libopac.example.edu.cn/opac

# 数据库导出 → 文献账
python <skill>/scripts/import_refs.py export.ris --out citations.csv
```

---

## 导出格式

优先 RIS：字段最全，各库都认。知网导出 EndNote（.enw）也能被解析；万方给 RIS；IEEE 给
BibTeX；Web of Science 给纯文本（另存为 RIS 更省事）。导出后**一律**跑
`verify_refs.py`——导入不等于核验。

---

## 失败对照

| 现象 | 原因 | 处理 |
|---|---|---|
| HTTP 418 / 420 / 429 | 反爬或频率限制 | 降低频率、隔几分钟再试；不要换 UA 硬刷 |
| 页面只有 `Loading...` | JS 渲染的壳 | 用浏览器打开，账号登录后人工检索 |
| 检索到 0 条但馆里有 | 字段选错（题名 vs 主题词）或繁体/简体差异 | 换 `--keyword`，或去掉书名号 |
| 有书目无馆藏 | 该馆没订，或只有电子版 | 查电子书库或馆际互借 |
| 导出无 DOI | 中文期刊多数如此 | `verify_refs.py` 会标 `MANUAL`，人工核对页码卷期 |
| doi.org 能解析但不返回 CSL-JSON | 中文注册机构不做内容协商 | 记为 `PARTIAL`，不是错录（见 `citation-contract.md`） |

---

## 合规红线

- 不代填账号密码、不代过验证码、不绕过访问控制。
- 不批量下载全文；一次检索取前 10–20 条即可。
- 不把数据库导出文件原样贴进交付物——先过 `citations.csv`，再到正文。
- 引用只认 `citations.csv` 里 `verified=y` 的行（见 `citation-contract.md`）。
