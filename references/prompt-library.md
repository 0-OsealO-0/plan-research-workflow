# Prompt and Handoff Library

In `execute` mode these entries are handoff specifications: the orchestrator
loads the skill and passes these fields as parameters, so nobody copies text.
Print them for the user only in `plan` mode, replacing the bracketed fields.

## Discovery

### `deep-research`

```text
用 deep-research 技能，围绕“[主题]”做完整研究。

目标：先冻结 2 到 3 个具体研究问题，再检索、核验、分类综合和交叉对比。
学科范围：[学科]
目标用途：[课程报告 / 论文选题 / 系统综述 / 项目申请]
必须使用的材料：[文件或目录]
可用数据库或来源：[数据库]
输出格式：[Markdown / APA 7 / IEEE / 其他]
输出语言：[中文 / 英文]
限制条件：[时间范围、地域、方法、必须包含或排除的内容]

请给出研究问题、检索策略、证据矩阵、主要争议、研究空白和下一步建议。
所有引用都要逐条核验，不得编造。
```

## Idea Evaluation

### `idea-evaluator`

```text
用 idea-evaluator 技能评估下面的研究 Idea。

Idea：[完整描述]
目标会议或期刊：[名称]
核心方法：[方法]
预期贡献：[贡献]
数据：[已有或计划获取的数据]
算力：[可用算力]
团队：[团队组成]
每周有效时间：[小时]
计划周期：[周数或月份]

请先做致命缺陷审计，再做生命周期、能力匹配、五维评分、范式潜力、
可行性和完整性检查。
按 CRITICAL / MAJOR / MINOR 分级，并给出 Strong Accept、
Accept with Revisions 或 Reject and Pivot 的结论。
```

## Paper Planning

### `tech-paper-template`

```text
用 tech-paper-template 技能，为我的技术论文搭建完整逻辑骨架。

研究问题：[问题]
核心 Idea：[Idea]
已有方法局限：[限制]
关键技术挑战：[挑战]
拟采用模块：[模块]
预期贡献：[贡献]
已有证据：[证据]
目标会议或期刊：[名称]

请对齐 Background、Limitations、Key Idea、Challenges、Modules
和 Contributions，并执行挑战、模块、贡献三路一致性检查。
```

### `benchmark-paper-template`

```text
用 benchmark-paper-template 技能，帮我规划或检查 Benchmark 论文。

当前阶段：[Gap / Design / Construction / Experiments / Writing / Checklist]
研究空白：[Gap]
目标评估能力：[能力或维度]
数据来源：[来源]
构建流程：[流程]
评估指标：[指标]
当前实验结果：[结果]
目标会议或期刊：[名称]

先判断我处于六阶段中的哪一步，再检查五支柱完整性，
输出 Introduction 逻辑链、Section 2 到 7 骨架和下一步动作。
```

## Drafting

### `anti-defensive-writing`

```text
用 anti-defensive-writing 技能重构下面这段论文文字（或这一节）。

语言：[中文 / 英文]
论文类型：[技术论文 / 评测论文 / 课程报告 / 综述]
目标会议或期刊：[名称]
篇幅限制：[页数 / 字数]
我真正占优的地方：[新能力 / 新机制 / 场景 / 成本 / 合理权衡，具体到能被数据支撑]
支撑它的结果：[结果名 + 数字]
不能改动的内容：[数字、引用、方法、实验设置]
必须保留的负面结果：[哪些结果不能删，因为它们是核心主张的一部分]

要求：
- 先判断主线和最强优势，再动笔；
- 不写"我们先做了 A 又试了 B"的过程叙事；
- 删掉自我削弱表达（遗憾的是 / 仅 / 效果有限 / 仍明显落后）；
- 不占优的维度不作为主战场，改选能体现价值的评价口径；
- 每个实验说明它承担哪种论证职责；
- 摘要前五句必须出现问题和贡献；
- 结论只强化记忆点，不新增自我否定；
- 不新增数据、引用或结论，不修改任何数字；
- 输出改后文字，另附改动清单（哪里压缩、哪里重排、为什么）。

原文：
[粘贴正文]
```

如果只是语法、语气或翻译问题，用 `paper-polish`；如果核心主张本身站不住，
先走 `pre-submission-reviewer` 或 `idea-evaluator`，不要用叙事重构掩盖证据问题。

### `intro-drafter`

```text
用 intro-drafter 技能，根据下面的结构写 Introduction。

论文定位：[Technique / New Problem / New Setting]
研究问题：[问题]
Running Example：[真实案例或明确说明暂无]
现有方法局限：[限制]
核心挑战：[挑战]
方法总览：[方案]
贡献：[贡献]
目标会议或期刊：[名称]
引用格式：[IEEE / ACM / APA / 其他]
输出语言：[英文 / 中文]

请输出六段式 Introduction 正文和 References。
引用必须经过真实检索核验，不得编造 Running Example 或文献。
如果 Running Example 缺失，请使用抽象背景并在尾注提醒我补充。
```

### `paper-writer`

```text
用 paper-writer 技能，写 [章节名称]。

目标会议或期刊：[名称]
论文类型：[论文类型]
输出语言：[英文 / 中文]
字数或篇幅：[限制]

写作约束（写的时候就生效，不要留到事后清洗）：
- 主线一句话：[这件事在论证什么]
- 主张边界：[只主张到哪一步；超出范围的说法不要写]
- 禁用自我削弱表达：[遗憾的是 / 仅 / 效果有限 / 仍明显落后 / 存在严重不足]
- 禁用翻案腔：[不是…而是… / 并非…而是… / 不在于…而在于…]
- 不用冒号提示语（核心是：/ 原因如下：/ 一句话总结：），不用序数词当小标题
- 正文每个数字都要能指回 `citations.csv` 的编号

可用材料：
1. [文件路径或内容]
2. [实验结果]
3. [方法笔记]
4. [图表]
5. [已核验引用]

写作要求：
- 每个事实性声明必须来自我提供的材料或经过检索核验的文献。
- 不得编造数据、机制、案例、引用、数字或占位符。
- 不得使用模型记忆补全缺失事实。
- 如果证据不足，请检索、改写或删除，并在交付说明中列出缺口。

输出：[正文] + [References] + [证据缺口说明]。
```

如果初稿写完才想起去 AI 味和防线，不要只补一遍 `lieflat-less-ai-tone`：按
SKILL.md 规则 29，把上面这组约束挂回 handoff 重写该步，清洗只处理残余。

### `academic-paper`

```text
用 academic-paper 技能，以 [full / plan / outline / revision /
revision-coach / abstract / lit-review / format-convert /
citation-check / disclosure / rebuttal-audit] 模式处理我的论文。

当前材料：[文件路径]
目标期刊或会议：[名称]
论文类型：[类型]
输出语言：[语言]
字数或页数：[限制]
引用格式：[格式]
输出格式：[LaTeX / DOCX / PDF / Markdown]
学生或作者信息：[信息]
必须保留的内容：[内容]
不能修改的内容：[内容]

请先检查当前阶段和缺失信息，再执行该模式。
所有引用、格式和事实必须可核验，不得编造。
```

### `research-paper-writing`

```text
用 research-paper-writing 技能，优化我的论文 [章节列表]。

目标会议或期刊：[名称]
论文领域：[ML / CV / NLP / 其他]
现有草稿：[文件路径或正文]
实验结果：[表格或文件]
主要主张：[主张]
不能修改的内容：[内容]

请：
1. 先给出 3 到 7 条小节提纲；
2. 按一段一个中心意思改写；
3. 标明每段角色；
4. 检查术语一致性、章节流和 Claim-Evidence 对齐；
5. 输出 Claim | Evidence | Status 对照表；
6. 给出投稿前自审清单。
```

## Figures

### `figure-designer`

```text
用 figure-designer 技能，为我设计 [Figure 1 / Solution Overview /
Experimental Results]。

论文主题：[主题]
这张图必须说明：[核心信息]
相关方法或实验：[材料]
目标会议或期刊：[名称]
可用工具：[PPT / TikZ / Inkscape / Draw.io / Python / 其他]
画布和版式限制：[限制]

请给出布局、标注、配色、图表类型、工具选择和常见反例，
最后执行一次图表质量检查。
```

### `drawio-reconstruction`

```text
用 drawio-reconstruction 技能，把 [参考图路径或目录] 重建为
可编辑的 .drawio 文件。

输出目录：[路径]
是否需要 PNG 预览：[是 / 否]
是否需要逐图视觉审计：[是 / 否]
文字和结构要求：[必须保持可编辑的内容]
复杂图标处理：[优先矢量 / 允许透明 PNG]

请保留文字和结构，对复杂视觉使用合适的保真方案，
输出 .drawio、PNG 预览和审计记录。
```

## 术语表（见 `语法`/`术语`）

`status.py init` 已生成 `术语表.md`；动笔前把它填完，不要留示例行。

```text
用途：写作前定义术语，改稿时按表校对。
术语（固定说法）：<一句话定义>；禁用近义词：<容易混用的词，逗号分隔>
术语（固定说法）：<一句话定义>；禁用近义词：<...>
硬规则：正文、表、图注、图内文字只用「术语」列的说法；禁用词只列真正会混用的，
列太多会让 check.py 在引用标题里误报——误报时删词条，不改正文。
```

## 主张与证据账本（claims ledger）

和 `citations.csv` 分工不同：`citations.csv` 管"这条文献本身真不真"，账本管"这句话靠什么撑着"。
写初稿前建表，红队审查时逐行攻击，交稿前每行都必须有归属。

模板：

| # | 主张（一句话，尽量可被反驳） | 支撑类型 | 证据位置 | 反例风险 | 处置 |
|---|---|---|---|---|---|
| C1 | 无人客舱的核心问题从"信息不足"转为"身体缺席" | 文献 + 推导 | [15][16][22] §2 | 已有研究可能已覆盖情绪层 | 收窄为"现有研究集中在可用层" |
| C2 | 环境节律可以在不显示数字的情况下传达飞行阶段 | 设计假定 | §4–§5 走查 | 无用户数据，不可证伪 | 标为待验证命题 |
| C3 | 客舱照明 200 lx 上限是合适的 | 行业惯例 | 待补 | 未给标准来源 | 加依据或降级为假定 |

支撑类型只允许五档，写错比写少更危险：

- `标准`：国标/行标/适航文件，给编号与条款；
- `文献`：给编号（必须已进 `citations.csv` 且 `verified_by` 非空）；
- `推导`：从前两者或方案内部约束推出来，要写出推导链；
- `惯例`：行业通行做法，说不出出处就降级为假定；
- `假定`：设计设定，必须写"待验证"，且不能拿它去反驳别人的实测结论。

三条硬规则：

1. 一行的"支撑类型"若是 `假定`，"证据位置"就不能填文献编号——那是伪造证据。
2. 红队（`grilling`）攻击的对象是这张表，不是行文。表里没有的主张，正文里不该有。
3. 交稿前扫一遍"反例风险"列：任何一条写着"不可证伪"的主张，要么补一个可检验命题，要么降级成设计说明。

## Data and Statistics

### `statistical-analysis`

```text
用 statistical-analysis 技能分析这批数据，并给出可直接写进报告的结果段落。

研究问题：[问题]
数据情况：[样本量、分组、变量、是否配对、缺失情况；或数据文件路径]
设计：[实验/问卷/观察，分组方式，随机化情况]
想支持的结论：[结论]
报告要求：[课程/期刊要求，显著性水平，是否要效应量和置信区间]

请先判断设计是否支持这个检验，检查前提假设；
假设不满足时给出替代方案，不要直接跑一个 t 检验。
最后给：检验选择理由、假设检查、结果表、效应量、一句话结论和局限性。
```

### `exploratory-data-analysis`

```text
用 exploratory-data-analysis 技能，对 [数据文件路径] 做一次有边界的探索性分析。

我关心的问题：[问题]
数据来源和采集方式：[来源]
已知的坑：[缺失、重复、单位不一致、时间泄漏等]

请给出：行列概览、类型与缺失、分布与异常值、
可能的数据泄漏或分组错误、这张表能回答和不能回答的问题。
不要清洗数据，不要建模，只做诊断。
```

## Language and Presentation

### `paper-polish`

```text
用 paper-polish 技能润色下面这段论文文字。

目标语言：[英文 / 中文]
目标场景：[期刊 / 会议 / 课程报告]
必须保留的术语：[术语]
不能改变的结论：[结论]
不能新增的内容：[限制]

要求：
- 保留作者原意；
- 修正语法、语序、逻辑连接和学术语气；
- 修正明显的模板化或机械语气；
- 让措辞强度不超过证据强度；
- 任何可能改变科学含义的修改都单独列出，等待我确认。

原文：
[粘贴正文]
```

如果任务只是在内容定稿后按明确规则去除 AI 写作痕迹，改用
`lieflat-less-ai-tone`，不要用本 prompt 做通篇重写。

### `lieflat-less-ai-tone`

```text
用 lieflat-less-ai-tone 技能处理这份已经完成内容与引用的文稿。

原文件：[Markdown / Word / 文本路径]
输出文件：[路径]
目标语体：[学术论文 / 课程报告 / 新闻 / 公文 / 其他]
语言：[中文 / 英文]
现有风格参考：[路径或明确说明没有]
必须保持不动的内容：[结构、标题、结论、引文、数字、引用、脚注、术语等]

要求：
- 只处理该 skill 明确列出的改写规则；
- 未命中规则的文字逐字保留；
- 不改变标题层级、章节顺序、段落数量和顺序、观点、证据、因果、限定词与引用；
- 不新增事实、数字、案例、来源或作者信息；
- 不把它当作通用润色、扩写、缩写或结构重写；
- 如果文稿仍有逻辑、证据或引用问题，先停止并指出，不要继续去 AI 味；
- 完成后给出代表性前后对比，并说明哪些内容保持不变。
```

## Review

### `academic-paper-reviewer`

```text
用 academic-paper-reviewer 技能，以 [full review / re-review /
quick assessment / methodology focus / Socratic guided] 模式审阅论文。

论文文件：[路径]
目标期刊或会议：[名称]
学科和论文类型：[学科]
当前阶段：[首次投稿 / 修订稿 / 复审]
我最担心的问题：[问题]
输出语言：[语言]

请生成独立审稿意见、编辑决定和修改路线图。
区分必须修复、建议修复和可忽略问题，不得假设论文中存在未提供的证据。
```

### `pre-submission-reviewer`

```text
用 pre-submission-reviewer 技能，在投稿前检查我的论文。

论文文件：[路径]
目标会议或期刊：[名称]
截止时间：[时间]
格式模板：[LaTeX 模板或要求]
图源文件：[路径]

请检查：
1. 宏观逻辑；
2. 写作细节；
3. 英文语法；
4. LaTeX 排版；
5. 图表质量。

按 CRITICAL / MAJOR / MINOR 排序，并单独列出 72 小时内必须完成的修复。
```

## Rebuttal and Revision

### `rebuttal-guidance`

```text
用 rebuttal-guidance 技能，根据下面的审稿意见设计回应策略。

论文摘要：[摘要]
目标会议或期刊：[名称]
审稿意见：
[粘贴 R1、R2、R3 的完整意见]

可新增的实验或证据：[证据]
不能完成的要求：[限制]
字数或时间限制：[限制]

请逐条分类 concern，区分需要补实验、补解释、承认局限和反驳的问题，
并给出语气、证据指针和回应结构。不要直接伪造 rebuttal 正文。
```

### `academic-paper` for Rebuttal

```text
用 academic-paper 技能，以 revision、revision-coach 或 rebuttal-audit
模式检查我的审稿回复。

原论文：[路径]
审稿意见：[路径或正文]
当前回复草稿：[路径或正文]
目标会议或期刊：[名称]
字数限制：[限制]

请检查：
1. 是否逐条回应；
2. 是否区分新证据和解释；
3. 是否与修订稿一致；
4. 是否存在过度承诺或攻击性语气；
5. 是否遗漏审稿人真正关心的问题。

输出修改路线、逐条覆盖检查和最终回复建议。
```

## Format, Proposal, and Integrity

### 实验报告（Lab Report）

```text
用 paper-writer 技能写一份实验报告正文，按 IMRaD 组织。

课程与实验名称：[名称]
实验目的与指导书要求：[要求]
原始数据或数据文件：[数据]
实验设计与操作步骤：[步骤]
不确定度来源：[仪器精度、重复测量、环境]
本课程的报告模板：[模板要求，若无则用通用 IMRaD]

统计与作图请先用 statistical-analysis 和 uncertainty-and-units 处理，
再用 figure-designer 或 matplotlib 出图。
要求：方法与结果分离；误差只写来源与量级，不写“由于时间不足”；
结论只覆盖被测对象和测量范围；引用只用真实读过的文献。
```

### 开题 / 大创 / SRTP 申报书

```text
用 academic-paper 的 plan 或 outline 模式，帮我写 [开题报告 / 大创申报书 / SRTP 申报书]。

题目或方向：[方向]
已做的初步工作：[已有数据、复现结果、读过的文献]
可用条件：[时间、设备、导师、经费、能否拿到数据]
评审要求：[字数、章节、评分标准、截止时间]

先用 idea-evaluator 判断这个想法值不值得做；
再给：要回答的问题（不是题目）、现状与缺口、方法路线、
初步结果（没有数据就写“待验证”，不要编）、周级时间表、
风险与备选方案、预期产出。
```

### 格式转换与 GB/T 7714

```text
把下面这份稿子转成 [目标格式 / 学校模板] 的格式。

当前格式：[现有格式]
目标格式：[课程模板 / 学位论文 / 期刊模板；具体字号、行距、标题层级]
参考文献：[现有条目或文献列表]

先用 academic-paper 的 format-convert 处理结构；
中文参考文献按 references/gbt7714.md 逐条手工核对，
不要声称 formatter_agent 能输出 GB/T 7714。
最后给一份修改清单：改了哪里、为什么、还有哪些需要我确认。
```

### 导出 Word（学院模板）

```text
把 draft.md 导出成要交的 .docx。

源文件：draft.md
模板：<学院模板.docx>（页边距、页眉、字体、字号以模板为准）
文献表：citations.csv（GB/T 7714-2015 顺序编码制）
输出：提交版.docx

步骤：
1. export_docx.py draft.md --template <模板> --references-csv citations.csv --out 提交版.docx
2. 对导出的 .docx 跑 check.py --type <course|imrad|lab|proposal|thesis> --citations-csv citations.csv，exit 0 才算完成；
3. 报告模板带来的差异（自带封面或说明段、样式名不匹配而退回默认样式、表格列丢失）；
4. 不要手改 .docx：Markdown 改了要重新导出，再跑一次 check.py。
```

### AI 使用声明

```text
帮我起草一份 AI 使用声明，符合 [课程 / 期刊 / 学校] 的要求。

我实际使用了 AI 做：[检索、整理、润色、翻译、代码、作图、其他]
没有使用 AI 做的：[选题、实验、数据分析、结论、最终改写]
使用工具与时间范围：[工具，大致时间]
相关要求原文：[粘贴课程或期刊的 AI 政策]

要求：只写真实使用范围，不夸大也不隐瞒；
把“机械性辅助”和“实质性贡献”分开写；
给出可直接粘贴的中英文两个版本，并标出需要我确认的空缺。
```

### 引用核验（citations.csv）

```text
帮我建立并核验引用表 citations.csv，规则见 references/citation-contract.md。

正文草稿：[路径 / 粘贴]
我手头已有的文献来源：[DOI 列表 / 图书馆链接 / 导师给的 PDF / 无]
引用格式：[GB/T 7714 / APA / IEEE]

要求：
1. 先写 citations.csv（字段见 references/citation-contract.md），每条必须有 DOI/URL 或出版信息+页码；
2. 运行 python scripts/verify_refs.py --csv citations.csv，把 MISMATCH / UNREACHABLE / NO_ID 逐条告诉我，并建议删除或更正；
3. 脚本通过的条目，再人工看它是否真的支持正文那句话；
4. 查不到的文献不要补造，宁可让正文主张降级；
5. 只对已核实的条目填写 verified_by 和 verified_on；
6. 最后运行 python scripts/check.py 草稿.md --type <类型> --citations-csv citations.csv，解释每个 CRITICAL 和 WARN。
```

## Literature（文献获取）

### 文献检索（`search_meta.py`）

```text
帮我为「题目 / 主题」检索文献。

主题与关键词（中英文各写几个）：[…]
时间范围：[如 2020 以后 / 不限]
语言偏好：[中文为主 / 英文为主 / 都要]
用途：[课程论文引 5 篇 / 开题背景 / 方法对比]

要求：
1. 先运行 python scripts/search_meta.py "关键词" --limit 10 [--year-from …]，把候选列给我；
2. 每条给出年份、作者、刊名/会议、DOI、被引数，并说明它可能支撑正文的哪个论点；
3. 没有 DOI 的条目单独标出——不能直接进正文；
4. 不要凭记忆补文献；检索不到就说检索不到；
5. 选定后写进 citations.csv 并跑 verify_refs.py。
```

### 馆藏核对（`opac_search.py`）

```text
帮我确认东南大学图书馆有没有这些书 / 学位论文：[题名或 ISBN 列表]

要求：
1. 运行 python scripts/opac_search.py --title "…" 或 --isbn …；
2. 给出索书号、出版信息、可借状态，附 item.php 链接；
3. 查不到时说明可能原因（只有电子版 / 外文写法不同），不要猜；
4. 查学位论文用 --keyword，注明学院与年份。
```

### 数据库导出 → `citations.csv`（`import_refs.py`）

```text
我从 [知网 / 万方 / IEEE / Elsevier / EBSCO] 导出了题录：[文件路径]
请把它并进 citations.csv。

要求：
1. 先 --dry-run 给我看会导入哪些、跳过哪些重复；
2. 导入后逐条跑 python scripts/verify_refs.py --only <id>，列出 OK / PARTIAL / MISMATCH / UNREACHABLE / NO_ID；
3. MISMATCH 以 DOI 登记为准修表；NO_ID 的条目标出（要有 URL 或页码才能用）；
4. 不要因为"格式看起来对"就填 verified_by；
5. 最后 python scripts/check.py 草稿.md --type <类型> --citations-csv citations.csv，核对正文与表是否一致。
```

## Screening

### `sr-screener`

```text
用 sr-screener 技能，按我的协议筛选文献记录。

当前模式：[protocol / pilot / ta-screen / ft-screen / adjudicate /
audit / report]
协议文件：[路径]
记录文件：[RIS / NBIB / CSV / EndNote / Zotero 路径]
输出目录：[路径]
评审者数量：[2]
是否需要第三评审裁决：[是 / 否]
排除原因顺序：[原因]

先检查协议和输入格式，再做 pilot。
不要默认纳入证据不足的记录，所有排除都必须有明确原因。
```

## Orchestration

### `academic-pipeline`

```text
用 academic-pipeline 技能，管理从研究问题到最终论文的完整项目。

研究主题：[主题]
目标期刊或会议：[名称]
学科：[学科]
论文类型：[类型]
可用数据：[数据]
时间预算：[时间]
语言：[语言]
输出格式：[LaTeX / DOCX / PDF / Markdown]
阶段确认要求：[每个阶段暂停 / 自动推进到某一步]

请建立十阶段计划，明确每阶段输入、输出、诚信检查、评审节点和所需资源。
所有引用、数据、实验结论都必须可核验。
```

## Cross-Cutting

### `vibe-research-workflow`

```text
用 vibe-research-workflow 技能，帮我设计“[当前任务]”的 AI 辅助流程。

当前活动：[Vibe Coding / Vibe Figure / Vibe Writing]
我已有的工具：[工具]
我不熟悉的部分：[部分]
必须由我本人判断的内容：[内容]
希望 AI 承担的工作：[工作]

请给出人机分工、推荐工具链、每一步的输入输出和常见失败模式。
```
