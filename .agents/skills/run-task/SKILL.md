---
name: run-task
description: Lightweight workflow for minor engineering tasks. No design document. Principal-authored plan, execution, single review pass, squash onto topic branch. No PR creation.
---

# Run Task Skill

Coordinate a minor engineering task with minimal overhead: principal-authored plan, direct execution, and a single
lightweight code review pass. Use this workflow for small features, refactors, cleanup, configuration changes, or
documentation updates where the scope is clear and a full design-plus-implementation cycle would be excessive.

All artifacts are stored under `.artifacts/{YYYYMMDD}--{JIRA-ID}--{project-name}/`.


## When to use

Use this skill for any well-scoped minor change where the human already knows what they want and a separate design
document adds no value.

This is a standalone skill triggered directly by humans.

Do not use when:
- The change is significant enough to warrant a design plan → use `run-implementation` instead
- The work is fixing a confirmed bug → use `run-bug-fix` (full) or `run-hotfix` (post-PR urgent) instead
- The fix addresses a gap in an existing implementation project → use `run-fix` instead
- Addressing PR review comments → use `review-pr` instead


## Prerequisites

Your prompt must include:

- A clear description of the task to perform

If not provided, ask before proceeding. Do not guess.


## Project directory

Derive `{project-name}` from the task description: kebab-case, lowercase, five words or fewer
(e.g. `add-retry-logic`, `clean-up-imports`, `update-default-timeout`).

Run branch setup first (see Git workflow below) so `{JIRA-ID}` is known, then create
`.artifacts/{YYYYMMDD}--{JIRA-ID}--{project-name}/`. If the branch has no ticket (no match, or it contains
`NO-TICKET`), omit the `{JIRA-ID}` segment entirely — do not write the literal text `NO-TICKET` into the path.

All artifacts for this task are stored there.

| Artifact                 | Description                                    |
| ------------------------ | ---------------------------------------------- |
| `task-plan.md`           | Minimal plan authored by the principal         |
| `task-journal.md`        | Execution journal                              |
| `code-review--01.md`     | Single lightweight review pass                 |


## Git workflow

Check the current branch:

- If it is `main` or `master`: ask the human for an associated work ticket ID. Wait for their
  response — do not proceed without it. If they provide a ticket ID (e.g. `FUS-123`), use it
  as `{TASK-ID}`. If they confirm there is no ticket, use `NO-TICKET` as `{TASK-ID}`.

  Derive `{type}` from the nature of the work (same conventional-commit types used in commit
  messages: `feat`, `fix`, `refactor`, `docs`, `ci`, etc.).

  Derive `{slug}` from the task description: kebab-case, lowercase, five words or fewer.

  Create the branch:
  ```shell
  git switch -c {type}/{TASK-ID}--{slug}
  ```

- Otherwise: create an `--agents-task` branch from the current branch:
  ```shell
  git switch -c {current-branch}--agents-task
  ```

Extract the Jira ID from the current (parent) branch name:
- Match the pattern `[A-Z]+-[0-9]+` (e.g. `FUS-123`) → use it as `{JIRA-ID}`
- If the branch contains `NO-TICKET` → use `NO-TICKET` as the Jira ID
- If neither matches → no Jira ID; omit the parenthetical from commit messages

All commits are made on the `--agents-task` branch.

After the review is approved, squash onto the parent branch:

```shell
git switch {parent-branch}
git merge --squash {parent-branch}--agents-task
git commit -m "<message>"
```

The `--agents-task` branch is **local only**. Do not push it to origin. It exists as a local audit trail and is
preserved after the squash.

Do NOT push the parent branch and do NOT create a PR — that is the human's decision.

Commit message format follows `~/.agents/instructions/git.md`:

```text
<type>(<jira-id>): <short description>

- <bullet describing what was done>
- <bullet describing what was done>
```

Use `feat`, `fix`, `refactor`, `docs`, or `ci` as appropriate for the change.


## Process

### 1. Plan

Dispatch an `engineer-task-planner` subagent to write `task-plan.md`. The prompt must include:
- The task description
- The project directory path
- Instruction to read `.agents/artifacts/task-plan/description.md` for section definitions and render
  `.agents/artifacts/task-plan/template.md.j2` to produce the initial file
- Instruction to replace all dummy content — every line drawn from the retro encabulator — with real content
- Instruction to fill in only what is essential for the executor to proceed: `Goal`, `Project Commands`,
  `Project Standards` (if relevant), `Steps`, and `Acceptance Criteria`
- Instruction to omit `Technical Notes` unless there is something genuinely task-specific to note
- Instruction that the rendered file must contain no placeholder text when submitted

Do not dispatch a reviewer.

**STOP — end your turn here.**
Present the task plan to the human. Wait for the human to ask questions, request revisions, or give approval.

**Do not proceed to execution under any circumstances until the human responds with an unambiguous approval
signal** — a message such as "approved", "looks good", "proceed", or similar. Silence, a question, or a request
for changes is NOT approval.

Your final output in this turn must include this exact block, filled in:

```
AWAITING APPROVAL: task plan
Path: {path to task-plan.md}
Unlocks: stage 2 (execution) — nothing else
```

When the human responds with approval, your next turn must open with:

```
APPROVED: task plan
Proceeding to: stage 2 (execute)
```


### 2. Execute

Dispatch an `engineer-executor` subagent with the `execute-implementation-plan` skill, the task plan path, and the
task journal path (`task-journal.md`).


### 3. Review

Read the journal to collect the list of modified files. Dispatch an `engineer-reviewer` subagent with the
`review-code` skill, passing the list of modified files and the project directory.

Address all findings:
- Apply Trivial findings directly without discussion.
- Resolve Critical findings before squashing — dispatch an `engineer-executor` to fix them, then re-run the
  quality gate.
- Log Significant findings as follow-up work; they do not block the task.

**STOP — end your turn here.**
Present the review to the human. Wait for the human to ask questions, request revisions, or give approval.

**Do not squash under any circumstances until the human explicitly approves.**

Your final output in this turn must include this exact block, filled in:

```
AWAITING APPROVAL: code review
Path: {path to code-review--01.md}
Unlocks: stage 4 (squash) — nothing else
```

When the human responds with approval, your next turn must open with:

```
APPROVED: code review
Proceeding to: stage 4 (squash)
```


### 4. Squash and report

Perform the squash onto the parent branch (see Git workflow above).

Report completion to the human with:
- The project directory path
- The squash commit SHA on the parent branch
- The `--agents-task` branch name (preserved for history)
- Any Significant findings deferred as follow-up work
