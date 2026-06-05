---
name: run-hotfix
description: Streamlined workflow for urgent fixes. Minimal Stop points, no plan review, lightweight code review.
---

# Run Hotfix Skill

Coordinate an urgent fix with minimal overhead: brief investigation, principal-authored plan, direct
execution, and a single lightweight code review pass. Use this workflow when speed is critical and the
change is well-scoped. All artifacts are stored under `.agents/work/{YYYYMMDD}-{HHmmss}--{project-name}/`.


## Prerequisites

Your prompt must include:

- Bug description or fix objective
- Justification for hotfix (why the full `run-bug-fix` workflow is not appropriate)

If not provided, ask before proceeding. Do not guess.


## Project directory

Derive `{project-name}` from the bug description, prefixed with `hotfix-`
(e.g. `hotfix-auth-token-expiry`). Create `.agents/work/{YYYYMMDD}-{HHmmss}--{project-name}/`. All
artifacts for this project are stored there.

| Artifact                    | Description                                         |
| --------------------------- | --------------------------------------------------- |
| `bug-report.md`             | Brief investigation findings and root cause         |
| `implementation-plan.md`    | Minimal fix plan authored by the principal          |
| `implementation-journal.md` | Execution journal                                   |
| `code-review--01.md`        | Single lightweight review pass                      |


## Process


### 1. Investigate

Dispatch an `engineer-investigator` subagent with the `investigate-codebase` skill. Keep the
investigation focused: root cause and minimal blast radius only.

Synthesize findings into `bug-report.md` using `.agents/templates/bug-report.md` as the template.


### 2. Plan

Write `implementation-plan.md` directly from the bug report. Use
`.agents/templates/implementation-plan.md` as the template. Fill in only what is essential for the
executor to proceed: `Goal`, `Project Commands`, `Project Standards`, and a single execution task with
clear steps and acceptance criteria.

Do not dispatch a planner subagent. Do not dispatch a reviewer. Speed is the priority.


### 3. Execute

Dispatch an `engineer-executor` subagent with the `execute-implementation-plan` skill and the plan path.


### 4. Review

Read the journal to collect the list of modified files. Dispatch an `engineer-reviewer` subagent with the
`review-code` skill, passing the list of modified files and the project directory.

**Stop.** Present the review to the human. Resolve Critical findings before shipping. Significant and
Trivial findings are logged as follow-up work for a proper `run-bug-fix` cycle; they do not block the
hotfix.


### 5. Report

Report completion to the human with the project directory path. Explicitly list any Significant or Trivial
findings that were deferred as follow-up work.
