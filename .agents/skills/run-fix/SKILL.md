---
name: run-fix
description: Extends an existing implementation project with a scoped fix. Use when a human identifies a gap or missed requirement post-implementation. Never trigger automatically.
---

# Run Fix Skill

Extend an existing implementation project with a scoped fix plan. This skill is always triggered
by a human identifying a specific gap — never by an agent acting on its own initiative.

The fix lives in the same project directory as the original implementation. It adds new artifacts
without modifying the original design plan, implementation plan, or journal.


## When to use

Use this skill when, after a `run-feature` project is complete, a human identifies a
missed requirement or incorrect behaviour that needs a targeted fix — through code review, UAT,
or manual testing feedback.

This is a standalone skill triggered directly by humans. It always operates within an existing
project directory created by `run-feature`.

Do not use when:
- The gap is discovered during a PR review → use `review-pr` instead
- The bug is unrelated to an existing implementation project → use `run-bug-fix` or
  `run-hotfix` instead
- The change is a new feature rather than a fix → start a new `run-feature` project
- No agent triggered this — this skill must never be triggered automatically


## Prerequisites

Your prompt must include:

- Path to the existing project directory (`.artifacts/{project}/`)
- A clear description of the gap or missed requirement to fix

If either is missing, ask before proceeding. Do not guess.


## When to use this skill

Use this skill when, after implementation is complete, a human identifies something that was
missed — through code review, UAT, or operational feedback. Examples:

- An AC was not met
- A key design constraint was not implemented correctly
- A behaviour is wrong in a way that requires targeted changes

Do NOT use this skill to:
- Add new features (start a new project with `run-feature` instead)
- Make broad architectural changes (those require a new design plan)
- Fix things proactively — only when a human explicitly requests it


## Artifacts

All artifacts are written to the existing project directory alongside the original artifacts.

| Artifact                                        | Description                                                                               |
| ----------------------------------------------- | ----------------------------------------------------------------------------------------- |
| `implementation-plan--fix-{N}.md`               | Scoped fix plan (N = zero-padded 2 digits: 01, 02, ...)                                   |
| `implementation-review--fix-{N}--{M}.md`        | Fix plan review (N = fix number, M = zero-padded iteration: 01, 02, ...)                  |
| `implementation-journal--fix-{N}.md`            | Execution journal for the fix                                                             |
| `execution-review--fix-{N}--whole-plan--{M}.md` | Execution review (N = fix number, M = zero-padded iteration: 01, 02, ...)                 |

Use the next available N by checking what fix artifacts already exist in the project directory.


## Isolated worktree lifecycle

Before reading or writing fix artifacts or changing code, record the parent worktree, parent branch,
and immutable parent base. Create a distinct agent worktree and agent branch from that base. Every fix
artifact and code change stays in the agent worktree, and every gate names its path and branch.

Locate the existing implementation project from the agent-worktree view, then attach the fix plan,
journal updates, bug context, and review evidence to that project's established artifact directory.
Fail closed when the project is missing, the artifact directory is ambiguous, or the expected project
path cannot be established in the agent worktree. Report the specific resolution failure and create
or modify no artifact or code. Never attach fix work to the human worktree or guess a project path.

For investigator, planner, executor, constrained QA-fix, and reviewer handoffs, the principal selects
and dispatches a model-specific `--work-{suffix}` or `--personal-{suffix}` variant from the approved
project-class menu. Record the exact variant, provider/model ID, project class, and handoff purpose in
the fix journal or review context. Never dispatch a generic specialist role.

Run final QA once, obtain independent review, and wait for explicit approval. Immediately before
exclusive squash integration, compare the recorded parent worktree, branch, and base with current
parent state. A stale parent stops the run and requires an explicit human reconciliation decision.
Never silently rebase, merge, discard, overwrite, or mutate human work. After a successful squash,
remove only the agent worktree and retain every temporary `--agents-*` branch locally indefinitely for
audit and recovery. Never delete it automatically; only explicit human cleanup may delete it.
Declined or abandoned runs preserve both until explicit human cleanup. Never push or create a pull
request.


## Git workflow

This skill manages its own git commits throughout the workflow. It always creates a fresh agent
branch and worktree; do not reuse an original `run-feature` agent branch.

### Branch and integration contract

All worktrees must be exactly `<repo-root>/.worktrees/<agent-branch>`. Never use `git switch` in the human worktree.
Starting from `main` or `master`, create normal `{type}/{TASK-ID}--{slug}` with `git branch` and create the agent
worktree directly on that normal branch. There is no `--agents` branch in this mode. Starting from an existing normal
feature/task branch, create local/audit only `{parent-branch}--agents-fix` with `git branch`, then create its agent
worktree and squash it back
to the normal parent after all gates. This workflow never pushes, creates a pull request, or merges into `main` or
`master`. Once the normal branch is ready, tell the human to invoke `run-pr`.

For local main integration, stop and obtain explicit human approval before integration. After approval rebase the
normal branch onto current main, then use `git merge --ff-only`. Never squash directly to main.

### 0. Branch setup

Before reading the existing project artifacts or changing code, record the parent worktree path,
`{parent-branch}`, and immutable `{parent-base}` SHA.

1. If the parent is `main` or `master`, obtain `{TASK-ID}`, derive `{type}` and `{slug}`, then create the normal
   parent branch:
   ```shell
   git branch {type}/{TASK-ID}--{slug} {parent-base}
   ```
   Set `{agent-branch}` to `{type}/{TASK-ID}--{slug}`.
2. Otherwise, create the temporary agent branch from the existing parent:
   ```shell
   git branch {parent-branch}--agents-fix {parent-base}
   ```
   Set `{agent-branch}` to `{parent-branch}--agents-fix`.
3. Immediately after `git branch`, create the matching agent worktree:
   ```shell
   git worktree add <repo-root>/.worktrees/<agent-branch> {agent-branch}
   ```

Never use `git switch` in the human worktree. Extract the Jira ID from the parent branch name using the same rules as
`run-feature`. Continue directly to stage 1 (plan) and its approval gate. Do not stop before that gate.

### Commits after each approved stage

After the human approves each stage, commit:

```shell
git add -A
git commit -m "<message>"
```

Stage-specific commit types:
- **After fix plan approved**: `docs(<jira-id>): add fix-{N} plan for {project-name}`
- **After fix execution approved**: `fix(<jira-id>): apply fix-{N} for {project-name}`

### Final squash onto parent branch

After the human approves the fix execution and the CHANGELOG is updated, squash all new
`--agents` commits (those not already on the parent branch) onto the parent branch:

1. Propose a squash commit message to the human. **Wait for explicit approval.**
2. Once approved:
   ```shell
    git -C {parent-worktree} merge --squash {agent-branch}
    git -C {parent-worktree} commit -m "<approved message>"
   ```
3. Do NOT delete the `--agents` branch.
4. Do NOT push the parent branch — that is the human's decision.


## Process

### 1. Plan

Run branch setup before reading the existing implementation project.

Read the existing `implementation-plan.md` and `design-plan.md` to understand the project context.

Dispatch the selected model-specific `engineer-planner--{work|personal}-{suffix}` variant to create
`implementation-plan--fix-{N}.md`. The prompt
must include:
- The specific gap or missed requirement
- Path to the existing project directory
- Instruction to scope the plan narrowly — only what is needed to address the gap, nothing more
- Instruction to read `.agents/artifacts/implementation-plan/description.md` for section definitions,
  render `.agents/artifacts/implementation-plan/template.md.j2` to produce the initial file, and replace
  all dummy content with real content. The rendered file must contain no placeholder text when submitted.

Then dispatch an `architect-reviewer` subagent with the `review-implementation-plan` skill, the
fix plan path, and iteration `01`.

Address all findings from the review:
- Apply trivial findings directly without discussion.
- Apply significant and critical findings using judgment. If a finding is genuinely ambiguous —
  where the correct resolution depends on information only the human has — flag it inline and
  note what you need. Do not stop the workflow for findings you can resolve yourself.
- Record the outcome in each finding's `##### Outcome` subsection.
- Re-dispatch an `architect-reviewer` at M+1 if changes were substantial. Repeat until the
  agent reviewer approves.

**STOP — end your turn here.**
The fix plan is ready for human review. Present it to the human. Do not summarize the agent
findings — the human will read the plan directly. Wait for the human to ask questions, request
revisions, or give approval. Do not proceed until the human explicitly approves.

Before ending your turn, verify every item in this checklist:
- [ ] I have presented the fix plan to the human in this turn
- [ ] I have NOT dispatched an executor agent or started any execution work
- [ ] I am ending my turn now and will not act again until the human responds

Once approved: commit (see Git workflow — "After fix plan approved").


### 2. Execute

Dispatch the selected model-specific `engineer-executor--{work|personal}-{suffix}` variant with the
`execute-implementation-plan` skill and the fix plan path. Record the exact variant and model ID.
The journal is `implementation-journal--fix-{N}.md`. Use the same variant family for a constrained
QA-fix handoff and record that purpose.

Then dispatch the selected model-specific `engineer-reviewer--{work|personal}-{suffix}` variant with
the `review-implementation-execution` skill, the fix journal path, scope `whole-plan`, and iteration
`01`. Record the exact reviewer variant, project class, and provider/model ID. The review artifact is
`execution-review--fix-{N}--whole-plan--01.md`.

Address all findings from the review:
- Apply trivial findings directly without discussion.
- Dispatch the selected model-specific executor variant to fix significant and critical findings.
  Flag genuinely ambiguous ones inline.
- Record the outcome in each finding's `##### Outcome` subsection.
- Re-dispatch an `engineer-reviewer` at M+1 if changes were substantial. Repeat until the
  agent reviewer approves.

If a `CHANGELOG.md` exists in the repo root, add an entry under `## Unreleased` summarising
what was fixed. Use the fix plan's Goal as the basis. Follow the existing entry style in the
file.

**STOP — end your turn here.**
The execution is ready for human review. Present the execution review to the human. Wait for the
human to ask questions, request revisions, or give approval. Do not proceed until the human
explicitly approves.

Before ending your turn, verify every item in this checklist:
- [ ] I have presented the execution review to the human in this turn
- [ ] I have NOT started the squash or any post-execution work
- [ ] I am ending my turn now and will not act again until the human responds

Once approved: commit (see Git workflow — "After fix execution approved"), then perform
the final squash onto the parent branch.


### 3. Report

Report completion with the paths to all new artifacts, a summary of what was changed, and the
squash commit SHA on the parent branch.

Once the normal branch is ready, tell the human to invoke `run-pr`.
