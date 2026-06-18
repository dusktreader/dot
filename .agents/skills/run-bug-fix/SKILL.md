---
name: run-bug-fix
description: Orchestrates the full bug fix workflow: investigate, plan, execute, and review.
---

# Run Bug Fix Skill

Coordinate the full bug fix workflow: investigation, implementation planning, execution, and review. All
artifacts are stored under `.agents/work/{YYYYMMDD}-{HHmmss}--{project-name}/`.


## When to use

Use this skill for a thorough, well-documented bug fix — when the root cause is unknown or
needs confirmation, and when the fix warrants a full plan-and-review cycle.

This is a standalone skill triggered directly by humans.

Do not use when:
- Speed is critical and the fix is obvious → use `run-hotfix` instead
- The bug is a gap in an already-implemented feature → use `run-fix` instead
- The PR is already open and the fix is in response to a review comment → use `review-pr`

Compared to `run-hotfix`: `run-bug-fix` includes investigation, a full implementation plan,
and a plan review. `run-hotfix` skips those and goes straight to execution.


## Prerequisites

Your prompt must include:

- Bug description
- Reproduction steps (if known)

If not provided, ask before proceeding. Do not guess.


## Project directory

Derive `{project-name}` from the bug description, prefixed with `fix-`
(e.g. `fix-null-pointer-on-login`). Create `.agents/work/{YYYYMMDD}-{HHmmss}--{project-name}/`. All
artifacts for this project are stored there.

| Artifact                                  | Description                                                                                |
| ----------------------------------------- | ------------------------------------------------------------------------------------------ |
| `bug-report.md`                           | Investigation findings and confirmed root cause                                            |
| `implementation-plan.md`                  | Fix plan                                                                                   |
| `implementation-review--{N}.md`           | Implementation plan review (N = zero-padded 2 digits: 01, 02, ...)                         |
| `implementation-journal.md`               | Execution journal                                                                          |
| `execution-review--{scope-id}--{N}.md`    | Execution review (scope-id = task-NN or whole-plan; N = zero-padded 2 digits: 01, 02, ...) |


## Process


### 1. Investigate

Dispatch an `engineer-investigator` subagent with the `investigate-codebase` skill. Direct the
investigator to determine: root cause, affected code paths, and blast radius.

Synthesize the investigator's findings into `bug-report.md`. Read
`.agents/artifacts/bug-report/description.md` for the canonical section definitions, and render
`.agents/artifacts/bug-report/template.md.j2` to produce the initial file. Replace all dummy
content — every line drawn from the retro encabulator — with real content for this bug. The rendered
file must contain no placeholder text when submitted.

**Stop.** Present the bug report to the human. Confirm the root cause and scope before proceeding. If the
root cause is unclear, dispatch the investigator again with a more targeted question.


### 2. Plan

Dispatch an `engineer-planner` subagent with the `create-implementation-plan` skill, passing the bug
report path as the planning input in place of a design plan.

Then dispatch an `architect-reviewer` subagent with the `review-implementation-plan` skill, the plan
path, and iteration `01`.

**Stop.** Present the implementation plan and its review to the human. Apply trivial findings directly.
Discuss significant and critical findings. Re-dispatch an `architect-reviewer` with
`review-implementation-plan` at N+1 until the plan is approved.


### 3. Execute

Dispatch an `engineer-executor` subagent with the `execute-implementation-plan` skill and the plan path.

Then dispatch an `engineer-reviewer` subagent with the `review-implementation-execution` skill, the
journal path, scope `whole-plan`, and iteration `01`.

**Stop.** Present the execution review to the human. Dispatch an `engineer-executor` to fix Critical and
Significant findings, then re-dispatch an `engineer-reviewer` with `review-implementation-execution` at
N+1 until the execution is approved.


### 4. Report

Report completion to the human with the project directory path and the final status of each artifact.
