---
name: run-bug-fix
description: Orchestrates the full bug fix workflow: investigate, plan, execute, and review.
---

# Run Bug Fix Skill

Coordinate the full bug fix workflow: investigation, implementation planning, execution, and review. All
artifacts are stored under `.artifacts/{YYYYMMDD}--{JIRA-ID}--{project-name}/`.


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
(e.g. `fix-null-pointer-on-login`), five words or fewer. Run branch setup first (see Git workflow below)
so `{JIRA-ID}` is known, then create `.artifacts/{YYYYMMDD}--{JIRA-ID}--{project-name}/`. Match
`{JIRA-ID}` using the same rule as the branch-setup Jira extraction below; if the branch has no ticket
(no match, or it contains `NO-TICKET`), omit the `{JIRA-ID}` segment entirely — do not write the literal
text `NO-TICKET` into the path. All artifacts for this project are stored there.

| Artifact                                  | Description                                                                                |
| ----------------------------------------- | ------------------------------------------------------------------------------------------ |
| `bug-report.md`                           | Investigation findings and confirmed root cause                                            |
| `implementation-plan.md`                  | Fix plan                                                                                   |
| `implementation-review--{N}.md`           | Implementation plan review (N = zero-padded 2 digits: 01, 02, ...)                         |
| `implementation-journal.md`               | Execution journal                                                                          |
| `execution-review--{scope-id}--{N}.md`    | Execution review (scope-id = task-NN or whole-plan; N = zero-padded 2 digits: 01, 02, ...) |


## Isolated worktree lifecycle

Before investigation or any bug-report artifact, record the parent worktree, parent branch, and
immutable parent base. Create a distinct agent worktree and agent branch from that base. Keep every
bug report, implementation plan, journal, code change, QA correction, and review context in the
agent worktree. Every later gate names the agent worktree path and agent branch.

Before each specialist handoff, the principal selects a model-specific variant from the
project-class menu. Use `engineer-investigator--{work|personal}-{suffix}` for investigation,
`engineer-planner--{work|personal}-{suffix}` for planning,
`engineer-executor--{work|personal}-{suffix}` for execution and constrained QA-fix, and
`engineer-reviewer--{work|personal}-{suffix}` for review. Record the exact variant, provider/model
ID, project class, and handoff purpose in the implementation journal or review context. Never dispatch
a generic specialist role.

Perform final QA exactly once before independent review. QA-fix is a constrained executor handoff,
not a second QA owner. Review approval remains an explicit human gate. Immediately before exclusive
squash integration into the ready-to-PR parent branch, compare the current parent worktree, branch,
and base with the recorded values. A stale-parent result stops the run and offers only an explicit
human reconciliation decision. Never silently rebase, merge, discard, overwrite, or mutate human work.

After successful squash, remove only the agent worktree and retain every temporary `--agents-*`
branch locally indefinitely for audit and recovery. Never delete it automatically; only explicit
human cleanup may delete it. If integration is declined or the run is abandoned, preserve both
worktree and branch until the human explicitly requests cleanup. The workflow never pushes or
creates a pull request.


## Git workflow

This skill manages its own git branch and commits throughout the workflow. Follow these rules
exactly.

### Branch and integration contract

All worktrees must be exactly `<repo-root>/.worktrees/<agent-branch>`. Never use `git switch` in the human worktree.
Starting from `main` or `master`, create normal `{type}/{TASK-ID}--{slug}` with `git branch` and create the agent
worktree directly on that normal branch. There is no `--agents` branch in this mode. Starting from an existing normal
feature/task branch, create local/audit only `{parent-branch}--agents-bug-fix` with `git branch`, then create its
agent worktree and squash it
back to the normal parent after all gates. This workflow never pushes, creates a pull request, or merges into `main` or
`master`. Once the normal branch is ready, tell the human to invoke `run-pr`.

For local main integration, stop and obtain explicit human approval before integration. After approval rebase the
normal branch onto current main, then use `git merge --ff-only`. Never squash directly to main.


### 0. Branch setup (before any work)

Record the parent worktree path, `{parent-branch}`, and immutable `{parent-base}` SHA before creating a branch or
worktree. Check the current branch:

- If the parent is `main` or `master`: obtain `{TASK-ID}`, then create the normal parent branch:
  ```shell
  git branch {type}/{TASK-ID}--{slug} {parent-base}
  ```
  Set `{agent-branch}` to `{type}/{TASK-ID}--{slug}`.
- Otherwise: create the temporary agent branch from the existing parent:
  ```shell
  git branch {parent-branch}--agents-bug-fix {parent-base}
  ```
  Set `{agent-branch}` to `{parent-branch}--agents-bug-fix`.

Extract the Jira ID from the current (parent) branch name:
- Match the pattern `[A-Z]+-[0-9]+` (e.g. `FUS-123`) → use it as the Jira ID
- If the branch contains `NO-TICKET` → use `NO-TICKET` as the Jira ID
- If neither matches → no Jira ID; omit the parenthetical from commit messages

Immediately after `git branch`, create the matching agent worktree:

```shell
git worktree add <repo-root>/.worktrees/<agent-branch> {agent-branch}
```

Never use `git switch` in the human worktree. All commits during stages 1–3 are made on the selected agent branch.
Continue directly to stage 1 (investigate) and its root-cause approval gate. Do not stop before that gate.


### Commits after each approved stage

After the human approves each stage, commit everything staged at that point:

```shell
git add -A
git commit -m "<message>"
```

The commit message format follows `~/.agents/instructions/git.md`:

```text
<type>(<jira-id>): <short description>

- <bullet describing what was done>
- <bullet describing what was done>
```

Stage-specific commit types:
- **After bug report approved**: `docs(<jira-id>): add bug report for {project-name}`
- **After implementation plan approved**: `docs(<jira-id>): add fix plan for {project-name}`
- **After execution approved**: `fix(<jira-id>): {short description of fix}`

The body bullets should summarise what the stage produced — not implementation detail.

The `--agents-build` branch is **local only**. Do not push it to origin. It exists as a local
audit trail and is preserved after the squash so the full history remains accessible on the
machine.


### Squash onto the feature branch

After the execution is approved by both the agent reviewer and the human, squash all
`--agents-build` commits onto the parent feature branch:

1. Propose a squash commit message to the human following the same format. **Wait for explicit
   approval before proceeding.**
2. Once approved:
   ```shell
    git -C {parent-worktree} merge --squash {agent-branch}
    git -C {parent-worktree} commit -m "<approved message>"
   ```
3. Do NOT delete the `--agents-build` branch — it is preserved locally as the full commit history.
4. Do NOT push the parent branch — that is the human's decision.


## Process


### 1. Investigate

Run branch setup (see Git workflow above) before doing anything else.

Dispatch the selected model-specific `engineer-investigator--{work|personal}-{suffix}` variant with
the `investigate-codebase` skill. Direct the investigator to determine: root cause, affected code
paths, and blast radius. Record the selected variant and model ID in the journal before dispatch.

Synthesize the investigator's findings into `bug-report.md`. Read
`.agents/artifacts/bug-report/description.md` for the canonical section definitions, and render
`.agents/artifacts/bug-report/template.md.j2` to produce the initial file. Replace all dummy
content — every line drawn from the retro encabulator — with real content for this bug. The rendered
file must contain no placeholder text when submitted.

**STOP — end your turn here.**
Present the bug report to the human. Confirm the root cause and scope before proceeding. If the
root cause is unclear, dispatch the investigator again with a more targeted question.

**Do not proceed to planning until the human explicitly confirms the root cause.**

Before ending your turn, verify every item in this checklist:
- [ ] I have presented the bug report to the human in this turn
- [ ] I have NOT dispatched a planning agent or started any planning work
- [ ] I am ending my turn now and will not act again until the human responds

Once confirmed: commit (see Git workflow — "After bug report approved").


### 2. Plan

Dispatch the selected model-specific `engineer-planner--{work|personal}-{suffix}` variant with the
`create-implementation-plan` skill, passing the bug report path as the planning input in place of a
design plan. Record the exact variant and model ID in the journal.

Then dispatch an `architect-reviewer` subagent with the `review-implementation-plan` skill, the plan
path, and iteration `01`.

Address all findings from the review:
- Apply trivial findings directly without discussion.
- Apply significant and critical findings using judgment. Flag genuinely ambiguous ones inline.
- Record the outcome in each finding's `##### Outcome` subsection.
- Re-dispatch an `architect-reviewer` at N+1 if changes were substantial. Repeat until the
  agent reviewer approves.

**STOP — end your turn here.**
The implementation plan is ready for human review. Present it to the human. Do not summarize the
agent findings — the human will read the plan directly. Wait for the human to ask questions,
request revisions, or give approval.

**Do not proceed to execution until the human explicitly approves the plan.**

Before ending your turn, verify every item in this checklist:
- [ ] I have presented the implementation plan to the human in this turn
- [ ] I have NOT dispatched an executor agent or started any execution work
- [ ] I am ending my turn now and will not act again until the human responds

Once approved: commit (see Git workflow — "After implementation plan approved").


### 3. Execute

Dispatch the selected model-specific `engineer-executor--{work|personal}-{suffix}` variant with the
`execute-implementation-plan` skill and the plan path. Record the exact variant and model ID in the
journal. Use the same variant family for a constrained QA-fix handoff and record that purpose.

Then dispatch the selected model-specific `engineer-reviewer--{work|personal}-{suffix}` variant with
the `review-implementation-execution` skill, the journal path, scope `whole-plan`, and iteration
`01`. Record the exact reviewer variant, project class, and provider/model ID in the review context.

Address all findings from the review:
- Apply trivial findings directly without discussion.
- Dispatch the selected model-specific executor variant to fix significant and critical findings.
  Flag genuinely ambiguous ones inline.
- Record the outcome in each finding's `##### Outcome` subsection.
- Re-dispatch an `engineer-reviewer` at N+1 if changes were substantial. Repeat until the
  agent reviewer approves.

**STOP — end your turn here.**
The execution is ready for human review. Present the execution review to the human. Wait for the
human to ask questions, request revisions, or give approval.

**Do not proceed to the squash until the human explicitly approves the execution.**

Before ending your turn, verify every item in this checklist:
- [ ] I have presented the execution review to the human in this turn
- [ ] I have NOT started the squash or any post-execution work
- [ ] I am ending my turn now and will not act again until the human responds

Once approved: commit (see Git workflow — "After execution approved"), then perform the squash
onto the feature branch (see Git workflow — "Squash onto the feature branch").


### 4. Report

Report completion to the human with:
- The project directory path
- The final status of each artifact
- The `--agents-build` branch name (preserved for history)
- The squash commit SHA on the parent branch

Once the normal branch is ready, tell the human to invoke `run-pr`.
