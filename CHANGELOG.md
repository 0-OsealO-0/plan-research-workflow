# Changelog

## v1.1.5 — 换个 agent 也能用

别人问「这个 skill 在别的 agent 上能跑吗」。结构上能：`SKILL.md` 是标准 Agent Skills 格式，
脚本除 Word 导出外只用标准库；但实际上有四处会绊住人，这一版堵掉三处，第四处写进说明。

- **`preflight.py` 的根目录扩到别的 agent**：新增 `~/.claude/skills`、`~/.cursor/skills`、
  `~/.config/opencode/skill`（单数）与 `skills`（复数）、以及项目级 `<project>/.claude/skills`、
  `<project>/.cursor/skills`。此前只认 library/codex/dsh/agents，Cursor 用户会把装好的技能看成「全缺」。
- **安装不再绑死本机工具**：`references/skill-dependencies.md` 与 `README.md` 补了「只有 git / 只有文件夹」
  两条等价路径（`git clone` 后复制到对应 agent 目录），`skills-manager-cli` 降为其中一种便利方式。
- **没有 skill 工具的宿主**：执行循环第 4 步写明「直接读该技能的 SKILL.md 并照做，流程相同，只是加载机制不同」。
- **`python-docx` 前置依赖写进 SKILL.md**：`export_docx.py` 会在 `PAPERFLOW_PYTHON` / DSH 自带解释器下重执行，
  都没有时需要 `pip install python-docx`。
- **测试**：`tests/test_preflight_roots.py`（3 例：跨 agent 目录能被识别、默认根目录清单完整、
  `PAPERFLOW_SKILL_ROOTS` 可追加）。

仍未验证的是「在 Claude Code / Cursor 里真的跑通一遍」——本机只有 DSH 和 Codex 两条真实路径。

## v1.1.4 — 缺技能要说、要问、才装

用户提出的问题：搭档技能不在仓库里，安装时会不会告知、会不会在知情情况下帮装？此前的答案是「都不会」：
`skills install` 只拷文件，第一次 `preflight.py` 才列 `[missing]`，而那是给 agent 看的，用户可能只看到「已完成」。

- **新增** `references/skill-dependencies.json`：27 个搭档技能的作用、安装来源（有公开地址的才写）、缺失时的代价；`install` 为空 = 没有公开地址，不许 agent 猜 URL 去装。
- **新增** `references/skill-dependencies.md`：为什么依赖不打包、三类来源（公开仓库 / 本机库 / 作者提供）、正确的安装顺序、降级原则。
- **新增** `preflight.py --explain`：逐个缺失技能打印「作用 / 安装 / 缺失时」，并写明「先让用户确认，再 skill-inspector 扫描，然后 install + deploy」；JSON 输出的 `missing_skills` 也带上这三项。
- **新增** SKILL.md 规则 32 + First Actions 第 10 条：缺技能必须先列清单问用户，不许静默替代、不许静默安装；装完重跑 preflight 并报告新状态。
- **文档**：README、QUICKSTART 补「第一次跑会先问你」段落。
- **测试**：`tests/test_preflight_explain.py`（5 例：explain 三要素、同意规则、默认提示、manifest 覆盖全部默认技能、JSON 字段）。

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
