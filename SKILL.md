---
name: plan-research-workflow
description: >-
  Turn a paper, thesis, course project, research question, proposal,
  experiment, literature review, writing task, revision, review, submission, or
  final AI-tone cleanup request into a concrete workflow using the research
  skills installed on this machine. Use when the user asks how to approach a
  paper or research task, which skill to use, what to provide at each stage, in
  what order to work, or asks for exact prompts and an example workflow.
  Diagnose the current stage, select the minimum useful skill chain, specify
  required resources and decisions, then run the chain one approved step at a
  time, and add quality gates without inventing unavailable tools. Supports a
  plan-only mode that writes nothing.
  中文说法同样可以触发：这个作业怎么写、论文从哪开始、帮我把这篇论文走完、帮我
  规划一下、文献从哪找、参考文献怎么引、格式怎么改、还要准备什么、我下一步该干
  什么、审稿意见怎么回、投稿前该检查什么、帮我看看流程对不对、只给计划先别动文件。
---

# Plan Research Workflow

## Purpose

Convert the user's paper or research request into an executable workflow based on locally installed skills.

The skill must:

1. Diagnose the user's current stage.
2. Identify only the critical missing information.
3. Select one primary skill at a time.
4. State when the user must provide resources, evidence, or decisions.
5. Plan the handoff, then run it: invoke the named skill with a parameter block instead of printing a prompt the user has to copy into another skill.
6. Add quality gates and stop conditions.
7. End with a concrete example adapted to the user's subject.

This skill is an orchestrator and executor, not a prompt generator. Default to execute mode: diagnose, list the full step plan, take one approval, then run one step per message and report evidence. Keep plan mode for thinking-only requests.

## Operating Model

Two modes, one loop; the full protocol is `references/execution-protocol.md`.

| Mode | When | Behavior |
|---|---|---|
| `execute` (default) | the user wants the work done | diagnose, propose the step plan, take one approval, then run the named skills yourself, one step per message |
| `plan` | 只给计划 / 先别执行 / 不要改文件 / 只看思路, or a form-filling or defense-prep request | read-only: analyze and return the plan; write nothing |

State the mode in the first line, for example `模式：execute（说"只给计划"可冻结为计划模式）`.

Execution loop:

1. Diagnose from the conversation and the files already on disk.
2. Propose the complete step plan, including the paths that will be written.
3. Ask for approval once.
4. After approval, run one step per message: load the skill, follow it with the
   step's parameters, then report. Once approved, every reply runs the next step
   automatically; do not ask "shall I continue" between steps. If the host has no
   skill-loading tool (some editors only read Markdown), read that skill's
   `SKILL.md` from disk and follow it directly — the procedure is the same, only
   the loading mechanism differs.
5. Report: skill, artifact path, what changed with line ranges, the verification
   you ran, gate status, next step.
6. Stop at a decision point, a missing input, or a failed gate; never pass a
   failed gate.

At a decision point, offer at most three options with cost, benefit, and risk,
plus a recommendation, and accept a conditional override. In `execute` mode back
up an existing user file before overwriting it, and never delete anything.

## First Actions

1. Determine whether the request is about:
   - finding a direction,
   - searching for literature, or checking whether the library holds a book or thesis,
   - validating an idea,
   - planning a paper,
   - deciding the paper's narrative or which results carry it,
   - writing a section,
   - creating figures,
   - analyzing data or choosing a statistical test,
   - polishing text,
   - removing AI writing tells from finished text,
   - reviewing a draft,
   - responding to reviewers,
   - systematic review or screening,
   - or managing the entire project.
2. Classify the work as technical paper, benchmark paper, empirical study, humanities or social science paper, course report, review paper, or unknown.
3. Read `references/skill-catalog.md` when choosing a skill.
4. Read only the relevant scenario in `references/workflow-playbooks.md`.
5. Read `references/prompt-library.md` for the handoff fields of the chosen skill; in `plan` mode these are the prompts to print.
6. Read `references/example-course-report.md` when the user asks for a concrete example.
7. Read `references/execution-protocol.md` before running any downstream skill, and decide the mode first: `execute` unless the user asks for thinking only.
8. Before proposing a step plan, run `scripts/preflight.py --require <the chain's skills>` (rule 22); add `--explain` when anything is missing (rule 32).
9. On the first use on a machine, or whenever literature access is needed and `institution.local.md` is
   missing, run the one-time profile in `references/institution-setup.md` (school, department, discipline,
   OPAC base, remote access, databases). Store it in the untracked `institution.local.md` and never assume
   a school. Ask at most the three questions it lists, once.
10. If preflight reports missing skills, run `scripts/preflight.py --explain` and
    put the list to the user before doing anything else: each missing skill's role,
    its install source (when one exists), and what degrades without it (rule 32).

If the user's request is already specific enough, proceed with stated assumptions instead of asking many questions.

## 首次使用：机构档案

本 skill 不内置任何学校信息。第一次使用时先按 `references/institution-setup.md` 问三件事（学校院系 /
学科方向 / 文献入口），写进**不提交**的 `institution.local.md`，后续会话直接复用。

- 没配置时：文献检索走 `search_meta.py`（无需机构），馆藏检查降级为人工，参考文献仍按 GB/T 7714。
- 不要在交付物里写死「某某大学图书馆」；用户没说的机构信息，问一次，不要猜。
- 环境变量 `PAPERFLOW_OPAC_BASE` / `PAPERFLOW_OPAC_RSS` 优先于档案文件。

## Routing Rules

Use these rules as the default selection logic. When two rows could match, or the
first message is short, ambiguous, or names only a deadline, run the three probes
and the misjudgment table in `references/routing-checklist.md` before choosing.

| Situation | Primary skill | Support or later skill |
|---|---|---|
| No clear research direction | `deep-research` | `idea-evaluator`, `academic-paper` |
| Find papers on a topic, or the DOI of a known paper | `scripts/search_meta.py` (OpenAlex / Crossref) | `references/library-access.md` for entry points |
| Does the library own this book or thesis, and where is it | `scripts/opac_search.py` (your OPAC, once configured) | `references/institution-setup.md`, then `references/library-access.md` |
| References exported from CNKI / 万方 / IEEE need to enter the work | `scripts/import_refs.py` into `citations.csv` | `scripts/verify_refs.py` before any of them is cited |
| User wants the plan only: filling a form, preparing a defense, or says 只给计划 | this skill in `plan` mode | none; no downstream skill writes files |
| Specific idea needs validation | `idea-evaluator` | `tech-paper-template` or `benchmark-paper-template` |
| Technical paper structure is unstable | `tech-paper-template` | `intro-drafter`, `paper-writer` |
| Benchmark or evaluation paper | `benchmark-paper-template` | `figure-designer`, `pre-submission-reviewer` |
| Introduction only | `intro-drafter` | `paper-polish` |
| Other section or full draft from author materials | `paper-writer` | `paper-polish`, reviewer |
| Draft reads defensive, apologetic, or like a work log | `anti-defensive-writing` | `paper-writer` for new prose, `paper-polish` after |
| Choosing the main line, headline result, or which results stay | `anti-defensive-writing` | `pre-submission-reviewer` on the rebuilt draft |
| Project-level writing, revision, citation, format, rebuttal audit | `academic-paper` | `academic-pipeline` |
| ML, CV, or NLP paper already drafted | `research-paper-writing` | `paper-polish`, `pre-submission-reviewer` |
| Figure design | `figure-designer` | `drawio-reconstruction` |
| Reference image must become editable Draw.io | `drawio-reconstruction` | `pre-submission-reviewer` |
| Data analysis, statistical test choice, or reporting numbers | `statistical-analysis` | `exploratory-data-analysis` for profiling, `matplotlib` for figures |
| Lab report or experiment write-up without a literature contribution | `paper-writer` | `statistical-analysis`, `figure-designer`, `paper-polish` |
| Course paper or report for a class | `paper-writer` | `paper-polish`, `lieflat-less-ai-tone`; add `deep-research` only when a literature review is required |
| 大创 / SRTP / 开题 or grant proposal | `academic-paper` plan or outline mode | `tech-paper-template`, `pre-submission-reviewer` |
| Chinese journal or thesis formatting (GB/T 7714) | `academic-paper` citation-check | rule reference in `references/gbt7714.md` |
| Citation authenticity in doubt (fabricated or mismatched references) | run `scripts/verify_refs.py` before anything else | `academic-paper` citation-check for style only |
| Language-only polishing | `paper-polish` | `pre-submission-reviewer` |
| Finished text needs whitelist-based AI-tone cleanup | `lieflat-less-ai-tone` | `pre-submission-reviewer` when a final audit is also required |
| Substantive simulated peer review | `academic-paper-reviewer` | `academic-paper` revision mode |
| Deadline-focused final audit | `pre-submission-reviewer` | `paper-polish` |
| Rebuttal strategy | `rebuttal-guidance` | `academic-paper` rebuttal audit |
| Systematic review or meta-analysis | `deep-research` | `sr-screener`, `academic-paper` |
| Record screening | `sr-screener` | `academic-paper` |
| End-to-end project from question to final paper | `academic-pipeline` | Do not duplicate its internal chain manually |
| AI collaboration rules | `vibe-research-workflow` | Cross-cutting only |

### Overlap Rules

`deep-research`:

- Use the installed `.agents` version as the default.
- Do not activate two same-name versions.

Writing:

- Use `paper-writer` to draft new prose from author materials.
- Use `academic-paper` for project-level writing, revision, citation, format, and rebuttal work.
- Use `research-paper-writing` to improve an existing ML, CV, or NLP draft.

Review:

- Use `academic-paper-reviewer` for substantive peer review.
- Use `pre-submission-reviewer` for the final operational pass before submission.
- For high-stakes papers, review substantively first, revise, then run the final audit.

Language versus structure:

- Use `paper-polish` when the logic is sound and only language needs work.
- Use `research-paper-writing` when paragraphs, section flow, or claim-evidence alignment need work.

Language polishing versus AI-tone cleanup:

- Use `paper-polish` for broader grammar, flow, tone, translation, and overclaiming repairs.
- Use `lieflat-less-ai-tone` only when meaning, structure, evidence, and citations are frozen and the remaining task is removing explicitly defined AI writing tells.
- When both are needed, run `paper-polish` first, then `lieflat-less-ai-tone` as the final editorial pass.
- Do not run both in the same step or use AI-tone cleanup to repair logic, evidence, organization, or citation problems.

Narrative versus evidence:

- Use `anti-defensive-writing` to pick the main line, name the advantage the paper actually wins on, set claim scope, and strip self-undermining language. Use `anti-defensive-writing-en` when the manuscript is English.
- Order matters: narrative decision first, prose second. Run `anti-defensive-writing` before `paper-writer`/`intro-drafter` on a new draft, and before `paper-polish` on an existing one.
- `anti-defensive-writing` may reframe, reorder, narrow, cut, or re-pick the headline result. It may never change numbers, results, citations, or methods, and it may never hide an unfavorable result that carries a core claim.
- When its advice conflicts with evidence discipline, evidence discipline wins. `paper-polish` still calibrates verb strength to evidence; `pre-submission-reviewer` still audits whether claims survive the data.
- On revision or rebuttal, rerun the narrative pass after the review, because revision drafts grow new hedging.

## Required Output Format

Return these sections unless the user asks for a shorter answer.

In `execute` mode, sections 1-4 are delivered once as the approval request, then section 5 is updated every step. In `plan` mode all sections are delivered once and the run stops.

Scale the answer to the task: a single-step question (one section, one figure, one
format fix) needs Stage Diagnosis, the one-skill chain, the exact prompt, and
Immediate Next Action. A project-level or first-time request gets all eight
sections. Do not dress a ten-minute task as a semester plan.

### 1. Stage Diagnosis

State:

- current stage,
- task type,
- likely paper type,
- main risk,
- recommended primary skill,
- **the evidence you diagnosed from** (one line: which words, files, or deadline),
- **the correction sentence**, verbatim: 「如果你不是这个场景，回一句『不是，我是 Y』，我重排链条，已产出的文件不动。」

The diagnosis is a claim, not a fact. Announce it before spending the user's time
on a chain built from it. A correction is handled by rule 25 and
`references/routing-checklist.md`, "Correction protocol".

### 2. Missing Information

List at most three critical missing items.

Separate:

- information the user must provide,
- decisions the user must make,
- assumptions you will use if the user does not answer.

### 3. Resource Schedule

Use a table:

| Timing | What the user must provide | Why it is needed | Where it is used |
|---|---|---|---|

Cover resources needed now, before drafting, before review, and before finalization.

### 4. Skill Chain

Use a table:

Start from the playbook's minimal chain and name the reason for every step added
beyond it. Above the table, state the preflight result in one line: either every
skill is present, or the substitute and what it costs.

| Step | Skill | Purpose | Required input | Deliverable | Gate before moving on |
|---|---|---|---|---|---|

Rules:

- One primary skill per step.
- `preflight.py` looks in the library and in the per-agent skill directories
  (`~/.codex/skills`, `~/.dsh/skills`, `~/.claude/skills`, `~/.cursor/skills`,
  `~/.config/opencode/skill`, plus `<project>/.claude/skills` and
  `<project>/.cursor/skills`). A skill present in any of them counts as installed;
  if the layout is unusual, extend the search with `PAPERFLOW_SKILL_ROOTS`.
- Mark optional steps.
- Avoid overlapping skills in the same step.
- Keep the shortest chain that can solve the task.
- Put `lieflat-less-ai-tone` after all substantive writing and polishing, immediately before final citation or submission checks.

### 5. Step Plan and Handoff

In `execute` mode this is the run ledger: for each step, the skill, the
parameters passed, the artifact path, the verification, and the gate status. Run
the skill yourself; do not print prompts for the user to paste elsewhere.

In `plan` mode, give one copy-ready prompt per step, including:

- current task and stage,
- named skill,
- source materials and paths,
- target venue or course,
- output language and format,
- evidence discipline,
- expected deliverable,
- what must not be changed.

### 6. Quality Gates

Include:

- evidence gate,
- narrative gate: the main line rests on the paper's strongest supported advantage, and no load-bearing claim exceeds its evidence,
- structure gate,
- claim-evidence gate,
- citation verification,
- human review of experimental facts,
- AI-tone cleanup gate when `lieflat-less-ai-tone` is used,
- final submission gate.
- data and statistics gate: sample size, test choice, effect size, and uncertainty are stated and match the design; `statistical-analysis` owns this.
- academic-integrity gate: AI use is disclosed as the venue or course requires, no citation or data is fabricated, and a similarity check is run where required.
- format and template gate: the draft matches the course template or the Chinese thesis layout, including GB/T 7714 references.
- reproducibility gate (when the venue or course requires it): data, code, or derivation are available to the degree the claim needs.

### 7. Concrete Example

Give a worked example based on the user's actual topic when available.

If no topic is available, use a realistic example and label it as illustrative.

### 8. Immediate Next Action or Waiting Point

In `execute` mode, end with the step that will run next, or the single decision
or missing input blocking it. In `plan` mode, end with one exact action the user
should take now.

Do not end with a generic offer to continue.

## Deterministic Checks

Machines check what machines can. After any step that writes or rewrites a
draft, run (`<skill>` is this skill's install directory, e.g.
`C:\Users\<you>\.dsh\skills\plan-research-workflow`):

```text
python <skill>/scripts/check.py <file> --type <course|imrad|lab|proposal|thesis|generic> [--min-words N] [--max-words N] [--citations-csv citations.csv]
```

Exit code 0 means no critical finding, 1 means at least one critical finding,
2 means a usage or file error.

Before anything is exported or declared final, run the skill ledger:

```text
python <skill>/scripts/usage_report.py --root .
```

Exit 0 means every required skill appears in `paperflow/runlog.md`, 1 means one
did not (this blocks the export gate), 2 means the project has no state file
yet. The table it prints is what you show the user before exporting: which
skills ran, which did not, and what each one exists to catch.

The script checks:

- code-fence balance,
- leftover placeholders (TODO, 待补, 模板变量),
- body citations against the reference list: missing entries, duplicates,
  orphan entries,
- reference entries missing a year, a type marker, or any identifier
  (DOI / URL / page numbers) that would let someone check them,
- with `--citations-csv`: cited ids absent from `citations.csv` (CRITICAL),
  rows not yet verified, orphan rows, and a count mismatch between table and
  reference list,
- figure and table references against captions,
- banned self-weakening phrases, flagged tone phrases, and em-dash overuse,
- required sections for the draft type,
- word count against the assigned range, using Word's counting (CJK characters
  plus Latin/number tokens, references and tables included) — report that number
  and not a CJK-only count, or the assignment limit is silently exceeded,
- banned near-synonyms listed in `术语表.md` beside the draft,
- body numbers that disagree with a single-valued `参数 | 设定值` table row.

The script does not check whether a claim is true, whether a citation supports
the sentence it is attached to, whether the statistics fit the design, whether
the narrative persuades, or whether a reference exists at all. Those stay with
the reviewer and with the user.

**The gate depends on what the step writes:**

| Artifact | Gate before the step may be called complete |
|---|---|
| `.md` draft, `.docx` submission | `check.py` exit 0, with `--citations-csv` when the draft cites |
| `citations.csv` | `verify_refs.py` on the changed rows, then `check.py --citations-csv` |
| figure (`.png`, `.svg`, `.pdf`) | open it: axes, labels, units, and the number in the caption match the data |
| script or other code | run it once on the real input and report its exit code |
| data table | re-read the numbers against the source and report the row count |

A step is complete only when the gate for its artifact passed; report the gate and
its result. Output that looks plausible is not a gate.

In `plan` mode run only read-only commands (`check.py`, `preflight.py`,
`verify_refs.py --offline`); they write nothing. Then say which command the user
can run once a draft exists.

When you edit this skill's own documentation, run `scripts/lint_docs.py`: it
checks rule numbering, per-playbook `Minimal:` lines, the verbatim correction
sentence, and code fences.

Reference existence is a separate, networked check:

```text
python <skill>/scripts/verify_refs.py --csv citations.csv [--only 3,5] [--strict] [--offline] [--assign-ids] [--allow-unchecked]
```

It resolves every DOI through doi.org and compares title, year, first author,
venue, and page. Exit 1 (`MISMATCH`, `UNREACHABLE`, `NO_ID`) blocks submission.
Exit 2 means the input could not be checked at all — missing `id` column, a CSV
with only a header, or `--only` matching nothing. That is a failure, not a pass:
a report with zero verified rows never counts as verification. Exit 3 means
`--offline` left rows `UNCHECKED`; pass `--allow-unchecked` only when you accept
that nothing was actually checked. ISBN-only rows are reported `MANUAL` (no
doi.org record exists) and do not fail the run.
Never write `verified_by` without having seen the resolved record; `--offline`
output may not be reported as verification.

## Literature Acquisition

Literature has three separate channels, and they are not interchangeable.
`references/library-access.md` holds the endpoint table, the export formats, the
compliance rules, and the failure table.

```text
python scripts/search_meta.py "深层学习 交通流" --limit 10 [--source auto|crossref|openalex] [--year-from 2021] [--doi 10.xxxx/yyy]
python scripts/opac_search.py --title "机器学习" [--author 周志华 | --keyword 交通安全 | --isbn ...] [--limit 10]
python scripts/import_refs.py refs.ris [refs.bib ...] --csv citations.csv [--dry-run]
```

- **Metadata** comes from open APIs (`search_meta.py`), not from a library
  database; it yields candidates with DOI, year, venue. No login, no VPN.
- **Holdings** come from whatever catalogue the user configured
  (`opac_search.py --base`, `PAPERFLOW_OPAC_BASE`, or `institution.local.md`):
  paper copies, call numbers, theses. It does not index journal articles, and it
  has no fallback institution — with nothing configured it prints the setup
  steps and exits 2.
- **Full text** requires the user's own institutional login (VPN / WebVPN /
  aTrust / EZproxy — see `library-access.md`). The flow supplies the search terms
  and reads back exported files; it never authenticates, never bypasses a captcha
  or paywall, and never bulk-downloads. Vendors answer 418/420/429 to bots,
  Chinese databases need 统一身份认证, and systematic downloading can get the
  whole campus IP blocked.
- An exported reference is metadata, not proof: `import_refs.py` writes rows with
  `verified_by` empty on purpose, and rule 20 still applies before any of them
  reaches the body.

## Word Delivery

Most Chinese course papers, lab reports, and 申报书 are submitted as `.docx` with
a school template (margins, header, 宋体/小四, cover page). Write in Markdown,
then render:

```text
python scripts/export_docx.py draft.md --template 学院模板.docx --references-csv citations.csv --title "论文题目" --out 提交版.docx
python scripts/check.py 提交版.docx --type course --citations-csv citations.csv
```

- The template keeps its page size, margins, headers/footers and styles; the
  converter appends the content and reuses the template's own styles
  (`标题 1`, `List Bullet`, `Table Grid`, with English fallbacks).
- `--references-csv` renders the 参考文献 list in 顺序编码制 from `citations.csv`
  (`type` column: J/M/C/D/S/P/N/EB-OL). Missing fields become visible
  placeholders such as ［缺出版地］ instead of a silent guess. `--references-mode
  auto` replaces an existing 参考文献 section rather than duplicating it;
  `append` always adds a section; `skip` ignores the CSV.
- Run `check.py` on the exported `.docx`, not only on the Markdown. It flattens
  headings, paragraphs and tables and re-runs every check, because a template can
  introduce or swallow content (leftover paragraphs, a table that lost a column).
- The `.docx` is a rendering, not evidence. Re-export after every Markdown edit;
  never hand-edit the docx and call the step done. If the two disagree, the
  Markdown that passed `check.py` is the manuscript and the docx is regenerated.

## Resource Timing Rules

Before research:

- topic or problem,
- target discipline,
- desired scope,
- available access,
- preferred output.

Before idea evaluation:

- idea statement,
- proposed method,
- expected contribution,
- data and compute,
- team and weekly time.

Before structure planning:

- core contribution,
- challenges,
- modules,
- evidence available for each claim.

Before drafting:

- the advantage the paper actually wins on and the results that carry it,
- notes,
- results,
- figures,
- datasets,
- verified references,
- target venue,
- language and format,
- prohibited changes,
- the narrative stance written as a constraint, not a later cleanup: the main
  line in one sentence, the claim boundary, the self-weakening phrases that are
  banned, and the numbers that must point back to `citations.csv`,
- the AI-tone bans that apply while drafting (`翻案腔` like "不是…而是…",
  colon signposts like "核心是：", ordinal headings, em-dash reveals) — say them
  in the handoff, do not plan to scrub them afterwards.

Before data analysis:

- raw data and how it was collected,
- design, groups, and sample size,
- software and packages available,
- reporting requirements (p values, effect sizes, confidence intervals, significant figures).

Before review:

- full draft,
- venue or journal,
- deadline,
- prior reviews,
- target evaluation criteria.

Before AI-tone cleanup:

- finished draft,
- frozen structure and terminology,
- verified evidence and citations,
- explicit list of content that must remain unchanged.

Before rebuttal:

- reviewer comments,
- current manuscript,
- new evidence or experiments,
- constraints on what can be changed.

Before final submission:

- course or venue template and file-naming rules,
- citation style and reference list (GB/T 7714 for Chinese outlets),
- AI-use disclosure requirements,
- similarity-check rules,
- author and contribution statement, if required.

## Quality Rules

1. Never invent a skill that is not installed.
2. Never invent citations, results, mechanisms, or data.
3. Do not ask for the same resource twice.
4. Do not recommend every skill in one chain.
5. Do not recommend `academic-pipeline` and then manually repeat its internal stages.
6. Do not use `paper-polish` to fix structural or evidentiary problems.
7. Do not use two review skills at the same time.
8. In `plan` mode write nothing and start no downstream skill that changes files. In `execute` mode do not begin before the step plan is approved, except one action the user named in this message (one sentence, one figure, one format fix): that request is the approval, and the action still appears in the plan and the report (`references/execution-protocol.md`, "Budget").
9. Do not use `lieflat-less-ai-tone` to change structure, claims, evidence, citations, numbers, or unmatched text.
10. Treat `lieflat-less-ai-tone` as a final whitelist-based cleanup, not a general-purpose rewrite.
11. Do not use `anti-defensive-writing` to hide a load-bearing unfavorable result, or to change numbers, results, citations, or methods. Framing is negotiable; data are not.
12. Match chain length to the task. A course paper under 6000 words with no new empirical contribution starts from the light chain in playbook 5 (`paper-writer` → `paper-polish` → citation check); escalate only when the brief demands its own literature review or the paper carries a real contribution.
13. Do not write an AI-use disclosure that misstates what was done, and do not help a user hide AI involvement where disclosure is required.
14. Do not claim GB/T 7714 output from a formatter that does not support it. Build the list against `references/gbt7714.md` and have the user check it against the course template.
15. In `execute` mode run only the approved step plan; adding, reordering, or dropping a step needs a fresh approval.
16. After each executed step, report the artifact path, what changed, and the verification actually run. A step is not complete because the output looks plausible.
17. At a decision point offer at most three options with cost, benefit, and risk plus a recommendation (`references/execution-protocol.md`, "Decision points"); do not decide for the user when the choice changes the argument, scope, data, or files.
18. Back up an existing user file before overwriting it, and never delete one (`status.py backup`; `references/execution-protocol.md`, "File safety").
19. Do not report a step complete unless the gate for its artifact passed, and report that gate: text deliverables (`.md`, `.docx`) need `scripts/check.py` exit 0, and other artifacts use the gate for their type in "Deterministic Checks".
20. Treat `citations.csv` as the only source of citations: never cite an id that is not in it, never list an entry that lacks the identifiers its type requires (`references/citation-contract.md`, section 2), and never write a citation whose `verified_by` is empty. If writing would start without that file, stop and build it from the user's own sources; do not invent entries to fill the gap.
21. Fill that table only from user-supplied sources or from a verification action that resolved each entry; never from memory or from a plausible-looking format. After `verify_refs.py`, correct or delete every `MISMATCH`/`UNREACHABLE`/`NO_ID` row and re-run it before claiming the step is complete.
22. Run `scripts/preflight.py` for the chain before asking for approval. If a skill is missing from every root, substitute from the degradation order in `references/skill-catalog.md`, state the loss, and never skip the step silently or describe the substitute as equivalent.
23. Keep `paperflow/state.json` for any job with more than one step or one that may resume later: `status.py init` once, `start` before a step, `done`/`fail` after it with the real artifact path and the gate that actually ran. `paperflow/runlog.md` is append-only; never rewrite it. A resumed session reads `status.py show` instead of asking the user to retell the work.
24. When the submission must be Word, export with `scripts/export_docx.py` and run `check.py` on the exported `.docx` ("Word Delivery"). A Markdown draft that passes is not a delivered assignment: never report the step done on the `.md` alone, and never hand-edit the `.docx` as the fix.
25. Say which scenario you diagnosed and what evidence produced it before proposing a chain, and give the correction sentence. A correction is a re-diagnosis, not a negotiation: ask at most one question, keep every artifact already produced, log `路由改判`, and never argue the user back into the first scenario.
26. Take literature in this order: metadata (`search_meta.py`) → holdings (`opac_search.py`) → full text by the user's own login. Never claim to have searched a database you cannot reach, and never present an entry point as a search you performed.
27. Never authenticate as the user, never solve a captcha, never bypass a paywall, and never bulk-download from a database. Supply the entry point and the search terms; per-article reading and download stay manual and must respect the database license.
28. An imported or exported reference is unverified metadata. It may enter `citations.csv` with `verified_by` empty, but it may not enter the body until `verify_refs.py` returns a resolvable record and a human fills `verified_by`.
29. Defensive writing and AI tone are generation constraints, not a cleanup pass. Every writing handoff carries the main line in one sentence, the claim boundary, the banned self-weakening phrases, the `翻案腔`/colon-signpost bans, and the rule that each number points back to `citations.csv`. A draft written without those constraints and only scrubbed by `lieflat-less-ai-tone` afterwards does not pass the language gate: run the writing step again with the constraints attached, and use the cleanup only for what the draft still missed.

30. **Before the final deliverable leaves the room, run `scripts/usage_report.py`
    and show the table.** It lists every applicable skill, what it is there to
    catch, and whether it appears in `paperflow/runlog.md`. You must then tell the
    user, in one message: which skills ran, which did not, and why the missing
    ones were not needed this time. A user who never sees this list cannot tell a
    finished paper from a paper that skipped its review. Exporting without this
    report is a violation even when every other gate passes.

31. **Define the terms before writing, and keep the numbers tied to the table.**
    `status.py init` writes `术语表.md` (`term | definition | banned near-synonyms`).
    Fill it before the first paragraph, then use one name per thing in the body,
    the tables, the figure captions and the text inside the figures: two names for
    one concept is the defect a reviewer reads as carelessness, and its author
    cannot see it. `check.py` reports a banned synonym as `[term]` and reports a
    body number that disagrees with a single-valued `参数 | 设定值` table row as
    `[number]`. Both rules are deliberately narrow. When a banned word appears
    legitimately inside a cited title, delete that word from the glossary instead of
    editing the citation, and never widen the rule until it flags ordinary prose.

32. **Never install a missing skill without saying so.** This skill does not
    bundle its partners (`paper-writer`, `grilling`, `paper-polish`,
    `academic-paper-reviewer`, `figure-designer`, …). When `preflight.py` reports
    them missing, show the user: which ones, what each is for, where it can be
    obtained (`references/skill-dependencies.json`), and what is lost by
    substituting. Then ask, once, whether to install them. Installing third-party
    code is the user's decision and needs the host's security scan
    (`skill-inspector`) first; after installing, run `preflight.py` again and
    report the new state. An agent that silently substitutes, or silently
    installs, has broken the run's audit trail.


## Reference Files

- `references/execution-protocol.md`: modes, approval gate, step loop, reporting format, decision-point format, file safety, and failure handling.
- `references/routing-checklist.md`: the three probes, the misjudgment table, and the correction protocol for a wrong scenario diagnosis.
- `references/citation-contract.md`: the `citations.csv` schema, the four hard citation rules, how to verify a DOI or URL, and the GB/T 7714 field mapping.
- `references/institution-setup.md`: the one-time profile (school, department, discipline, OPAC base, remote-access mode, databases) written to the untracked `institution.local.md`; nothing about a specific school ships with the skill.
- `references/skill-dependencies.md`: why the partner skills are not bundled, the three kinds of source, and the install-then-recheck order (`skill-inspector` first).
- `references/skill-dependencies.json`: the machine-readable manifest `preflight.py --explain` reads (role, install source, cost of doing without).
- `references/library-access.md`: the three literature stages, how to recognise an OPAC system, the four kinds of off-campus access, export formats, compliance red lines, and the failure table.
- `scripts/search_meta.py`: OpenAlex / Crossref metadata search and DOI lookup; prints candidates with DOI, year, venue, citations.
- `scripts/opac_search.py`: library catalogue search (title / author / keyword / ISBN / call number / publisher) against the configured OPAC, with holdings URLs and thesis records.
- `scripts/import_refs.py`: RIS / BibTeX / CSL-JSON → `citations.csv`, auto-id, DOI and title+year dedupe, GB/T type code, `verified_by` left empty.
- `scripts/check.py`: deterministic draft checks (citations against the reference list and the `citations.csv` contract, figure references, fences, placeholders, banned phrases, sections, length).
- `scripts/verify_refs.py`: networked authenticity check for `citations.csv` (DOI resolution, field comparison). Exit codes: 0 pass, 1 mismatch/unreachable/no-id, 2 input error or nothing verified, 3 offline `UNCHECKED` without `--allow-unchecked`.
- `scripts/usage_report.py` — 技能账本：哪些跑了、哪些没跑、各自负责挡住什么；导出前必须展示。
- `scripts/preflight.py`: checks that every skill in a chain is installed and that the local scripts exist; exit 1 with the missing names.
- `scripts/status.py`: `paperflow/state.json` (stage, chain, per-step sha256, decisions), append-only `paperflow/runlog.md`, and `paperflow/backups/<name>.<NNN>.bak` versioned backups. `status.py show` tells a resumed session where the job stands. `status.py init` also writes the `术语表.md` template.
- `scripts/export_docx.py`: Markdown → `.docx` with a school template (margins, header, styles kept), GB/T 7714 参考文献 from `citations.csv`, and `_runtime.py` for the python-docx fallback. Needs `python-docx`: it re-executes under `PAPERFLOW_PYTHON` or the DSH bundled interpreter when the current one lacks it; otherwise install with `pip install python-docx`.
- `scripts/lint_docs.py`: consistency lint for this skill's own documentation (fences, rule numbering, per-playbook `Minimal:` lines, the verbatim correction sentence, referenced paths); run it after editing the skill.
- `references/skill-catalog.md`: local skills, functions, inputs, outputs, and selection conditions.
- `references/workflow-playbooks.md`: complete chains for common paper and research scenarios.
- `references/prompt-library.md`: handoff fields for every relevant local skill, and the prompt templates used in `plan` mode.
- `references/example-course-report.md`: full worked example using a course research report.
- `references/student-roadmap.md`: 大一 to 大四 capability and output roadmap, with the skills and gates that fit each year.
- `references/gbt7714.md`: GB/T 7714-2015 reference-list rules for Chinese course papers and theses.
