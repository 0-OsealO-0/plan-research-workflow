# Workflow Playbooks

Use only the playbook matching the user's current situation.

Each chain is an execution order, not a list of prompts to paste. In `execute`
mode run the steps one at a time, report after each, and stop at the playbook's
gates; in `plan` mode print the chain and the prompts.

## Minimum deliverable versions

Start from the minimal chain. Escalate only for a stated reason, and say what the
extra steps buy.

| Playbook | 最小可交付（3 步左右） | 何时才升级到完整链 |
|---|---|---|
| 1 Technical paper from zero | `tech-paper-template` → `paper-writer` → `paper-polish` | 有真实贡献、要投稿、需要评审循环 |
| 2 Benchmark / evaluation | `benchmark-paper-template` → `paper-writer` → `pre-submission-reviewer` | 要做数据集构建与多基线评测 |
| 3 Existing draft | `paper-polish` → `pre-submission-reviewer` → 修复 | 需要重写结构或补实验 |
| 4 Systematic review | `sr-screener` → `paper-writer` → `paper-polish` | 需要 meta-analysis 与 PRISMA 产物 |
| 5 Course report | `grilling`（攻提纲）→ `paper-writer` → `paper-polish` → citation-check | 综述型作业、要求文献覆盖 |
| 6 Deadline review | `paper-polish` → `pre-submission-reviewer` → 修复 | 24 小时内这就是完整链，不要再加 |
| 7 Rebuttal / revision | `rebuttal-guidance` → `anti-defensive-writing` → 修订 | 需要重跑评审与多轮 rebuttal |
| 8 Full managed project | 不用它；退回 playbook 1/3 的最小链 | 项目级工作、需要审计产物 |
| 9 Lab report | `paper-writer` → `paper-polish` → `check.py` | 有原始数据需要统计与作图 |
| 10 Proposal | `tech-paper-template` → 写申报书 → `pre-submission-reviewer` | 要 scoped 文献扫描与可行性评估 |

Rule: ask whether the minimal chain delivers the required artifact. Only escalate
when the contribution, the review cycle, or the data complexity demands it; name
the reason and the extra cost before adding steps.

One step is never optional: **red-team review after the first draft and before
language cleanup** (`grilling` for the claim chain, `academic-paper-reviewer` when
a full review report is cheaper than an interview). A draft nobody attacked is a
draft whose claims were checked only by the person who wrote them.

The table above is authoritative. If it and a playbook's `**Minimal:**` line
disagree, the playbook line is the bug: fix it in the same edit.

In `execute` mode a chain that spans several steps or sessions also keeps
`paperflow/state.json`; `status.py show` at the start of a resumed session is the
first command, not a question to the user (see `execution-protocol.md`,
"Project state and run log").

If the assignment is submitted in Word (course papers, lab reports, 申报书),
every playbook's last step is the export: `export_docx.py --template <学院模板>`
then `check.py` on the `.docx` (see SKILL.md, "Word Delivery"). The `.md` is the
working manuscript; the `.docx` is the deliverable.

Any chain that needs literature starts with `search_meta.py` (metadata + DOI) and,
when a specific book or thesis matters, `opac_search.py` (SEU holdings); references
exported from CNKI / 万方 / IEEE enter through `import_refs.py` and must pass
`verify_refs.py` before the first citation (see SKILL.md, "Literature Acquisition",
and `references/library-access.md`).

## 1. Technical Paper from Zero

**Minimal:** `tech-paper-template` → `paper-writer` → `paper-polish` → `check.py`.

### Chain

```text
deep-research
  -> idea-evaluator
  -> tech-paper-template
  -> anti-defensive-writing
  -> intro-drafter
  -> paper-writer
  -> figure-designer
  -> drawio-reconstruction
  -> research-paper-writing
  -> anti-defensive-writing (second pass on the full draft)
  -> paper-polish
  -> lieflat-less-ai-tone
  -> academic-paper-reviewer
  -> pre-submission-reviewer
```

### Resources by Stage

Before `deep-research`:

- broad topic,
- discipline,
- scope,
- expected paper type.

Before `idea-evaluator`:

- specific idea,
- method,
- expected contribution,
- data, compute, skills, team, and time.

Before `tech-paper-template`:

- validated idea,
- core challenge,
- intended modules,
- available evidence.

Before `anti-defensive-writing`:

- the advantage the paper actually wins on,
- the results that carry it, with numbers,
- page or word limit,
- venue and its evaluation culture.

Before `intro-drafter`:

- logic skeleton,
- running example,
- target venue,
- citation style.

Before `paper-writer`:

- notes,
- results,
- methods,
- figures,
- datasets,
- verified references.

Before reviewers:

- full manuscript,
- target venue,
- deadline,
- figure files,
- known risks.

Before `lieflat-less-ai-tone`:

- complete manuscript,
- frozen structure and terminology,
- verified evidence and citations,
- confirmation that only AI-tone cleanup is allowed.

### Gates

- Do not evaluate an idea before the research direction is clear.
- Do not draft before the logical skeleton is stable.
- Do not polish before evidence and structure are correct.
- Run `lieflat-less-ai-tone` only after substantive editing and polishing are complete.
- Do not review before the manuscript is internally consistent.

## 2. Benchmark or Evaluation Paper

**Minimal:** `benchmark-paper-template` → `paper-writer` → `pre-submission-reviewer`.

### Chain

```text
deep-research
  -> idea-evaluator
  -> benchmark-paper-template
  -> paper-writer
  -> figure-designer
  -> drawio-reconstruction
  -> paper-polish
  -> lieflat-less-ai-tone
  -> academic-paper-reviewer
  -> pre-submission-reviewer
```

### Required Input

Before `benchmark-paper-template`:

- research gap,
- target capability or evaluation dimension,
- construction pipeline,
- annotation or quality-control plan,
- evaluation framework,
- experimental plan or results.

Before `paper-writer`:

- benchmark design,
- construction details,
- evaluation metrics,
- empirical findings,
- limitations.

### Gates

- The gap must be more than "no dataset exists."
- The construction pipeline must be reproducible.
- Evaluation must measure what the paper claims.
- Findings must be more than a leaderboard.

## 3. Existing ML, CV, or NLP Draft

**Minimal:** `paper-polish` → `pre-submission-reviewer` → 按问题清单修复.

### Chain

```text
research-paper-writing
  -> anti-defensive-writing
  -> paper-polish
  -> lieflat-less-ai-tone
  -> academic-paper-reviewer
  -> academic-paper revision
  -> pre-submission-reviewer
```

### Required Input

- existing manuscript,
- target venue,
- experiment tables and figures,
- claim-evidence map if available,
- reviewer comments if this is a revision.

### Gates

- Every major Abstract and Introduction claim must match experiments.
- One paragraph should carry one main message.
- Figures and tables must be readable at venue scale.
- Structural problems must be fixed before language polishing.

## 4. Systematic Review or Meta-Analysis

**Minimal:** `sr-screener` → `paper-writer` → `paper-polish`.

### Chain

```text
deep-research
  -> sr-screener
  -> academic-paper
  -> academic-paper-reviewer
```

### Required Input

Before `deep-research`:

- review topic,
- review type,
- research questions,
- inclusion and exclusion criteria,
- databases and access.

Before `sr-screener`:

- screening protocol,
- record exports,
- duplicated-record handling,
- reviewer roles,
- output directory.

Before `academic-paper`:

- PRISMA counts,
- screening log,
- included corpus,
- synthesis results,
- target journal and reporting guideline.

### Gates

- Freeze eligibility rules before screening.
- Use ordered exclusion reasons.
- Resolve conflicts explicitly.
- Keep counts reproducible.
- Verify every citation before writing.

## 5. Course Report, Humanities, or Social Science

**Minimal:** `grilling`（先攻提纲）→ `paper-writer` → `paper-polish` → `academic-paper` citation-check.

### Default chain (course paper, no new empirical contribution)

Under roughly 6000 words, with no independent source discovery:

```text
paper-writer (outline only, with the claims written out one per line)
  -> grilling round 1 (attack the outline, before a single paragraph exists)
  -> paper-writer (draft, following the claims that survived)
  -> grilling round 2 (short pass: only the sentences added after round 1)
  -> paper-polish (repair the prose the review exposed)
  -> lieflat-less-ai-tone
  -> citation check (academic-paper citation-check, or manual)
```

Red team before drafting, not after. Attacking an outline costs one line per
claim; attacking a finished draft costs a section per claim, and the sections most
likely to die are the ones the figures were already drawn for. Round 1 asks: is
this claim falsifiable, which alternative is still standing, which parameter has
no provenance, is any citation used against its own source. The outline is revised
until those answers hold, and only then does prose start.

Round 2 is deliberately cheap, about ten minutes: the draft contains sentences the
outline did not, and those can smuggle in new claims. Scan only what is new.

Both rounds are not a formality and not skippable. Each hole gets a severity and a
repair (narrow the claim, add the missing exclusion, mark the parameter as
assumption, or cut the sentence). Fix the holes before polishing prose, because
polishing a claim that does not hold only makes it more persuasive and less true.

Escalate to the full chain below only when the brief demands its own literature
review (`deep-research`), the paper carries a real contribution, or several drafts
and a strict citation audit need project-level management (`academic-paper`).

The narrative stance and the AI-tone bans belong in the handoff to `paper-writer`,
not in a later cleanup: pass the main line, the claim boundary, the banned
self-weakening phrases, and the `翻案腔`/colon-signpost bans, and require the
first draft to obey them. `lieflat-less-ai-tone` at the end is a whitelist
scrub for what the draft missed; it is not the mechanism that keeps the draft
honest, and a draft that never received the constraints is re-written, not
scrubbed.

Before drafting, fill `术语表.md` (written by `status.py init`): one term per
line, its definition, and the near-synonyms that must not be used. Two names for
one thing is the defect a reviewer reads as carelessness, and the author cannot
see it, because both names mean the same thing to the author.

### Full chain (research-level course paper)

```text
deep-research
  -> academic-paper
  -> paper-writer (outline) -> grilling (attack the outline)
  -> paper-writer (draft)
  -> grilling (red team) 或 academic-paper-reviewer（要一份成文报告时）
  -> research-paper-writing
  -> paper-polish
  -> lieflat-less-ai-tone
  -> academic-paper citation-check
```

### Required Input

Before research:

- assignment brief,
- required sources,
- grading criteria,
- required length and format.

Before writing:

- source matrix,
- quotations and page references,
- report outline,
- group roles if collaborative,
- the writing constraints package: main line in one sentence, claim boundary,
  banned self-weakening phrases, `翻案腔`/colon/ordinal-heading bans,
- the verified ids in `citations.csv` that the numbers must point back to.

Before finalization:

- complete draft,
- references,
- a polished draft that is ready for final AI-tone cleanup,
- formatting template,
- submission file name rules.

### Gates

- Do not invent empirical evidence.
- Keep policy statements separate from observed outcomes.
- Use one central argument rather than topic stacking.
- Preserve source meaning when shortening quotations.
- Run `lieflat-less-ai-tone` only after the argument, citations, and source wording are frozen.
- Require the cleanup to preserve title hierarchy, paragraph order, quotations, citations, numbers, and unmatched text.

## 6. Deadline Review

**Minimal:** `paper-polish` → `pre-submission-reviewer` → 立即修复; 24 小时内不再加步骤.

### Chain

```text
research-paper-writing
  -> paper-polish
  -> lieflat-less-ai-tone
  -> pre-submission-reviewer
  -> immediate repair
```

### Required Input

- complete draft,
- venue,
- deadline,
- formatting requirements,
- current known issues.

### Gates

- Fix CRITICAL issues first.
- Defer changes that alter the research claim unless evidence exists.
- Verify citations and numbers after all edits.

## 7. Rebuttal and Revision

**Minimal:** `rebuttal-guidance` → `anti-defensive-writing` → 修订正文与回应.

### Chain

```text
rebuttal-guidance
  -> anti-defensive-writing
  -> academic-paper revision
  -> academic-paper rebuttal-audit
  -> academic-paper-reviewer re-review
```

### Required Input

- reviewer comments,
- manuscript,
- new experiments or evidence,
- venue response rules,
- word or time limits.

### Gates

- Answer every concern.
- Distinguish new evidence from explanation.
- Do not attack the reviewer.
- Keep claims consistent with the revised manuscript.

## 8. Full Managed Project

**Minimal:** 无; 退回 playbook 1 或 3 的最小链.

### Chain

```text
academic-pipeline
```

Use `academic-pipeline` only when the user wants one orchestrator to manage research, writing, integrity checks, review, revision, and finalization.

Do not manually repeat all internal pipeline stages.

## 9. Lab Report or Experiment Write-up

**Minimal:** `paper-writer` → `paper-polish` → `scripts/check.py`.

### Chain

```text
exploratory-data-analysis (optional, to profile the data)
  -> statistical-analysis
  -> paper-writer
  -> figure-designer or matplotlib
  -> paper-polish
```

### Required Input

- lab manual and the required report structure,
- raw data and instrument notes,
- design, groups, and sample size,
- error sources and uncertainty budget,
- grading rubric.

### Gates

- State the design before the numbers; a result without a stated design is not interpretable.
- Report uncertainty and significant figures (`uncertainty-and-units` when the course requires GUM-style budgets).
- Separate measurement error, systematic error, and model error.
- Do not import literature claims the experiment did not test.

## 10. 大创 / SRTP / 开题 Proposal

**Minimal:** `tech-paper-template` → 写申报书 → `pre-submission-reviewer`.

### Chain

```text
deep-research (scoped literature scan)
  -> idea-evaluator
  -> tech-paper-template, or academic-paper plan or outline mode
  -> pre-submission-reviewer on the proposal text
```

### Required Input

- call for proposals and review criteria,
- prior work and preliminary data,
- timeline, budget, and team roles,
- supervisor constraints.

### Gates

- The proposal states a question, not a topic.
- Every claimed preliminary result has data behind it.
- The timeline is written in weeks with one deliverable per phase.
- Feasibility is judged against a freshman's real access to data, compute, and lab time.
