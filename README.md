# plan-research-workflow

一个把「我要写论文 / 做研究 / 交课程报告」变成**可执行步骤**的 agent skill。
它不替你写，它安排谁写、按什么顺序写、每一步的交付物和门禁是什么，然后一步步跑给你看。

A meta-skill that turns a paper or research request into an approved, executable
plan: which installed skill does which step, what artifact each step must
produce, and which machine check gates it.

---

## 为什么需要它

大多数「AI 写论文」的失败不是文笔问题，而是顺序问题：先写、再补文献、最后才发现论证
站不住。这个 skill 把顺序固定下来：

1. **先诊断**（这是什么类型的交付、谁评、有没有自己的数据）
2. **先建账**（`citations.csv` 文献账、`术语表.md` 术语表、`主张账本.md` 主张账）
3. **先红队**（提纲阶段就攻击主张，而不是写完再挑错）
4. **再动笔**，写作约束（叙事立场、禁用词、数字必须指回文献账）进 handoff，不留给事后清洗
5. **每步有门**：`check.py` 0 CRITICAL、`verify_refs.py` 无双绿以外状态、`usage_report.py` 全跑过

## 两种模式

| 模式 | 触发 | 行为 |
|---|---|---|
| `execute`（默认） | 正常请求 | 诊断 → 出步骤计划 → **一次批准** → 一步一条消息地跑，停只在：要数据、要决策、门没过 |
| `plan` | 「只给计划」「别改文件」「先别执行」 | 只读：给链条、给 handoff 字段，不写任何文件 |

说一句「只给计划」随时冻结为 plan 模式；已产出的文件不动。

## 闭环

```
诊断 → preflight（技能在不在） → 步骤计划 → 批准
     → 每步：跑 skill → 写产物 → status.py 记账 → check.py 自检
     → 决策点：≤3 个选项 + 成本/收益/风险 + 推荐
     → 交付前三门：preflight 全绿 / check 0 CRITICAL / usage_report exit 0
```

## 脚本

11 个脚本，标准库优先，全部可单独跑（`python scripts/<name>.py --help`）：

| 脚本 | 作用 | 需要 |
|---|---|---|
| `preflight.py` | 检查这条链要用的 skill 是否真的装了 | — |
| `status.py` | 项目状态机：init/start/done/fail/decide/note/backup/show，写 `paperflow/state.json` + 只追加的 `runlog.md` | — |
| `check.py` | 确定性的稿子体检：代码围栏、占位符、引用与文献表对齐、图表标题、禁用自我削弱措辞、语体、章节完整性、字数；也读 `.docx` | — |
| `verify_refs.py` | 用 doi.org 的 CSL-JSON 逐条核 DOI、题名、年份、作者、页码 | 网络 |
| `usage_report.py` | 交付前的技能账本：哪些跑了、哪些没跑、各自挡住什么 | — |
| `export_docx.py` | Markdown → 带模板样式的 `.docx`（保留页面设置、标题阶梯、页码域、参考文献悬挂缩进） | `python-docx` |
| `search_meta.py` | 元数据检索（OpenAlex + Crossref 兜底），拿到可核验的 DOI | 网络 |
| `opac_search.py` | 图书馆 OPAC 馆藏检索（汇文系统 RSS 接口） | 网络 |
| `import_refs.py` | RIS / BibTeX / CSL-JSON → `citations.csv` | — |
| `lint_docs.py` | 检查本 skill 自己的文档一致性（围栏配对、规则编号连续、playbook 完整） | — |
| `_runtime.py` | 公共运行时：缺 `python-docx` 时自动用 DSH 自带解释器重跑；可用 `PAPERFLOW_PYTHON` 指定解释器 | — |

## 快速开始

```text
# 1) 让 skill 出计划（execute 模式，会先要一次批准）
用 plan-research-workflow 帮我做「低空经济 eVTOL 创新设计」的通选课期末报告，
2000–4000 字，至少两张概念图。

# 2) 项目里初始化状态
python <skill>/scripts/status.py init --type course --title "…" --scenario "…"

# 3) 每一步之后
python <skill>/scripts/check.py draft.md --type course --citations-csv citations.csv

# 4) 交付前
python <skill>/scripts/preflight.py
python <skill>/scripts/usage_report.py --root .
```

## 安装

DeepSeek Harness（skills-manager）：

```text
skills-manager-cli skills install https://github.com/0-OsealO-0/plan-research-workflow
skills-manager-cli skills deploy plan-research-workflow --agent deepseek_harness
```

其他 agent：把整个目录放进它的 skills 目录即可（`SKILL.md` + `references/` + `scripts/`）。

## 依赖与边界

- Python 3.9+；`export_docx.py` 需要 `python-docx`（缺失时会尝试 DSH 自带运行时，也可 `pip install python-docx`）。
- `search_meta.py` / `verify_refs.py` / `opac_search.py` 需要网络。
- **它不自己写论文**：写作、润色、评审、绘图交给被编排的其他 skill（`paper-writer`、`paper-polish`、`anti-defensive-writing`、`lieflat-less-ai-tone`、`grilling`、`academic-paper-reviewer`、`figure-designer`、`matplotlib` 等）。没装的那些，`preflight.py` 会报出来，而不是假装跑过。
- 不内置任何学校的端点：首次使用按 `references/institution-setup.md` 填一次机构档案（学校、院系、OPAC 地址、校外访问方式、常用数据库），写进不提交的 `institution.local.md`；没配时馆藏检查降级为人工，元数据检索不受影响。
- 中文优先，GB/T 7714-2015 是默认参考文献格式。

## 目录

```
SKILL.md                      技能主文件：模式、路由、规则、门禁
references/
  execution-protocol.md       执行循环、决策点、报告格式、记账
  workflow-playbooks.md       10 条场景链路（技术论文 / benchmark / 综述 / 课程报告 / 实验报告 / 申报书 / rebuttal…）
  routing-checklist.md        路由误判的 10 行对照表 + 改判协议
  skill-catalog.md            本机 skill 清单与降级顺序
  prompt-library.md           handoff 模板（写作、红队、统计、导出 Word…）
  citation-contract.md        citations.csv 契约与核验纪律
  gbt7714.md                  GB/T 7714-2015 条目规则
  library-access.md           文献获取渠道（检索 → 馆藏 → 全文）
  student-roadmap.md          大一到大四的科研能力路线
  example-course-report.md    一份完整的应答样例
scripts/                      11 个可执行检查与工具
agents/openai.yaml            agent 清单
```

## 许可

MIT，见 [LICENSE](LICENSE)。
