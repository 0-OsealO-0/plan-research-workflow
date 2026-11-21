# Worked Example: Course Research Report

This example demonstrates how `plan-research-workflow` should respond when the user asks about a course project.

## User Request

```text
我要完成“新思想概论第六章：推动高质量发展”的四千字小组报告。
我已经有五篇指定研读材料、课程要求、报告目录和四人分工草案。
请给我一条具体工作链，并告诉我每一步要提供什么、用什么 skill、
具体 prompt 是什么。
```

## Stage Diagnosis

- Current stage: discovery and evidence organization.
- Task type: humanities or social science course report.
- Paper type: course research report, not a submission-ready technical paper.
- Main risk: using secondary web articles instead of the five designated primary texts.
- Primary skill: `deep-research`.
- Later skills: `research-paper-writing`, `paper-polish`, `lieflat-less-ai-tone`, and `academic-paper` citation-check.

## Missing Information

Must provide:

- five source PDFs,
- course brief and grading criteria,
- group division,
- required report structure and submission format.

Must decide:

- whether only the five assigned texts are allowed,
- whether one real case is required,
- whether the final output is Word, PDF, or both.

Assumptions if not answered:

- Use only the five assigned texts as primary evidence.
- Do not add outside empirical cases.
- Output a Chinese Word-ready report and a separate source matrix.

## Resource Schedule

| Timing | What the user must provide | Why it is needed | Where it is used |
|---|---|---|---|
| Now | Five assigned PDFs, course brief, group brief, report requirements | Defines the evidence boundary and grading target | `deep-research` |
| Now | Confirmed group roles and report title | Prevents overlapping ownership | Research matrix and outline |
| Before writing | Source matrix with page references and quotations | Ensures every claim is traceable | `research-paper-writing` |
| Before polishing | Complete four-thousand-character draft | Allows section-level flow and transition repair | `paper-polish` |
| Before AI-tone cleanup | Polished draft with frozen structure, citations, and quotations | Prevents style cleanup from masking substantive problems | `lieflat-less-ai-tone` |
| Before submission | Final Word file, references, file-name rule | Prevents formatting and submission errors | `academic-paper` citation-check |

## Skill Chain

| Step | Skill | Purpose | Required input | Deliverable | Gate |
|---|---|---|---|---|---|
| 1 | `deep-research` | Organize five assigned texts into evidence matrix and detailed outline | Five PDFs, brief, grading rules | Source matrix, chapter outline, group division | Each claim has a page or section reference |
| 2 | `research-paper-writing` | Improve abstract, introduction, transitions, and conclusion | Draft and source matrix | Revised target sections and Claim-Evidence table | Every major claim has supporting evidence |
| 3 | `paper-polish` | Improve Chinese academic expression and consistency | Revised full draft | Polished report | Meaning and quotations remain unchanged |
| 4 | `lieflat-less-ai-tone` | Remove only whitelist-matched AI writing tells as the final editorial pass | Polished report and frozen source material | Minimal-edit revised report and before-after comparison | Structure, claims, citations, numbers, quotations, and unmatched text are preserved |
| 5 | `academic-paper` citation-check | Verify references, citations, and Word formatting | Final draft and reference list | Citation report and submission-ready file | All references match source text |

## Exact Prompts

### Step 1

```text
用 deep-research 技能，围绕“从三大变革到新质生产力：推动高质量发展的逻辑、实践与青年行动”整理课程报告。

证据范围：只使用我提供的五篇指定研读文本，不检索网络二手文章。
课程要求：[粘贴要求]
小组分工：[粘贴分工]
五篇材料路径：[粘贴路径]

请输出：
1. 资料矩阵：篇目、页码或期号、核心观点、可引用原句、对应报告章节、建议负责人；
2. 四千字报告的详细目录；
3. 每一节的核心判断和证据；
4. 组员分工与交叉审阅建议；
5. 需要我补充或确认的信息。

所有引文不得改写原意，页码或章节定位必须准确。
```

### Step 2

```text
用 research-paper-writing 技能，不要重写全文，只优化课程报告的摘要、引言、章节过渡和结论。

重点检查：
1. 每段是否只有一个中心意思；
2. 第一句是否点明本段主题；
3. 术语是否前后一致；
4. 每个主要判断是否有原著、政策或案例支撑；
5. 输出 Claim | Evidence | Status 对照表。

不能新增未经指定材料支持的事实或案例。
```

### Step 3

```text
用 paper-polish 技能润色这份课程报告。

目标：让语言更适合大学课程研学报告，保持理论性、科学性、价值性和真实性。
不能改变引文、政策表述、数据、结论和组员观点。
任何可能改变原意的修改请单独列出。
```

### Step 4

```text
用 lieflat-less-ai-tone 技能处理这份已经完成内容和引用的课程报告。

原文件：[路径]
输出文件：[路径]
目标语体：大学课程研学报告
语言：中文
现有风格参考：[路径或明确说明没有]
必须保持不变：标题层级、章节顺序、段落顺序、全部观点、引文、政策表述、
数据、参考文献、脚注、作者分工与 AI 使用说明。

只处理该 skill 明确列出的 AI 写作痕迹规则。
未命中规则的文字逐字保留；不得扩写、缩写、重排或新增案例。
如果仍有逻辑、证据、引用或结构问题，请停止并指出，不要继续改写。
完成后给出代表性前后对比，并列出未改动的内容。
```

### Step 5

```text
用 academic-paper 技能，以 citation-check 模式检查这份课程报告的参考文献和正文引用。

请核对：
1. 正文引用与参考文献是否双向对应；
2. 页码、篇名、作者和出处是否一致；
3. 是否存在重复计算同一文本的情况；
4. Word 文件格式是否符合课程提交要求；
5. 文件名是否满足“研学报告+班级号+报告名称（组长姓名组）”规则。
```

## Quality Gates

Evidence gate:

- Only the five assigned texts count as primary evidence.
- Secondary explanations must be clearly separated.

Argument gate:

- High-quality development must be treated as a system transition.
- The three transformations, new quality productive forces, policy practice, and youth action must form one logical chain.

Citation gate:

- Each quotation must have a page or section location.
- Shortened quotations must not change meaning.

Policy gate:

- Policy deployment must not be described as an already achieved outcome.

Format gate:

- Length, citation format, file name, and group roles must match the course brief.

AI-tone cleanup gate:

- Substantive structure, evidence, citations, numbers, and quotations are already frozen.
- Only whitelist-matched AI writing tells are changed.
- Unmatched text and the logical content of the report remain intact.

## Immediate Next Action

Place the five assigned PDFs, the course brief, the group division, and the report requirement in one folder, then run the Step 1 prompt with that folder path.
