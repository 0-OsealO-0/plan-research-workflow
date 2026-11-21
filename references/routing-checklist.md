# Routing Checklist

Routing is the highest-cost decision in this skill: a wrong scenario sends the
whole chain to the wrong skills, and the user pays for it in hours. Diagnose out
loud, with evidence, and make the correction cheap.

## Three probes, in this order

1. **What is the deliverable?** A graded Word assignment / a lab report / a 申报书
   or 开题报告 / a submission to a venue / a rebuttal letter / nothing yet, only an
   idea. The deliverable decides the playbook more often than the topic does.
2. **Whose data is in it?** The user's own measurements or experiments, someone
   else's literature, or neither (a pure argument paper). No data and no new claim
   means a course-report chain, not a research-paper chain.
3. **Who judges it, and by what?** A course rubric and page limit, peer reviewers,
   a 结题验收 panel, or a deadline that is hours away. A <24h deadline removes
   research and review from the chain no matter how good they would be.

If a probe cannot be answered from the conversation or the files, ask one question
about that probe; do not ask all three at once.

## Misjudgment table

| Symptom in the user's words | Common wrong route | Correct route | Why it is wrong |
|---|---|---|---|
| 老师布置的论文 / 3000 字 / 有评分标准 | full research paper (deep-research → academic-paper) | playbook 5 default chain (`paper-writer` → `paper-polish` → citation check) | no new contribution; the rubric rewards coverage and clarity, not novelty |
| 实验报告 / 有原理和步骤 | course report | playbook 9 (data → `statistical-analysis` → `paper-writer` → figure) | a lab report is judged on data handling and uncertainty, not on argument |
| 大创 / SRTP / 开题 | research paper | playbook 10 (proposal) | judges ask feasibility, timeline, and preliminary data, not results |
| 文献综述 (course) | `sr-screener` + PRISMA | playbook 5 with a scoped read | PRISMA is for a systematic review protocol, not a graded summary |
| 我已经有数据了 | start with `deep-research` | `statistical-analysis` / playbook 9 first | the numbers decide what the paper can claim; literature comes after |
| 只有想法 / 有个方向 | write a draft | `idea-evaluator` first | an unevaluated idea produces a confident but unpublishable draft |
| 收到审稿意见 | polish the paper | playbook 7 (`rebuttal-guidance` → `anti-defensive-writing` → revision) | every comment needs a response, not just smoother prose |
| 明天交 | full chain | playbook 6 (polish → pre-submission-reviewer → repair) | adding steps this late lowers quality |
| 要交 Word 模板 | deliver the Markdown | last step `export_docx.py` + `check.py` on the `.docx` | an unexported `.md` cannot be submitted |
| 帮我看看这段写得怎么样 | full diagnosis + plan | one-skill answer (`paper-polish` or `anti-defensive-writing`) | scale the answer, do not dress a ten-minute task as a semester plan |

## Correction protocol

1. The diagnosis line names the scenario **and the evidence**: 「判定：课程报告（依据：你提到『老师评分』『3000 字』）。」
2. Record it: `python scripts/status.py init --type <类型> --scenario "<场景>"`, so a
   later session can see which scenario the chain was built for.
3. Attach the correction sentence verbatim: 「如果你不是这个场景，回一句『不是，我是 Y』，我重排链条，已产出的文件不动。」
4. When the user corrects it: ask **one** clarifying question only if the new
   scenario is still ambiguous; otherwise re-diagnose immediately. Do not ask the
   user to re-explain what they already said.
5. Keep every artifact already produced. Re-label it in the new chain (a draft
   written for the wrong playbook is still a draft) instead of deleting it.
6. Append a `路由改判` line to the run log with the old and new scenario, so a later
   session does not re-litigate it:

   ```text
   python scripts/status.py note "路由改判：课程报告 → 开题申报书（用户说这是大创申报）"
   ```
7. Never argue the user back into the first diagnosis, and never re-ask the same
   ambiguity twice.

## Signals that the diagnosis is still weak

- The user's first message names only a topic and a deadline.
- The user says "论文" but also mentions 课程 / 作业 / 学分.
- The user has files already (a draft, data, a template) and did not mention them.
- Two rows of Routing Rules both fit, and the difference changes cost by an order
  of magnitude.

In these cases say the diagnosis is provisional, pick the cheaper chain, and let
the first step's output settle it.
