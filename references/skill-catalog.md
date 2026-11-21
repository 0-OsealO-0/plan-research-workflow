# Local Research Skill Catalog

Use this catalog to select the smallest useful set of local skills.

## Installation Roots

Library (source of truth for every installed skill):

```text
%USERPROFILE%\.skills-manager\skills
```

Agent roots, each exposing a subset of the library:

```text
%USERPROFILE%\.codex\skills       Codex
%USERPROFILE%\.dsh\skills         DeepSeek Harness (links or copies from the library)
%USERPROFILE%\.agents\skills      academic-paper, academic-paper-reviewer,
                                   academic-pipeline, deep-research,
                                   research-paper-writing, sr-screener
```

Rules:

- The library is where edits belong; agent roots are deployment targets.
- Codex and DeepSeek Harness each get their own copy or link, so a skill can be
  present in one and missing in the other.
- Skills installed only for DeepSeek Harness: `statistical-analysis`,
  `exploratory-data-analysis`, `matplotlib`, `uncertainty-and-units`, `sympy`.
- Before routing to a skill, check it appears in the current agent's skill list;
  a route to an absent skill fails silently and looks like the skill did nothing.
- Skills with source type `import` cannot be updated from git; a later
  `skills update` overwrites local edits, so keep a copy of any customization.

## Supervisor-Skills

### `idea-evaluator`

Function:

- Evaluate an idea before months of implementation.
- Score Higher, Faster, Stronger, Cheaper, and Broader dimensions.
- Audit fatal flaws, novelty, capability fit, feasibility, and paradigm-shift potential.

Use when:

- The user has a concrete idea.
- The user asks whether it is worth pursuing.
- The user compares several candidate ideas.

Required input:

- Idea statement.
- Method and intended contribution.
- Data, compute, skills, team, and available time.
- Target venue.

Output:

- Verdict.
- Fatal-flaw audit.
- Dimension scores.
- Feasibility risks.
- Next actions.

Do not use when:

- The user has no direction yet.
- The manuscript is already drafted.

### `tech-paper-template`

Function:

- Build the logical skeleton of a technical or new-problem paper.
- Align background, limitations, key idea, challenges, modules, and contributions.

Use when:

- The idea is validated.
- The paper story or module structure is unstable.

Required input:

- Research problem.
- Core Idea and contribution.
- Method modules.
- Known evidence.

Output:

- Thinking-template table.
- Four-point consistency check.
- Input for `intro-drafter`.

### `benchmark-paper-template`

Function:

- Structure benchmark and evaluation papers using five pillars.
- Cover gap, construction, evaluation, findings, and optional companion method.

Use when:

- The paper creates or evaluates a benchmark, dataset, or evaluation protocol.
- The gap, evaluation dimensions, or findings are unclear.

Required input:

- Research gap.
- Data construction plan.
- Evaluation design.
- Planned or completed experiments.

Output:

- Completeness audit.
- Six-part Introduction logic chain.
- Section 2 to 7 skeleton.
- Pre-submission checklist.

### `intro-drafter`

Function:

- Draft or outline a technical paper Introduction.
- Use a six-paragraph internal scaffold and verify citations.

Use when:

- The paper structure is settled.
- The user needs an Introduction specifically.

Required input:

- Structure skeleton.
- Running example.
- Key limitations and challenges.
- Target venue and citation style.

Output:

- Introduction prose or outline.
- References.

### `paper-writer`

Function:

- Draft publishable prose from the author's own materials.
- Enforce evidence-gated writing with no fabricated facts or placeholders.

Use when:

- The user needs a section or full draft.
- The structure and core evidence are available.

Required input:

- Notes, results, methods, data, figures, and verified references.
- Venue, language, format, and constraints.

Output:

- Clean prose.
- References.
- Evidence map and blueprint for full-paper tasks.

Do not use when:

- The request is Introduction only.
- The task is language-only polishing.
- The structure is unresolved.

### `anti-defensive-writing`

Function:

- Pick the narrative: identify the strongest supported advantage and organize the paper around it.
- Strip defensive writing: self-weakening phrases, work-log structure, volunteered weaknesses, experiment diaries, self-negation in the conclusion.
- Re-pick the headline result, narrow a claim, or cut results that do not carry the main line.

Use when:

- The draft reads apologetic, self-auditing, or like a project summary.
- Abstract, introduction, conclusion, or the experiment section needs reframing.
- A page or word budget forces a decision about which results stay.
- The manuscript is Chinese.

Required input:

- The draft or the section being reframed.
- The results actually available, with numbers.
- Target venue and page or word limit.
- Any unfavorable result that is load-bearing for a core claim.

Output:

- Reframed text, or a restructuring plan when the whole story moves.
- Changelog: what moved, was narrowed, or was cut, and why.
- Flags for claims with no evidence behind them, raised with the author rather than repaired by editing the data.

Do not use when:

- The problem is grammar, flow, or translation: `paper-polish`.
- The evidence itself is in doubt: `pre-submission-reviewer` or `idea-evaluator` first.
- The request is to manufacture support for a claim the data do not show.

Constraint: it changes framing, never numbers, results, citations, or methods. A load-bearing unfavorable result stays in the paper.

### `anti-defensive-writing-en`

English twin of `anti-defensive-writing`: same function, constraints, inputs, and output, for an English manuscript. Load one language version per task, never both.

### `paper-polish`

Function:

- Repair grammar, flow, tone, translation, and overclaiming.
- Translate Chinese academic prose into submission-quality English.

Use when:

- The scientific meaning and structure are sound.
- Only the language layer needs work.

Required input:

- Existing prose.
- Language target.
- Phrases or meanings that must not change.

Output:

- Polished prose.
- Main edits.
- Meaning-risk flags.

### `lieflat-less-ai-tone`

Function:

- Remove explicitly defined AI writing tells using a whitelist-based, minimal-edit process.
- Preserve unmatched sentences, document structure, claims, evidence, citations, numbers, and quotations.

Use when:

- The text is already substantively finished.
- Organization, evidence, terminology, and citations are frozen.
- The user specifically wants less AI-sounding prose without a broader rewrite.

Required input:

- Existing Markdown, Word, or plain-text draft.
- Scope and deliverable path.
- Any style reference or language-DNA document that should override the default rules.
- Content that must remain unchanged.

Output:

- Revised text with only rule-matched edits.
- Before-and-after examples for representative changes.
- A statement of which structure and source material remained unchanged.

Do not use when:

- The draft still has logic, evidence, citation, or structural problems.
- The user wants broader language polishing, translation, shortening, or expansion.
- The task would require changing claims or adding material.

### `figure-designer`

Function:

- Design the Motivated Example, Solution Overview, and Experimental Results figures.
- Recommend layout, labels, colors, and tools.

Use when:

- The narrative or method structure is known.
- The user needs figure planning or audit.

Required input:

- What each figure must communicate.
- Results or method structure.
- Venue and style constraints.

Output:

- Design guidance.
- Tool recommendation.
- Figure quality audit.

### `drawio-reconstruction`

Function:

- Reconstruct reference images as editable `.drawio` files.
- Export PNG previews and visual audits.

Use when:

- A reference image, diagram, architecture, slide, or UI screenshot exists.
- The deliverable must be editable.

Required input:

- Reference image or folder.
- Desired output path.
- Batch manifest when applicable.

Output:

- `.drawio` source.
- PNG preview.
- Audit record.

### `pre-submission-reviewer`

Function:

- Run the final operational audit before submission.
- Check logic, writing, grammar, LaTeX, and figures.
- Rank issues as CRITICAL, MAJOR, or MINOR.

Use when:

- Submission is within one week.
- The user needs repairs prioritized by deadline.

Required input:

- Full draft.
- Venue.
- Deadline.
- Formatting and figure files.

Output:

- Prioritized issue list.
- Fix recommendations.
- 72-hour repair subset.

### `rebuttal-guidance`

Function:

- Classify reviewer concerns.
- Match each concern to a response strategy, tone, and evidence pointer.

Use when:

- Reviewer comments have arrived.
- The user needs rebuttal strategy rather than polished rebuttal prose.

Required input:

- Reviewer comments.
- Relevant manuscript evidence.
- Constraints on additional experiments.

Output:

- Concern classification.
- Response strategy.

### `vibe-research-workflow`

Function:

- Define human-AI collaboration for research coding, figures, and writing.
- Recommend the right tool for the current activity.

Use when:

- The user is unsure what to delegate to AI.
- The user needs an AI-assisted research workflow.

Output:

- Tool choice.
- Human-AI division of work.
- Failure-mode guidance.

## Data and Computation

These are analysis skills, not writing skills: they decide what the numbers mean
before any prose claims something about them.

### `statistical-analysis`

Function:

- Select the right test, check its assumptions, report effect sizes and power.
- Produce APA-style statistical reporting.

Use when:

- The task compares groups, tests a hypothesis, or analyzes survey or experiment data.
- A draft reports a test that may not match the design.

Required input:

- Data or a summary table.
- Design: groups, sample size, independence, repeated measures.
- The claim the analysis must support.

Output:

- Test choice with rationale, assumption checks, results, effect sizes.
- A reporting paragraph.

Do not use when:

- The data do not exist yet; collect first.

### `exploratory-data-analysis`

Function:

- Bounded profile of a local dataset: columns, types, missingness, distributions.
- Leakage and outlier checks.

Use when:

- The dataset is new and its shape is unknown.
- Results look too good and need a leakage audit.

Required input:

- A local CSV, TSV, JSON, or supported scientific file.

Output:

- Data profile, anomalies, and a short list of questions the data can answer.

### `matplotlib`

Function:

- Publication-quality plots with explicit control over axes, ticks, fonts, and export.

Use when:

- A figure needs precise sizing, panel layout, or journal styling.

Required input:

- Data or a summary table, plus target figure size and format.

Output:

- Plot script and PNG, PDF, or SVG output.

### `uncertainty-and-units`

Function:

- Track physical units and propagate measurement uncertainty.
- GUM uncertainty budgets, significant figures, coverage factors.

Use when:

- A lab report or experiment reports measured quantities with error bars.
- A calculation mixes units.

Required input:

- Values with units, uncertainty sources, confidence level.

Output:

- Converted values, propagated uncertainty, correctly rounded reporting.

Note: `sympy` is available for exact symbolic work; use it only when a result
must stay symbolic, not for ordinary numerical analysis.

## academic-research-skills

### `deep-research`

Function:

- Act as the general research director.
- Support question formulation, methodology, literature search, synthesis, fact checking, systematic review, and meta-analysis.

Use when:

- The topic or direction is unclear.
- A literature review or systematic review is required.
- Research questions and methodology must be designed together.

Required input:

- Topic.
- Discipline.
- Scope.
- Research questions if known.
- Source and access constraints.

Output:

- Research plan.
- Verified literature synthesis.
- Review or meta-analysis materials.

### `academic-paper`

Function:

- Manage paper writing from outline to final output.
- Support full, plan, outline, revision, revision-coach, abstract, lit-review, format-convert, citation-check, disclosure, and rebuttal-audit modes.
- Convert between APA 7.0 (default), Chicago, MLA 9, IEEE, and Vancouver. It has
  no GB/T 7714 formatter: Chinese references must be built against
  `references/gbt7714.md` and then checked for consistency, not converted.

Use when:

- The project is paper-level rather than section-level.
- The user needs revision, citations, formatting, AI disclosure, or rebuttal audit.

Required input:

- Current manuscript or notes.
- Target venue.
- Required format and citation style.
- Review comments when revising.

Output:

- Manuscript or revision.
- Citation and format checks.
- Revision or rebuttal audit.

### `academic-paper-reviewer`

Function:

- Simulate multi-perspective peer review.
- Support full review, re-review, quick assessment, methodology focus, guided review, and calibration.

Use when:

- The draft needs substantive review.
- The user needs an editorial decision or revision roadmap.

Required input:

- Full manuscript.
- Target venue.
- Review stage and desired mode.

Output:

- Reviewer reports.
- Editorial decision.
- Revision roadmap or re-review.

### `academic-pipeline`

Function:

- Orchestrate research, writing, integrity checks, review, revision, and finalization.

Use when:

- The user wants one managed project from research question to final paper.

Required input:

- Project objective.
- Discipline and target venue.
- Constraints and available materials.
- Preferred stage checkpoints.

Output:

- Stage plan and artifacts.
- Integrity checks.
- Two-stage review.
- Final package.

Do not use when:

- The user only needs one stage.
- The user wants to control every step manually.

### `sr-screener`

Function:

- Screen systematic, scoping, and rapid-review records using a protocol.
- Support blinded reviewers, adjudication, PRISMA, and evidence export.

Use when:

- A protocol or PROSPERO plan exists.
- Records are ready for title, abstract, or full-text screening.

Required input:

- Eligibility rules.
- RIS, PubMed, Web of Science, EndNote, Zotero, or CSV records.
- Output directory and screening mode.

Output:

- Screening log.
- Conflict resolution.
- PRISMA counts.
- Literature corpus.

## Research-Paper-Writing-Skills

### `research-paper-writing`

Function:

- Improve the structure, paragraph flow, presentation, and claim-evidence alignment of existing ML, CV, or NLP papers.

Use when:

- A draft already exists.
- The user needs section-level rewriting or reviewer-facing improvement.

Required input:

- Existing sections.
- Experimental evidence.
- Target venue.
- Claim-evidence mapping when available.

Output:

- Section outline.
- Rewritten paragraphs with roles.
- Self-review checklist.
- Claim | Evidence | Status map.

## Degradation order

Run `scripts/preflight.py --require <chain>` before approving a plan. When a
required skill is missing from every root, use the substitute below and say what
is lost; do not silently skip the step, and do not present the substitute as
having the same coverage.

| 首选 | 替代 | 损失 |
|---|---|---|
| `deep-research` | 手动检索（`web_search` / `web_fetch`）+ 来源矩阵 | 系统化检索与来源核验的覆盖面 |
| `academic-paper` | `paper-writer` + `pre-submission-reviewer` 分步 | 分阶段编排、格式转换、模板一致性 |
| `academic-pipeline` | 按 playbook 1/3 手动执行 | 审计产物、两轮评审的完整性门 |
| `academic-paper-reviewer` | `pre-submission-reviewer` + 自拟反驳 | 多视角审稿与 devil's advocate 的独立视角 |
| `sr-screener` | 手动标题/摘要筛选 + 记录排除码 | 双人盲筛、kappa 一致性 |
| `tech-paper-template` | `intro-drafter` 大纲 + 自检 | 逻辑骨架的完整性检查 |
| `benchmark-paper-template` | `tech-paper-template` | 基准论文五支柱的结构审计 |
| `paper-writer` | 用户自写 + `paper-polish` | 逐段生成的速度与表达一致性 |
| `paper-polish` | `research-paper-writing` 的写作建议 | 语言层精修与语气校准 |
| `lieflat-less-ai-tone` | `paper-polish` 的 AI 味清理规则 | 白名单式保守清理，误改风险更高 |
| `anti-defensive-writing` | 无可靠替代 | 叙事判断（主线、取舍、克制自我削弱）需人做 |
| `figure-designer` | `matplotlib` 直接画 | 图形设计与版式建议 |
| `drawio-reconstruction` | `figure-designer` + 手绘 | 参考图重建的可编辑性 |
| `rebuttal-guidance` | `academic-paper` rebuttal-audit | 审稿人心理与策略建议 |
| `statistical-analysis` | `exploratory-data-analysis` + 手算检验 | 检验选择与假设检查的自动化 |
| `uncertainty-and-units` | 手算不确定度与量纲 | 批量单位换算与 GUM 预算 |
| `matplotlib` | 其他绘图工具（Excel/Origin） | 出版级样式与可复现脚本 |

Rules:

- 替代只能降级，不能包装成同等级。报告里写"改用 X 替代，代价是 Y"。
- 替代品仍必须过同一道质量门（`check.py` / `verify_refs.py` / 人工评审）。
- `anti-defensive-writing` 缺失时，不要用"少说缺点"冒充叙事判断。

## Selection Summary

- Direction unknown: `deep-research`.
- Data analysis or test choice: `statistical-analysis`.
- New dataset needs a profile or leakage audit: `exploratory-data-analysis`.
- Publication-quality plot: `matplotlib` (large redraw: `figure-designer` first).
- Measurements with error bars: `uncertainty-and-units`.
- Course paper, no new contribution: `paper-writer` → `paper-polish` → `lieflat-less-ai-tone`.
- Lab report or experiment write-up: playbook 9.
- 大创, SRTP, or 开题 proposal: playbook 10.
- Chinese references or thesis layout: `references/gbt7714.md`, then `academic-paper` citation-check.
- Long-range planning across years: `references/student-roadmap.md`.
- Idea needs evaluation: `idea-evaluator`.
- Technical structure: `tech-paper-template`.
- Benchmark structure: `benchmark-paper-template`.
- Introduction: `intro-drafter`.
- New prose: `paper-writer`.
- Defensive, apologetic, or log-like draft: `anti-defensive-writing` (English: `anti-defensive-writing-en`).
- Project-level paper work: `academic-paper`.
- Existing ML, CV, or NLP draft: `research-paper-writing`.
- Figures: `figure-designer` then `drawio-reconstruction`.
- Language: `paper-polish`.
- Final AI-tone cleanup: `lieflat-less-ai-tone`.
- Substantive review: `academic-paper-reviewer`.
- Final deadline audit: `pre-submission-reviewer`.
- Rebuttal: `rebuttal-guidance`.
- Screening: `sr-screener`.
- Full project: `academic-pipeline`.
