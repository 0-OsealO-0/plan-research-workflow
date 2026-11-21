# Execution Protocol

The skill is an orchestrator and an executor: after the user approves the step
plan, it runs the named skills itself instead of printing prompts to copy.

## Modes

| Mode | Trigger | Behavior |
|---|---|---|
| `execute` (default) | the user asks for the work itself | diagnose, propose the step plan, wait for one approval, then run one step per message and report |
| `plan` | "只给计划", "先别执行", "不要改文件", "我只想看思路", "帮我填表/准备答辩时先别动文件", or the task is advice only | read-only: analyze, return the plan and, if useful, the prompts; write nothing |

State the mode in the first line and how to switch:

```text
模式：execute（说“只给计划”可冻结为计划模式）
```

Switching:

- `plan` -> `execute`: the user says 开始执行、按方案做、可以动手.
- `execute` -> `plan`: the user says 停、只给计划、别改文件.
- Ambiguous instruction: stay in the current mode and say which one you are in.

## The loop

0. **Diagnose** from what is already known: conversation, files on disk, the
   stage table in SKILL.md. Do not ask for what can be read. Name the scenario and
   the evidence in one line, and attach the correction sentence from
   `routing-checklist.md` before any chain is proposed.
1. **Preflight the chain**: run `scripts/preflight.py --require <skills>` (rule 22).
   If anything is missing, substitute per the degradation order and put the loss
   in the plan before approval.
2. **Propose the step plan**: the Skill Chain table with purpose, input,
   deliverable, and gate per step. Include the file paths that will be written.
   Start from the playbook's minimal chain and justify each extra step.
3. **Ask for approval once**: "批准后我从第 1 步开始；要改步骤直接说。"
4. **Run one step per message** after approval: load the skill with the `skill`
   tool, follow it with the step's parameters, then report.
   For a submission that must be Word, the step ends with the export, not with
   the Markdown (rule 24): `export_docx.py … --template <学院模板.docx>` then
   `check.py <提交版>.docx --type … --citations-csv citations.csv`. The report
   names the `.docx` as the artifact and carries the docx exit code.
5. **Report** in this shape:

   ```text
   步骤 2/5 · paper-writer · 产物：draft_v1.md
   改动：新增 §2 方法段（第 45–88 行）
   验证：重读 §2，引用 [3][7] 与文献表一致；字数 1820
   自检：check.py exit 0（0 CRITICAL / 1 WARN）
   状态：paperflow/state.json 已更新（步骤 2 done，sha256 已记录）
   门：通过（叙述门待第 3 步）
   下一步：3/5 anti-defensive-writing
   ```

6. **Stop** at a decision point, missing input, or failed gate.
7. **Never** call a step complete when its gate failed. Say it failed, name the
   missing item, and offer the repair.

## Decision points

Ask when the choice changes the paper's argument, main line, scope, target
venue or format, data treatment, cost, or which files are written.

Format:

```text
需要你拍板：主结果选哪个？
1. 用表 2（A 数据集）作主结果 —— 成本低，但只能主张 A 上的优势
2. 用表 3（跨数据集）—— 更有说服力，需要补 2 天实验
我的建议：1，因为现在没有跨数据集的完整跑批。
回复 1/2/3，或直接给你的条件。
```

Rules:

- At most three options.
- Each option states cost, what it buys, and the main risk.
- Always give a recommendation with one line of reason.
- Never offer an option that violates the quality rules (deleting a negative
  result, overclaiming, hiding AI use, faking a citation).
- Accept a conditional override ("用 2，但保留原表作为附录").

## When to stop instead of proceeding

- Missing data, draft, template, or review comments that the step needs.
- A requirement is ambiguous in a way that changes scope.
- The next action would overwrite a user file without a backup.
- The downstream skill is missing from this agent's catalog.
- The previous step's gate failed.
- The step would spend more than roughly ten minutes or hundreds of tool calls;
  ask before starting.

## File safety

- `plan` mode writes nothing, including no backup copies.
- `execute` mode writes only paths named in the approved step plan.
- Before overwriting an existing user file, run
  `scripts/status.py backup <file>`: it writes `paperflow/backups/<name>.<NNN>.bak`
  without overwriting an earlier backup, and you say where it is. The plain
  `<name>.bak-<YYYYMMDD-HHMM>` copy is the fallback when the project has no
  `paperflow/` state.
- Never delete a file. Never edit outside the target paths.
- After writing, re-read the changed region and report line numbers.
- After writing, run `scripts/check.py` on the changed file; a non-zero exit
  blocks calling the step complete. Report the exit code and the failing items.
- If the user's draft is the only copy and no backup exists, create one first
  and say so, even inside an approved step.
- A writing step may use existing citation ids but may not create a new one.
  Adding a reference is its own step: append the row to `citations.csv`, run
  `scripts/verify_refs.py --only <id>`, then cite it. This keeps fabrication
  out of the prose by construction.

## Project state and run log

Any job with more than one step, or that may span sessions, keeps its state in
the paper's directory:

```text
python scripts/status.py init   --type course --title "..." --scenario "课程报告"
```

`init` also writes `术语表.md`. Before the first paragraph, replace the example rows
with the terms this paper actually uses, plus the near-synonyms it must not use.
Two names for one concept is the defect the author cannot see; `check.py` reports a
banned synonym as `[term]`, quoting the term the glossary chose.

```text
python scripts/status.py start  --skill paper-writer --deliverable draft_v1.md
python scripts/status.py done   --id 1 --artifact draft_v1.md --gate "check.py exit 0"
python scripts/status.py fail   --id 2 --note "数据不足，等待补实验"
python scripts/status.py decide --question "主线选哪个" --choice "A" --reason "数据更强"
python scripts/status.py show                                        # new session: where am I
python scripts/status.py note   "路由改判：课程报告 → 大创申报"       # free-text run-log line
python scripts/status.py backup 提交版.docx                          # versioned backup before an overwrite
```

- `paperflow/state.json` records stage, mode, chain, per-step status, artifact
  path and sha256, and decisions. `paperflow/runlog.md` is append-only; never
  rewrite or truncate it.
- `show` compares each recorded sha256 with the file on disk. `[已被改动]` means
  the file changed after that step, so the step's gate no longer holds — re-run
  the gate or the step. `[产物缺失]` means the file is gone.
- A new session starts with `show`. Do not ask the user to retell what the state
  file already records.
- `plan` mode creates no state file; the printed plan is the record.

## Handoff to downstream skills

The entries in `prompt-library.md` are handoff specifications, not text for the
user to copy. Pass those fields as a parameter block when invoking the skill.

- Load the skill with the `skill` tool before following it.
- Include the paths, the target venue or course, the evidence discipline, and
  the "must not change" list in the handoff.
- Any writing or revision step carries the path to `citations.csv` and the rule
  that only verified rows may be cited; a writing step with citations but no
  table stops before prose (`citation-contract.md`).
- Do not summarize a skill's instructions from memory; load it.

If a skill is unavailable:

1. Say which skill is missing and where it would have to be installed.
2. Name the next-best installed skill and what is lost by substituting.
3. Continue with the substitute only if the loss is acceptable; otherwise stop.

## Failure handling

- The skill's output fails a gate (unsupported claim, missing data, invented
  citation, wrong statistics): do not accept it. Re-run once with an explicit
  constraint list, or fix the specific sentences and report the change.
- Twice-failed step: stop and present the failure with the exact evidence.
- Never launder a failure into a success by rewriting the gate.

## Budget

- One step per message after approval. Inside one step you may take up to three
  trivial actions (write, re-read, re-check) before reporting; never merge two
  *steps* into one message.
- A trivial single action (one paragraph, one figure, one format fix) may run
  without a separate approval round when the user named it in this message: that
  request is the approval (rule 8), and the action still appears in the plan and
  in the report.
- For multi-agent skills (`deep-research`, `academic-paper`,
  `academic-paper-reviewer`), say the expected cost and get confirmation before
  starting.

## Progress log

One line per completed step, in order, so the user can audit the run:

```text
步骤 1/5 · tech-paper-template · 产物：outline.md · 门：通过
步骤 2/5 · paper-writer · 产物：draft_v1.md · 门：部分（引用未核）
```
