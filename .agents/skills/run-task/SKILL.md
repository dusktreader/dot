# Run Task Skill

Coordinate a bounded task with a human plan gate, focused execution, implementation approval,
user-directed QA, and a human approval gate before squash. Use this workflow for small
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

| Artifact             | Description                                                           |
| -------------------- | --------------------------------------------------------------------- |
| `task-plan.md`       | Minimal plan authored by the principal                                |
| `task-journal.md`    | Execution journal                                                     |
| `code-review--01.md` | Single lightweight review pass                                        |
| `qa-journal.md`      | User-directed QA changes, reasons, verification, and final QA summary |


## Git workflow

Make all workflow commits in the agent worktree on `{agent-branch}`. The agent never switches the human's worktree.


### Branch and integration contract

Invoke `create-agent-worktree` with workflow identifier `task`. It owns normal-branch selection, local/audit only
branch allocation, collision handling, and agent worktree creation. This workflow never pushes, creates a pull request,
or merges into `main` or `master`.
Once the normal branch is ready, tell the human to invoke `run-pr`.

For local main integration, stop and obtain explicit human approval before integration. After approval rebase the
normal branch onto current main, then use `git merge --ff-only`. Never squash directly to main.

After human QA approval and the stale-parent check, squash the agent branch exclusively into the parent branch:

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

The principal selects the profile and tier for the planner using the principal's routing policy, dispatches the shared
`engineer-task-planner` role, and records the active profile and tier. Stop for explicit human approval of the task plan
before execution.

Dispatch the shared `engineer-task-planner` role to write
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

Select the executor profile and tier using the principal's routing policy, then dispatch the shared
`engineer-executor` role and record the active profile and tier. The executor runs the focused tests
relevant to the task and records results.


### 3. Implementation review

Run final QA exactly once after execution as the implementation quality gate. Use a constrained light
executor to fix only straightforward failures. This final QA is distinct from the later user-directed
QA phase. Do not repeat the quality gate unless a fix changes acceptance criteria, introduces a new
code path, or changes behavior, an interface, data, security, or tests.

Use an independent reviewer exactly once for the implementation approval. Keep the review diff-first
and compact. Do not launch adversarial review cycles; re-review only if a critical fix changes
acceptance criteria, a new code path, behavior, interface, data, security, or tests.

Address critical findings before leaving this phase. Log significant findings as follow-up work
unless they block the stated task. Apply trivial findings directly.

Before entering QA, ask the human whether they would like to review the changes first. If they opt in, use any
interactive diff-review capability available in the current runtime, or present a concise diff summary through the
normal review channel. Incorporate clear feedback before entering QA. If they decline, proceed directly to QA. This
optional review does not replace the QA approval gate.

Once the independent reviewer approves, continue directly to stage 4. Do not present the code review artifact for
human approval, do not reconcile the task plan, and do not start another planning cycle.

**Do not squash. Do not create a PR. Proceed directly to stage 4.**


### 4. QA

This phase begins immediately after the independent reviewer approves execution and any optional human diff review is
complete. The agent must stop, notify the human that the code is ready for QA, and wait for testing feedback. QA is the
human approval gate for the implementation. It does not authorize a new planning or review cycle.

Tell the human that the implementation is on the agent branch and ready for QA. Ask them to test it and report any
issues or requested adjustments.

**STOP — end your turn here.**

Before making the first QA change, read `.agents/artifacts/qa-journal/description.md` and render
`.agents/artifacts/qa-journal/template.md.j2` as `qa-journal.md` in the project directory. Replace all
placeholder content with the implementation path and real QA details. For every user-directed change,
append:

- The user's issue or requested adjustment
- The reason for the change
- The files changed
- Verification performed and its result

During QA, agents and subagents MUST NOT modify the task plan, code review, or any other plan or review
artifact. Do not dispatch plan reviewers, reconcile the implementation against the plan, or start an
adversarial review loop. Make only the smallest changes needed to address the user's direction.

After each change, run the focused project quality gate and ask the human to verify the result. Wait for
more user direction or explicit QA approval. Issues reported, silence, or questions are not approval.

When the human approves QA, add a concise summary of all QA changes and their reasons at the top of
`qa-journal.md`, then proceed to stage 5. QA changes are committed as one approved stage.

```text
AWAITING APPROVAL: QA
QA journal: {path to qa-journal.md}
Unlocks: stage 5 (squash) — nothing else
```

When the human responds with approval, your next turn must open with:

```text
APPROVED: QA
Proceeding to stage 5 (squash)
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
