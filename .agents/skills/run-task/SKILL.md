# Run Task Skill

Coordinate a bounded task with a human plan gate, focused execution, one final QA pass,
independent review, and a human approval gate before squash. Use this workflow for small
features, refactors, cleanup, configuration changes, or documentation updates where the scope
is clear and a full design cycle would be excessive.

All artifacts are stored under `.artifacts/{YYYYMMDD}--{JIRA-ID}--{project-name}/`.


## When to use

Use this skill for any well-scoped minor change where the human already knows what they want
and a separate design document adds no value. If you can describe the full change in a short
task plan without needing an architecture section, use this skill.

**Reach for this skill first** whenever the request looks like any of these:

- Adding or tweaking a small feature to an existing module (new flag, new output format,
  changed behavior of one function)
- A localized refactor (rename, extract a helper, split a function, reorder imports)
- A configuration or tooling change (Makefile target, pyproject.toml entry, CI step)
- A style or formatting fix across a bounded set of files
- Adding tests for an already-implemented piece of code
- A documentation update (README, docstrings, changelog, TODO)
- Any change where all affected files can be listed up front and none of them require
  rethinking the architecture

**Use `run-feature` instead when:**

- The change requires a design decision that the human has not already made
- Multiple subsystems need to be coordinated in a non-obvious way
- The scope is uncertain and might expand once investigation begins
- A new module, subpackage, or major data structure is being introduced from scratch

**Use other skills when:**

- Fixing a confirmed bug → `run-bug-fix` or `run-hotfix`
- Addressing a gap in an existing implementation project → `run-fix`
- Addressing PR review comments → `review-pr`


## Prerequisites

Your prompt must include:

- A clear description of the task to perform

If not provided, ask before proceeding. Do not guess.


## Project directory

Derive `{project-name}` from the task description: kebab-case, lowercase, five words or fewer
(e.g. `add-retry-logic`, `clean-up-imports`, `update-default-timeout`).

Run process step 0 first so `{JIRA-ID}` is known, then create
`.artifacts/{YYYYMMDD}--{JIRA-ID}--{project-name}/`. If the branch has no ticket (no match, or it contains
`NO-TICKET`), omit the `{JIRA-ID}` segment entirely — do not write the literal text `NO-TICKET` into the path.

All artifacts for this task are stored there.

| Artifact             | Description                            |
| -------------------- | -------------------------------------- |
| `task-plan.md`       | Minimal plan authored by the principal |
| `task-journal.md`    | Execution journal                      |
| `code-review--01.md` | Single lightweight review pass         |


## Git workflow

Make all workflow commits in the agent worktree on `{agent-branch}`. The agent never switches the human's worktree.


### Branch and integration contract

Invoke `create-agent-worktree` with workflow identifier `task`. It owns normal-branch selection, local/audit only
branch allocation, collision handling, and agent worktree creation. This workflow never pushes, creates a pull request,
or merges into `main` or `master`.
Once the normal branch is ready, tell the human to invoke `run-pr`.

For local main integration, stop and obtain explicit human approval before integration. After approval rebase the
normal branch onto current main, then use `git merge --ff-only`. Never squash directly to main.

After human code-review approval and the stale-parent check, squash the agent branch exclusively into the parent branch:

```shell
git -C {parent-worktree} merge --squash {agent-branch}
git commit -m "<message>"
```

The audit branch is **local only**. Do not push it to origin. Retain it locally indefinitely for audit and recovery;
never delete it automatically. Only explicit human cleanup may delete it. After successful squash, invoke
`cleanup-agent-worktree` to remove only the agent worktree.

Do NOT push the parent branch and do NOT create a PR — that is the human's decision.

Commit message format follows `~/.agents/instructions/git.md`:

```text
<type>(<jira-id>): <short description>

- <bullet describing what was done>
- <bullet describing what was done>
```

Use `feat`, `fix`, `refactor`, `docs`, or `ci` as appropriate for the change.


## Process

### 0. Worktree and branch setup

Before creating the task plan or changing code, inspect the current parent worktree and branch.

- If the parent branch is `main` or `master`, ask the human for an associated work ticket ID. Wait for their response.
  Use the provided ID as `{TASK-ID}` or `NO-TICKET` if the human confirms there is no ticket. Derive `{type}` and
  `{slug}`, then create the ready-to-PR parent branch without switching the human's worktree.
- Otherwise, use the current parent branch as `{parent-branch}`. Extract `{JIRA-ID}` from it using `[A-Z]+-[0-9]+`; use
  `NO-TICKET` when present; otherwise omit the ticket segment from artifact paths and commit messages.

Invoke `create-agent-worktree` before any artifact with workflow identifier `task`, the parent worktree,
`{parent-branch}`, immutable parent base `{parent-base}`, and normal-branch naming data if needed. Keep the human in
the parent worktree. Create
every task artifact, journal, and code change in the agent worktree. Report the agent worktree path, agent branch,
parent branch, and recorded base at every later human gate.

Continue directly to stage 1 (plan) and its approval gate. Do not stop before that gate.


### 1. Plan

The principal selects the model for the planner using the principal's Model selection policy, chooses and dispatches the
model-specific `engineer-task-planner` variant, and records the exact variant agent name. Stop for explicit human
approval of the task plan before execution.

Dispatch the selected `engineer-task-planner--{work|personal}-{suffix}` variant to write
`task-plan.md`. The prompt must include:
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

If the task plan contains an **Unknowns** section, resolve each Unknown with the human before
proceeding. When resolved, fold the resolution into the plan body and remove it from Unknowns.
Remove the Unknowns section entirely once all items are resolved.

**STOP — end your turn here.**
Present the task plan to the human. Wait for the human to ask questions, request revisions, or give approval.

**Do not proceed to execution under any circumstances until the human responds with an unambiguous approval
signal** — a message such as "approved", "looks good", "proceed", or similar. Silence, a question, or a request
for changes is NOT approval.

Your final output in this turn must include this exact block, filled in:

```text
AWAITING APPROVAL: task plan
Path: {path to task-plan.md}
Unlocks: stage 2 (execution) — nothing else
```

When the human responds with approval, your next turn must open with:

```text
APPROVED: task plan
Proceeding to: stage 2 (execute)
```


### 2. Execute

Select the executor model using the principal's Model selection policy, choose and dispatch the
exact `engineer-executor--{work|personal}-{suffix}` variant, and record the exact variant agent
name. The executor runs the focused tests relevant to the task and records results.


### 3. Final QA

Run final QA exactly once after execution. Use a constrained light executor selected by the
principal's Model selection policy to fix only straightforward QA issues. Do not repeat final QA
after those fixes unless the fixes alter acceptance criteria, introduce a new code path, or
change behavior, an interface, data, security, or tests.


### 4. Review

Read the journal to collect modified files. Select the reviewer model using the principal's
Model selection policy, choose and dispatch the exact
`engineer-reviewer--{work|personal}-{suffix}` variant, and record the exact variant agent name.
Reviewers start diff-first, expand context only as required, and return compact findings without
redundant skill loading. Re-review only after acceptance-criteria, new-code-path, behavior,
interface, data, security, or test changes.

Address all findings:
- Apply Trivial findings directly without discussion.
- Resolve Critical findings before squashing — dispatch an `engineer-executor` to fix them, then re-run the
  quality gate.
- Log Significant findings as follow-up work; they do not block the task.

Before presenting the review, use any interactive diff-review capability available in the current runtime to gather
human feedback on the change. Incorporate clear feedback before the approval gate. If no such capability is available,
present the review artifact and a concise diff summary through the normal human-review channel. This supplements, and
does not replace, explicit human approval.

**STOP — end your turn here.**
Present the review to the human. Wait for the human to ask questions, request revisions, or give approval.

**Do not squash under any circumstances until the human explicitly approves.** This workflow never pushes and never
creates a PR.

Your final output in this turn must include this exact block, filled in:

```text
AWAITING APPROVAL: code review
Path: {path to code-review--01.md}
Unlocks: stage 5 (squash) — nothing else
```

When the human responds with approval, your next turn must open with:

```text
APPROVED: code review
Proceeding to: stage 5 (squash)
```


### 5. Squash and report

Immediately before integration, compare the recorded parent worktree, branch, and base with
current parent state. A mismatch is a stale-parent stop requiring an explicit human decision.
Never silently rebase, merge, discard, overwrite, or alter human work. If regeneration is
approved, explicitly discard the agent worktree and audit branch, record the decision, and
restart from the updated parent.

After successful exclusive squash integration, invoke `cleanup-agent-worktree` with the creation result and agent
worktree. It must remove only the agent worktree and retain the audit branch locally indefinitely only when the
creation result says one exists; otherwise it reports that no temporary audit branch was created. Never delete it
automatically; preserve both until the human explicitly removes them.

Successful cleanup preserves the local agent branch.

Perform the squash onto the parent branch (see Git workflow above).

Report completion to the human with:
- The project directory path
- The squash commit SHA on the parent branch
- The audit branch name (preserved for history)
- Any Significant findings deferred as follow-up work

Once the normal branch is ready, tell the human to invoke `run-pr`.
