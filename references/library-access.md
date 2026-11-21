# Literature Access: 东南大学图书馆与开放元数据

本文件规定"文献从哪来、哪些能自动、哪些必须人工"。它解决的是一件事：
**不让检索结果变成看起来可信、实际没核过的引用。**

## 0. 一句话原则

> 元数据走开放 API，馆藏走 OPAC，全文只能你自己登录取。
> 任何一步没做，就不能说"我检索过"。

## 1. 三条通道与边界

| 通道 | 工具 | 需要登录 | 能拿到 | 拿不到 |
|---|---|---|---|---|
| 元数据 | `scripts/search_meta.py`（OpenAlex / Crossref） | 否 | 题名、作者、年份、刊名/会议、DOI、被引数 | 全文、页码、卷期、中文库独有文献 |
| 馆藏 | `scripts/opac_search.py`（libopac 汇文系统） | 否 | 纸本馆藏、索书号、可借复本、东大学位论文 | 期刊论文全文、电子书正文 |
| 全文 | 图书馆门户 → CNKI / 万方 / Elsevier / IEEE / EBSCO | **是**（统一身份认证或校园网 IP） | PDF、页码、卷期 | 自动化批量抓取（不允许） |

**为什么全文不自动化**：这些库有验证码、IP/账号双认证和反爬（IEEE 实测直接返回 418）；
绕过它们违反数据库使用许可，也让流程在最关键的一步变得不可靠。流程只做到"给你正确入口 + 正确检索式"。

## 2. 入口（按可达性排序）

| 资源 | 入口 | 校外（aTrust） | 校内直连 |
|---|---|---|---|
| 图书馆主站 | https://lib.seu.edu.cn/ | 可访问（公开页） | 可访问 |
| 馆藏目录 OPAC | https://libopac.seu.edu.cn/opac/openlink.php | 可访问、免登录 | 可访问 |
| aTrust 校外访问入口 | https://lib-seu-edu-cn.atrust.seu.edu.cn/ | 需 aTrust 会话（JS 渲染，无法直接抓取） | 不需要 |
| 超星发现（发现系统） | https://ss.zhizhen.com/s?sw=关键词 | 需机构认证 | 校园网 IP 直接可用 |
| 中国知网 | https://www.cnki.net/ | 需机构认证 | 校园网 IP 直接可用 |
| 万方 | https://g.wanfangdata.com.cn/ | 需机构认证 | 校园网 IP 直接可用 |
| EBSCO 发现（EDS） | https://search.ebscohost.com/login.aspx?authtype=ip,guest&custid=s1397862&profile=eds&bquery= | 需机构认证 | 校园网 IP 直接可用 |
| IEEE Xplore | https://ieeexplore.ieee.org/ | 需机构认证（有反爬） | 校园网 IP 直接可用 |

`www.lib.seu.edu.cn` 的证书与域名不匹配（curl 报 `SEC_E_WRONG_PRINCIPAL`），
用 `lib.seu.edu.cn` 或 `http://www.lib.seu.edu.cn/`。

## 3. 元数据检索（可自动化）

```bash
python scripts/search_meta.py "network traffic anomaly detection" --limit 10
python scripts/search_meta.py "图神经网络 交通流预测" --limit 10 --year-from 2021
python scripts/search_meta.py --doi 10.1038/nature12373
python scripts/search_meta.py "topic" --source crossref --json
```

要点：

- **`--source auto` 先 OpenAlex 再 Crossref**；中文题名两边覆盖都不全，检索不到不等于不存在。
- 结果是**候选**，不是引用。要引用必须走第 5 节。
- OpenAlex 的中文作者名可能变成"名 姓"顺序（如"淼玉 周"），写进 CSV 前自己改。
- 用 `--mailto 你的邮箱` 进入开放 API 的 polite pool，避免被限流。
- 没有 DOI 的条目（常见于国内普刊）不能直接进正文，除非拿到可访问的稳定 URL。

## 4. 馆藏检索（可自动化）

```bash
python scripts/opac_search.py --title "机器学习" --limit 10
python scripts/opac_search.py --author "周志华"
python scripts/opac_search.py --keyword "交通安全"        # 可检索到东大学位论文
python scripts/opac_search.py --isbn 9787302423287
python scripts/opac_search.py --title "深度学习" --json
```

实测（2026-11）：题名"机器学习"458 条（中文图书 438 / 西文 17 / 学位论文 3）；
主题词"交通安全"能查到交通学院 2020 年学位论文，索书号形如 `21交通学院/D2020:22`。

- 馆藏目录**只收纸本与学位论文**，不收期刊论文和电子书正文。查不到期刊论文是正常的。
- 学位论文是本科阶段最实用的中文参考文献：同校、同方向、可馆内阅览。
- "馆藏与借阅"链接里的 `item.php?marc_no=...` 可看具体馆藏地与借阅状态。

## 5. 全文获取与导入（半自动：你导出，脚本入库）

1. 用上表入口登录（校外先连 aTrust），在数据库里检索同一个关键词。
2. 勾选需要的文献 → 导出题录，格式选 **RIS**（CNKI 选"参考文献/EndNote"，万方选 RIS，
   IEEE 选 BibTeX，Elsevier 选 RIS，EBSCO 选 RIS）。
3. 把导出文件丢进当前目录，然后：

```bash
python scripts/import_refs.py refs.ris --csv citations.csv --dry-run   # 先看会进什么
python scripts/import_refs.py refs.ris --csv citations.csv
```

4. `import_refs.py` 会：自动编号、去重（按 DOI 与标题+年份）、按 GB/T 7714 类型码标注
   `type`（J/M/C/D/R/S/P/N/EB-OL）、把 `verified_by` 留空——**它不替你核验**。
5. 逐条核验：

```bash
python scripts/verify_refs.py --csv citations.csv              # 全量
python scripts/verify_refs.py --csv citations.csv --only 3     # 单条
```

6. 核验 `OK` 后，才填 `verified_by`（写 `lead` 或你的名字）与 `verified_on`，
   并在 `supports` 里写这条文献支撑正文的**哪句话**。

## 6. 合规红线

- 不批量下载、不整刊抓取、不共享账号、不绕过验证码或付费墙。
- 下载只为阅读与引用，不二次分发 PDF。
- 检索式与题录可以自动化；**全文下载保持人工、按篇**。
- 数据库许可通常禁止"系统性下载"，违规会导致全校 IP 被封——这是实际发生过的后果。

## 7. 常见失败与处理

| 现象 | 原因 | 处理 |
|---|---|---|
| IEEE 返回 418 / CNKI 跳登录 | 反爬或未认证 | 连 aTrust / 校园网，人工在浏览器打开 |
| aTrust 页面只有 `Loading...` | 那是 JS 壳，不是站点内容 | 用浏览器打开并完成认证；不要用 curl |
| 馆藏 0 条 | 只有电子版，或外文写法不同 | 换 `--author` / `--isbn`；期刊论文本来就查不到 |
| DOI 查不到 | 中文普刊常无 DOI | 用可访问 URL（知网/万方详情页）+ 页码，verify 记 `MANUAL` |
| `verify_refs.py` 报 MISMATCH | 导出元数据与 DOI 登记不一致 | 以 DOI 登记为准，修 CSV；改不动的删掉 |
| OpenAlex 检索不到某篇中文论文 | 收录范围有限 | 用 `--source crossref` 再试，或直接在知网检索后导出 |

## 8. 与流程其他环节的接口

- 引用契约：`references/citation-contract.md`（`citations.csv` 的列定义与硬规则）
- 引用核验：`scripts/verify_refs.py`（DOI 解析 + 字段比对 + 退出码）
- 稿件自检：`scripts/check.py --citations-csv citations.csv`
- Word 交付：`scripts/export_docx.py --references-csv citations.csv`（顺序编码制渲染）
