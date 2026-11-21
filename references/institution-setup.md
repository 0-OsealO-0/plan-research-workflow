# 首次使用：机构与文献入口

这个 skill 不内置任何学校的信息。第一次用的时候，先花一分钟把「你是谁、你在哪个库」记下来，
之后所有会话直接复用，不再问。

档案写在**不提交**的本地文件里：

```
institution.local.md          # skill 目录下，已在 .gitignore
```

也可以写到项目里 `paperflow/institution.md`（同样不进仓库）。两处都读到就合并，skill 目录优先。

---

## 要问的三件事（只问一次）

**1. 学校和院系** — 决定参考文献格式、课程论文模板、学分/毕业要求的口径。

```text
你在哪所学校、哪个院系？（例如：XX 大学 XX 学院）
```

**2. 学科方向** — 决定评审范式（工程/实验 vs 人文/设计）、常用数据库、图的类型。

```text
主要方向是？（例如：交通运输工程 / 设计学 / 公共管理）
```

**3. 文献入口** — 决定 `opac_search.py` 能不能用、检索往哪儿走。

```text
你们图书馆的馆藏目录（OPAC）网址是什么？
校外访问用哪种方式（校园 VPN / WebVPN / aTrust / EZproxy / 没有）？
常用的数据库是哪几个（知网、万方、Web of Science、IEEE、EBSCO…）？
```

如果对方不知道 OPAC 网址，就让他打开图书馆主页、随便搜一本书，把地址栏里带
`opac` 或 `search` 的那一段发过来。找不到就留空，馆藏检查降级为人工。

---

## 写进档案的格式

`institution.local.md` 是 `key=value`，一行一个。脚本只读它需要的键，其余当注释性记录。

```text
# 机构档案（本机，不提交）
INSTITUTION=XX 大学
DEPARTMENT=XX 学院
DISCIPLINE=XX 学科
DEGREE=本科
CITATION_STYLE=GB/T 7714-2015
# 馆藏目录。汇文系统形如 https://libopac.<域名>/opac；不知道就留空
OPAC_BASE=https://libopac.example.edu.cn/opac
OPAC_RSS_PATH=search_rss.php
# 校外访问方式：vpn / webvpn / atrust / ezproxy / none
REMOTE_ACCESS=webvpn
# 常用数据库，逗号分隔
DATABASES=CNKI,万方,Web of Science
# 课程论文模板路径（可选）
TEMPLATE=paperflow/模板_课程论文.docx
```

对应的环境变量优先于文件：`PAPERFLOW_OPAC_BASE`、`PAPERFLOW_OPAC_RSS`。

---

## 没有 OPAC 或不想填学校时

完全可以不填。此时：

- 文献检索仍可用 `search_meta.py`（OpenAlex + Crossref，不需要机构）
- 馆藏检查改人工：把书名/ISBN 丢给用户在图书馆页面搜
- 参考文献格式仍按 `references/gbt7714.md`
- 汇报里不要出现「贵校图书馆如何如何」，只写「按你的馆藏/数据库查找」

**不要**把学校名当成默认值写进任何交付物。用户没说的机构信息，宁可问一次，也不要猜。

---

## 已配置后

后续会话第一步读这两个文件（存在才读），然后按 `SKILL.md` 的 `execute` 模式继续。
用户换了学校、或某个数据库换了入口，就改这三个键，不用重新走一遍问卷。
