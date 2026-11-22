# Changelog

## v1.1.3 — verify_refs 不再 fail-open（外部反馈修复）

来自一份第三方实测反馈（Windows + Python 3.14 + DSH 2.2）：`verify_refs.py` 在"一条都没核验"时返回退出码 0。

- **修复**：`--csv` 缺 `id` 列直接报错（exit 2）；只有表头、`--only` 未命中、所有行都被筛掉时同样 exit 2；空结果集不再走 `any([]) == False` 的放行分支。
- **新增**：`--assign-ids`（无 `id` 列时按行序编号并警告）、`--allow-unchecked`（`--offline` 下允许把 `UNCHECKED` 当通过），`--offline` 的未核验结果改为 exit 3。
- **新增**：`search_meta.py --csv`，把检索结果直接写成带 `id` 的 `citations.csv`，形成 search → verify 不断链。
- **修复**：ISBN 类标识（如 `ISBN 978-7-5107-1166-4`）被误判为 `UNREACHABLE`，现按 `MANUAL` 处理（图书不走 doi.org）。
- **修复**：9 个脚本的 stderr 之前未设 UTF-8，Windows PowerShell 下中文报错会乱码；现 stdout/stderr 统一 UTF-8。
- **文档**：`check.py`、`verify_refs.py` 的 `--help` 增加退出码说明；SKILL.md、citation-contract.md、README 补退出码表。
- **测试**：新增 `tests/test_verify_refs.py`（9 个用例，无需网络）。

## v1.1.2 — 中文原话能命中

- `SKILL.md` 的 `description` 加中文说法（"这个作业怎么写""论文从哪开始"…），技能是描述匹配，英文描述对中文输入不稳定。
- `QUICKSTART.md` 加「不用背技能名，说人话就行」对照表。

## v1.1.1 — QUICKSTART

- 新增 `QUICKSTART.md`：课程论文 / 实验报告 / 开题申报三段可直接复制的输入模板，外加"三样凑不齐怎么办"。
- `lint_docs.py` 纳入顶层 `*.md`，README 与 QUICKSTART 也进文档一致性检查。

## v1.1.0 — 去本机化

- 删掉东南大学图书馆的硬编码端点，改为 `institution.local.md` + 首次使用三问（`references/institution-setup.md`）。
- `opac_search.py` 未配置时 exit 2 并说明三种配置方式。
- `.gitattributes` 统一 LF，修掉 CRLF 造成的整篇 diff 噪声。

## v1.0.0 — 首个公开版

- 11 个确定性脚本（preflight / status / check / verify_refs / usage_report / export_docx / search_meta / opac_search / import_refs / lint_docs / _runtime）。
- execute / plan 两种模式，一次批准、一步一报；三本账（state.json、runlog.md、citations.csv）+ 三道门（preflight、check.py、usage_report）。
