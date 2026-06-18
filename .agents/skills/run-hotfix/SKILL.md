---
name: run-hotfix
description: Streamlined workflow for urgent fixes. Minimal Stop points, no plan review, lightweight code review.
---

# Run Hotfix Skill

Coordinate an urgent fix with minimal overhead: brief investigation, principal-authored plan, direct
execution, and a single lightweight code review pass. Use this workflow for post-PR fixes — CI
failures, code review findings, or other issues found after a PR is open. All artifacts are stored
under `.agents/work/{YYYYMMDD}-{HHmmss}--{project-name}/`.


## When to use

Use this skill for post-PR fixes — when a PR is open and needs a targeted fix in response to
CI failures or code review comments from the PR thread.

This is a standalone skill triggered directly by humans.

Do not use when:
- Addressing PR *review comments* that require triage and human decisions → use `review-pr`
  instead (which calls this skill internally for the actual fixes)
- The bug requires thorough investigation and a full plan → use `run-bug-fix` instead
- The fix is a gap in an existing implementation project → use `run-fix` instead

Compared to `run-bug-fix`: `run-hotfix` skips the full plan-and-review cycle. It is faster
but produces lighter documentation.


## Prerequisites

Your prompt must include:

- Bug description or fix objective
- The parent feature branch the PR was created from

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


## Git workflow

Determine the next hotfix number N by counting existing `--agents-hotfix-{N}` branches on the
parent branch.

Create the hotfix branch from the parent branch:

```shell
git switch {parent-branch}
git switch -c {parent-branch}--agents-hotfix-{N}
```

All commits are made on `{parent-branch}--agents-hotfix-{N}`.

After the review is approved, squash onto the parent branch:

```shell
git switch {parent-branch}
git merge --squash {parent-branch}--agents-hotfix-{N}
git commit -m "<fix message>"
```

The `--agents-hotfix-{N}` branch is **local only**. Do not push it to origin. It exists as a
local audit trail and is preserved after the squash.

Do NOT push the parent branch — that is the human's decision.


## Process


### 1. Investigate

Dispatch an `engineer-investigator` subagent with the `investigate-codebase` skill. Keep the
investigation focused: root cause and minimal blast radius only.

Synthesize findings into `bug-report.md`. Read `.agents/artifacts/bug-report/description.md` for
the canonical section definitions, and render `.agents/artifacts/bug-report/template.md.j2` to produce
the initial file. Replace all dummy content — every line drawn from the retro encabulator — with real
content for this bug. The rendered file must contain no placeholder text when submitted.


### 2. Plan

Write `implementation-plan.md` directly from the bug report. Read
`.agents/artifacts/implementation-plan/description.md` for section definitions and render
`.agents/artifacts/implementation-plan/template.md.j2` to produce the initial file. Replace all dummy
content — every line drawn from the retro encabulator — with real content. Fill in only what is essential
for the executor to proceed: `Goal`, `Project Commands`, `Project Standards`, and a single execution task
with clear steps and acceptance criteria. The rendered file must contain no placeholder text when submitted.

Do not dispatch a planner subagent. Do not dispatch a reviewer. Speed is the priority.


### 3. Execute

Dispatch an `engineer-executor` subagent with the `execute-implementation-plan` skill and the plan path.


### 4. Review

Read the journal to collect the list of modified files. Dispatch an `engineer-reviewer` subagent with the
`review-code` skill, passing the list of modified files and the project directory.

**Stop.** Present the review to the human. Resolve Critical findings before shipping. Significant and
Trivial findings are logged as follow-up work; they do not block the hotfix.


### 5. Squash and report

Perform the squash onto the parent branch (see Git workflow above).

Report completion to the human with:
- The squash commit SHA on the parent branch
- The hotfix branch name (preserved for history)
- Any Significant or Trivial findings deferred as follow-up work
