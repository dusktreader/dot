# Review Implementation Execution Procedure

Define the independent, evidence-based review of executed work against an approved plan, execution journal, and recorded
deviations.


## Required inputs

The caller must provide:

- Approved plan path and plan type: `task` or `implementation`
- Execution journal path
- Deviation-journal path
- Review artifact path and iteration; use `execution-review--whole-plan--NN.md` for a task plan
- For re-reviews, the prior execution-review artifact
- Worktree and branch context
- Project class and review routing metadata if the caller uses routed profiles

If any input is missing or ambiguous, ask the caller before reviewing. Never substitute another plan revision.


## Reviewer instructions

Start with the diff and execution journal, then inspect the modified files recorded in the journal. Expand context only
as needed. Keep findings compact. Re-review only after a change to acceptance criteria, a new code path, behavior,
interface, data, security, or tests.

Read the approved plan referenced in the execution journal's source-plan section. For task plans, use the flat steps and
acceptance criteria as the baseline; there is no design plan. For implementation plans, read the referenced design plan
when available. Confirm that project commands and relevant standards are available from the plan or documented project
guides. If the information needed to run or assess required checks is missing, record a Critical finding and stop.

For `task-NN` scope, collect files from that implementation-plan task's journal entry. For `whole-plan` scope, collect
files from every journal task entry, including a task plan's single entry or independent sub-task entries. Read each
file directly. Do not rely only on the journal's description.

Run all documented project quality checks, including tests, linter, and type checker where available. Do not invent
commands. If a coverage command is not documented, record `skipped (no project-documented command)` in the verification
evidence. If a quality check fails, stop the review, record the complete failure output, and return `Quality checks
failing. Fix before review.`

Verify every in-scope acceptance criterion independently against the code and evidence. Cross-check the implementor's
journal validation but treat it as a claim, not proof. Record status and evidence for each AC. A Critical finding is
required for an unsatisfied AC, a behavioral code AC with no test, an AC without observable verification evidence, or a
plan with no acceptance criteria. For non-code ACs, appropriate evidence may include rendered output, configuration
inspection, or a documented manual check instead of a test.

Review scope and code quality. Map each changed file to a plan task or step. Unjustified changes to unrelated
subsystems, security-sensitive code, or public APIs are Critical; other unjustified changes are Significant. Assess
correctness, edge cases, error handling, input validation, meaningful test coverage, and code quality. Do not invent
style findings. Each finding must identify concrete evidence, credible impact, and an actionable fix.

For re-reviews, verify every prior finding, marking each fully resolved with `file:line` evidence, partially resolved
with explanation, or unresolved as a Critical finding. Check for new issues introduced by fixes.

Do not modify source code, the approved plan, execution journal, supplied deviation journal, or prior review artifacts.
Complete the `Skills Applied` artifact section with `review-implementation-execution` as procedure guidance, identifying
any other skills actually consulted.


## Review artifact

Read `.agents/artifacts/execution-review/description.md` for canonical section definitions and render
`.agents/artifacts/execution-review/template.md.j2` as the caller-supplied review artifact. Replace all sample content
with review-specific evidence and findings; leave no placeholders. Include the execution journal and approved plan
paths, review scope and iteration, verification results, acceptance-criteria and scope checks, findings, and an
`APPROVED` or `BLOCKED — CHANGES REQUIRED` decision.

Return the review artifact path and outcome to the caller. The caller resolves findings, records implemented post-plan
changes in the supplied deviation journal, and repeats the review after material changes. Do not contact the human,
perform blocker checks, commit, publish, or advance the workflow.
