# Execute Implementation Plan Procedure

Coordinate end-to-end execution of an approved task or implementation plan and record evidence in its execution journal.


## Required inputs

The caller must provide:

- `plan_type`: `implementation` or `task`
- Exact approved plan path
- Project artifact directory
- Execution journal path
- For an implementation plan: its design plan path, when available
- For a bug fix: the `bug-report.md` path or equivalent root-cause context, when available
- Any workflow-specific executor context, such as feature ID, parent epic path, or fix number

If any input is missing or ambiguous, ask the caller before execution. Never substitute another plan revision.


## Execution

The caller prepares the execution journal from `.agents/artifacts/execution-journal/description.md` and
`.agents/artifacts/execution-journal/template.md.j2` before dispatch. Record the approved plan path as the journal's
source plan. For a fix workflow, use its fix-specific deviation journal and leave original project journals unchanged.
For a task plan, use one journal task entry for a coherent task, or one entry per independent sub-task explicitly
identified in the plan.

Dispatch the shared `engineer-executor` role with this procedure, the exact approved plan, the execution journal, and
all supplied context. The executor reads the entire plan and does not modify planning documents. For implementation
plans, missing project commands are a blocker to execution. For task plans, use project commands documented in the plan
and report any missing commands that prevent verification to the caller.

For `implementation` plans, execute every plan task in order. Read the corresponding design plan when available and use
each task's acceptance criteria and steps as the execution baseline. For `task` plans, follow the flat ordered steps and
acceptance criteria; no design plan is required.

For code changes, use test-driven design: write a failing test, confirm failure, implement, and confirm it passes. Run
focused tests, linters, and type checks documented by the plan or project standards. Record completed work, steps taken,
files changed, acceptance-criteria evidence, and objective verification results in the execution journal. Follow the
journal's canonical artifact definition and template.

Complete every task and acceptance criterion before returning. Do not stop at intermediate checkpoints. Stop only when
blocked by information unavailable in the codebase or by a quality gate that requires human input; report the specific
blocker and leave the journal accurately marked incomplete. If the plan is unclear or appears unsafe, report the concern
to the caller before starting execution.

The caller owns deviation recording, final QA, execution review, and workflow transitions. Do not modify the approved
plan, `plan-deviations.md`, or review artifacts. Do not contact the human, commit, publish, or advance the workflow.
