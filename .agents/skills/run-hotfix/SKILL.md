# Run Hotfix Skill

Coordinate an urgent fix with minimal overhead: brief investigation, principal-authored plan, direct
execution, and a single lightweight code review pass. Use this workflow for post-PR fixes — CI
failures, code review findings, or other issues found after a PR is open. All artifacts are stored
under `.artifacts/{YYYYMMDD}--{JIRA-ID}--{project-name}/`.


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
(e.g. `hotfix-auth-token-expiry`), five words or fewer. Run branch setup first (see Git workflow below)
so `{JIRA-ID}` is known, then create `.artifacts/{YYYYMMDD}--{JIRA-ID}--{project-name}/`. If the parent
branch has no ticket (no match, or it contains `NO-TICKET`), omit the `{JIRA-ID}` segment entirely — do
not write the literal text `NO-TICKET` into the path. All artifacts for this project are stored there.

| Artifact                    | Description                                 |
| --------------------------- | ------------------------------------------- |
| `bug-report.md`             | Brief investigation findings and root cause |
| `implementation-plan.md`    | Minimal fix plan authored by the principal  |
| `implementation-journal.md` | Execution journal                           |
| `code-review--01.md`        | Single lightweight review pass              |


## Isolated worktree lifecycle

Before investigation, the principal-authored minimal plan, or code changes, invoke `create-agent-worktree` with
workflow identifier `hotfix`. Investigation notes, the minimal plan, code, QA-fix changes, and lightweight review
context stay there, and every existing hotfix gate identifies the agent worktree path and agent branch.

Select a model-specific variant before every applicable handoff: use
`engineer-investigator--{work|personal}-{suffix}` for investigation,
`engineer-executor--{work|personal}-{suffix}` for execution and constrained QA-fix, and
`engineer-reviewer--{work|personal}-{suffix}` for review. Record the exact variant, provider/model ID,
project class, and handoff purpose in the hotfix journal or review context. Never dispatch a generic
specialist, and do not add an engineer-planner handoff unless the principal explicitly changes the
workflow class.

Preserve the streamlined gates: brief investigation, principal-authored minimal plan, direct execution,
one lightweight review, and the existing approval thresholds. Do not add task-style plan approval,
independent review, or any additional human approval gate solely because isolation was added. Immediately before
exclusive squash integration, compare the recorded parent worktree, branch, and base with current
parent state. A stale parent stops the run and requires an explicit human reconciliation decision.
Never silently rebase, merge, discard, overwrite, or mutate human work. After a successful squash, invoke
`cleanup-agent-worktree` with the creation result and agent worktree. It must remove only the agent worktree and retain
the audit branch locally indefinitely only when the creation result says one exists; otherwise it reports that no
temporary audit branch was created. Never delete it automatically; only explicit human cleanup may delete it. Declined
or abandoned runs preserve both until the human explicitly requests cleanup. Never push or create a pull request.


## Git workflow

### Branch and integration contract

Invoke `create-agent-worktree` with workflow identifier `hotfix`. It owns normal-branch selection, local/audit only
branch allocation, collision handling, and agent worktree creation. This workflow never pushes, creates a pull request,
or merges into `main` or `master`. Once the normal branch is ready, tell the human to invoke `run-pr`.

For local main integration, stop and obtain explicit human approval before integration. After approval rebase the
normal branch onto current main, then use `git merge --ff-only`. Never squash directly to main.

Extract the Jira ID from the parent branch name:
- Match the pattern `[A-Z]+-[0-9]+` (e.g. `FUS-123`) → use it as `{JIRA-ID}`
- If the branch contains `NO-TICKET`, or neither matches → no Jira ID; omit the `{JIRA-ID}` segment
  from the project directory name (see Project directory above)

Before investigation, invoke `create-agent-worktree` with the parent worktree, `{parent-branch}`, immutable
`{parent-base}` SHA, workflow identifier `hotfix`, and normal-branch naming data. All commits are made on
`{agent-branch}`. Continue directly to stage 1
(investigate), then proceed directly through the principal-authored plan and execution to stage 4 (review) and its
existing lightweight review approval gate. Do not stop before that gate.

After the review is approved, squash onto the parent branch:

Run the squash from the parent worktree with `git -C {parent-worktree} merge --squash {agent-branch}`, then commit.

The audit branch is **local only**. Do not push it to origin. It is preserved after the squash.

After successful squash, invoke `cleanup-agent-worktree` with the creation result and agent worktree.

Do NOT push the parent branch — that is the human's decision.


## Process

### 1. Investigate

Dispatch the selected model-specific `engineer-investigator--{work|personal}-{suffix}` variant with
the `investigate-codebase` skill. Keep the investigation focused: root cause and minimal blast radius
only. Record the exact variant and model ID in the hotfix journal before dispatch.

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

Dispatch the selected model-specific `engineer-executor--{work|personal}-{suffix}` variant with the
`execute-implementation-plan` skill and the plan path. Record the exact variant and model ID. Use the
same variant family for a constrained QA-fix handoff and record that purpose.


### 4. Review

Read the journal to collect the list of modified files. Dispatch the selected model-specific
`engineer-reviewer--{work|personal}-{suffix}` variant with the `review-code` skill, passing the list of
modified files and the project directory. Record the exact reviewer variant, project class, and
provider/model ID in the hotfix review context.

Before presenting the review, use any interactive diff-review capability available in the current runtime to gather
human feedback on the change. Incorporate clear feedback before the approval gate. If no such capability is available,
present the review artifact and a concise diff summary through the normal human-review channel. This supplements, and
does not replace, explicit human approval.

**STOP — end your turn here.**
Present the review to the human. Resolve Critical findings before shipping. Significant and
Trivial findings are logged as follow-up work; they do not block the hotfix.

Before ending your turn, verify every item in this checklist:
- [ ] I have presented the code review to the human in this turn
- [ ] I have NOT started the squash or any post-review work
- [ ] I am ending my turn now and will not act again until the human responds


### 5. Squash and report

Perform the squash onto the parent branch (see Git workflow above).

Report completion to the human with:
- The squash commit SHA on the parent branch
- The hotfix branch name (preserved for history)
- Any Significant or Trivial findings deferred as follow-up work

Once the normal branch is ready, tell the human to invoke `run-pr`.
