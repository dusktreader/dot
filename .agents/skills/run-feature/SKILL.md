---
name: run-feature
description: Orchestrates the full implementation workflow from feature description to reviewed code.
---

# Run Feature Skill

Coordinate a full feature workflow in an isolated agent worktree. The human's current worktree
remains the integration authority throughout the run.


## When to use

Use this skill to implement a new feature or significant change end-to-end — from business
requirements through to a reviewed, tested, and PR-ready commit.

This is a standalone skill triggered directly by humans.

Do not use when:
- Fixing a known bug → use `run-bug-fix` (full) or `run-hotfix` (quick) instead
- Addressing a gap in an already-completed implementation → use `run-fix` instead
- Addressing PR review comments → use `review-pr` instead
- The work is exploratory with no clear output → use `run-architecture-audit` instead

This is the only skill that manages the full feature lifecycle from worktree creation through
exclusive squash integration. It never pushes or creates a PR. Post-PR work uses `review-pr` and
`run-hotfix`.


## Prerequisites

Your prompt must include:

- Feature description or business requirements to implement

If not provided, ask before proceeding. Do not guess.


## Worktree setup

Before creating any artifact, journal, plan, or code, and before any artifact is emitted:

1. Record the human parent worktree path, parent branch, and immutable parent base SHA.
2. Create an agent worktree and local agent branch from that recorded parent state. The agent
   worktree must be a distinct path, and the human stays in the parent worktree.
3. Put every project artifact and code change in the agent worktree. Record the agent worktree
   path and agent branch in every later gate and handoff.

Do not create a branch without its worktree. Do not emit a plan before setup completes.


## Project directory

Before starting, derive a `{project-name}` from the feature description:

- Kebab-case, lowercase, no special characters except hyphens
- Short and descriptive, five words or fewer
- Examples: `add-user-authentication`, `refactor-payment-module`

Run branch setup first (see Git workflow below) so `{JIRA-ID}` is known, then create
`.artifacts/{YYYYMMDD}--{JIRA-ID}--{project-name}/`. Match `{JIRA-ID}` using the same rule as the
branch-setup Jira extraction below; if the branch has no ticket (no match, or it contains
`NO-TICKET`), omit the `{JIRA-ID}` segment entirely — do not write the literal text `NO-TICKET` into
the path. All artifacts for this project are stored there.

| Artifact                                   | Description                                                                                |
| ------------------------------------------ | ------------------------------------------------------------------------------------------ |
| `design-plan.md`                           | Design plan                                                                                |
| `design-review--{N}.md`                    | Design plan review (N = zero-padded 2 digits: 01, 02, ...)                                 |
| `implementation-plan.md`                   | Implementation plan                                                                        |
| `implementation-review--{N}.md`            | Implementation plan review (N = zero-padded 2 digits: 01, 02, ...)                         |
| `implementation-journal.md`                | Execution journal                                                                          |
| `execution-review--{scope-id}--{N}.md`     | Execution review (scope-id = task-NN or whole-plan; N = zero-padded 2 digits: 01, 02, ...) |
| `manual-testing-issue--{N}.md`             | Manual testing issue and fix log (N = zero-padded 2 digits: 01, 02, ...)                   |


## Git workflow

This skill manages its own git branch and commits throughout the workflow. Follow these rules
exactly.


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
- **After design plan approved**: `docs(<jira-id>): add design plan for {project-name}`
- **After implementation plan approved**: `docs(<jira-id>): add implementation plan for {project-name}`
- **After execution approved**: `feat(<jira-id>): implement {project-name}` (or `fix`/`refactor`/`ci`
  as appropriate)
- **After each manual testing fix**: `fix(<jira-id>): {short description of fix}`

The body bullets should summarise what the stage produced — not implementation detail.

The `--agents-build` branch is **local only**. Do not push it to origin. It exists as a local
audit trail and is preserved after the squash so the full history remains accessible on the
machine.


### Exclusive squash integration

After the human approves manual testing, perform one exclusive squash integration into the
ready-to-PR parent branch:

1. Immediately before integration, compare the recorded parent worktree, parent branch, and base
   SHA with the current parent. If any differ, stop and present the stale-parent state to the
   human. Never silently rebase, merge, discard, overwrite, or alter human work.
2. If the human explicitly approves regeneration, discard the agent worktree and local audit
   branch as an explicit operation, record the decision, and restart from the updated parent.
3. Propose a squash commit message to the human and wait for explicit approval.
4. Once approved:
   ```shell
   git switch {parent-branch}
    git merge --squash {agent-branch}
   git commit -m "<approved message>"
   ```
5. Remove only the agent worktree after a successful squash. Successful cleanup preserves the local agent branch
   for audit. If integration is declined or the run is abandoned, preserve both worktree and
   branch until the human explicitly removes them.


## Process


### 0. Branch setup

Check the current branch:

- If it is `main` or `master`: ask the human for an associated work ticket ID. Wait for their
  response — do not proceed without it. If they provide a ticket ID (e.g. `FUS-123`), use it
  as `{TASK-ID}`. If they confirm there is no ticket, use `NO-TICKET` as `{TASK-ID}`.

  Derive `{type}` from the nature of the work (same conventional-commit types used in commit
  messages: `feat`, `fix`, `refactor`, `docs`, `ci`, etc.).

  Derive `{slug}` from the feature description: kebab-case, lowercase, five words or fewer.

  Create the branch:
  ```shell
  git switch -c {type}/{TASK-ID}--{slug}
  ```

- Otherwise: create a `--agents-build` branch from the current branch:
  ```shell
  git switch -c {current-branch}--agents-build
  ```

Extract the Jira ID from the current parent branch name:

- Match the pattern `[A-Z]+-[0-9]+` (e.g. `FUS-123`) → use it as the Jira ID
- If the branch contains `NO-TICKET` → use `NO-TICKET` as the Jira ID
- If neither matches → no Jira ID; omit the parenthetical from commit messages

All commits during stages 1–4 are made on the `--agents-build` branch.


### 1. Design

Before each dispatch, the principal selects the model using the principal's Model selection policy, chooses the
corresponding model-specific specialist variant, and records and dispatches that exact variant agent name. Do not
dispatch a generic unvaried specialist role name. Apply this requirement to every dispatch in this workflow.

Dispatch the selected `architect-planner--{work|personal}-{suffix}` variant with the `create-design-plan` skill, the feature
description, and the project directory.

Then dispatch the selected `architect-reviewer--{work|personal}-{suffix}` variant with the `review-design-plan` skill, the design
plan path, and iteration `01`.

Address all findings from the review:
- Apply trivial findings directly without discussion.
- Apply significant and critical findings using judgment. If a finding is genuinely ambiguous —
  where the correct resolution depends on information only the human has — flag it inline and
  note what you need. Do not stop the workflow for findings you can resolve yourself.
- Record the outcome in each finding's `##### Outcome` subsection.
- Re-dispatch an `architect-reviewer` at N+1 if changes were substantial. Repeat until the
  agent reviewer approves.

If the design plan contains an **Unknowns** section, every Unknown must be resolved with explicit
human input before the plan is approved. Present each Unknown to the human **one at a time**, in
order. Wait for the human's response to each before presenting the next. Do not assume an answer,
do not infer resolution from a related discussion, and do not resolve multiple Unknowns in a single
turn. Only after every Unknown has received an explicit human response may the plan be presented
for final approval.

When an Unknown is resolved, **fold the resolution into the plan body** (as an AC, architecture
note, or Technical Notes entry as appropriate) and **remove it from the Unknowns section**. Do
not leave resolved items in Unknowns. If all Unknowns are resolved, remove the Unknowns section
entirely. The same rule applies to implementation plans.

**STOP — end your turn here.**
The design plan is ready for human review. Present it to the human. Do not summarize the agent
findings — the human will read the plan directly. Wait for the human to ask questions, request
revisions, or give approval.

**Do not proceed to planning under any circumstances until the human responds with an
unambiguous approval signal** — a message such as "approved", "looks good", "proceed", or
similar. Silence, a question, or a request for changes is NOT approval. If the human asks
a question or requests a revision, address it and stop again. Do not interpret the absence
of objection as approval.

Your final output in this turn must include this exact block, filled in:

```
AWAITING APPROVAL: design plan
Path: {path to design-plan.md}
Unlocks: stage 2 (implementation plan) — nothing else
Still requires separate approval before it can proceed: implementation plan, execution, manual testing
```

When the human responds with approval, your next turn must open with:

```
APPROVED: design plan
NOT YET APPROVED: implementation plan, execution, manual testing
Proceeding to: stage 2 (create implementation plan)
```

Once approved: commit (see Git workflow — "After design plan approved").


### 2. Plan

Dispatch the selected `engineer-planner--{work|personal}-{suffix}` variant with the `create-implementation-plan` skill and the
design plan path.

Then dispatch the selected `architect-reviewer--{work|personal}-{suffix}` variant with the `review-implementation-plan` skill, the
implementation plan path, and iteration `01`.

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

**Do not proceed to execution under any circumstances until the human responds with an
unambiguous approval signal** — a message such as "approved", "looks good", "proceed", or
similar. Silence, a question, or a request for changes is NOT approval. If the human asks
a question or requests a revision, address it and stop again. Do not interpret the absence
of objection as approval.

Your final output in this turn must include this exact block, filled in:

```
AWAITING APPROVAL: implementation plan
Path: {path to implementation-plan.md}
Unlocks: stage 3 (execution) — nothing else
Still requires separate approval before it can proceed: execution, manual testing
```

When the human responds with approval, your next turn must open with:

```
APPROVED: implementation plan
NOT YET APPROVED: execution, manual testing
Proceeding to: stage 3 (execute)
```

Once approved: commit (see Git workflow — "After implementation plan approved").


### 3. Execute

Dispatch the selected `engineer-executor--{work|personal}-{suffix}` variant with the `execute-implementation-plan` skill and the
implementation plan path.

### Final QA

After the executor completes, the orchestrator runs the project-wide quality gate exactly once. Use a constrained,
lightweight executor to fix only straightforward QA failures that are clearly within the implementation plan's scope.
The lightweight executor must not expand the work or make design decisions. Re-run final QA only when such a fix
changes an acceptance criterion, introduces a new code path, or changes behavior, an interface, data, security, or
tests.

Then dispatch the selected `engineer-reviewer--{work|personal}-{suffix}` variant with the `review-implementation-execution` skill,
the journal path, scope `whole-plan`, and iteration `01`.

Address all findings from the review:
- Apply trivial findings directly without discussion.
- Dispatch an `engineer-executor` to fix significant and critical findings. Flag genuinely
  ambiguous ones inline.
- Record the outcome in each finding's `##### Outcome` subsection.
- Re-dispatch an `engineer-reviewer` at N+1 if changes were substantial. Repeat until the
  agent reviewer approves.

If a `CHANGELOG.md` exists in the repo root, add an entry under `## Unreleased` summarising
what was implemented. Use the implementation plan's Goal as the basis. Follow the existing
entry style in the file.

**STOP — end your turn here.**
The execution is ready for human review. Present the execution review to the human. Wait for the
human to ask questions, request revisions, or give approval. Do not proceed until the human
explicitly approves.

Your final output in this turn must include this exact block, filled in:

```
AWAITING APPROVAL: execution
Review path: {path to execution-review--whole-plan--NN.md}
Unlocks: stage 4 (manual testing) — nothing else
Still requires separate approval before it can proceed: manual testing
```

When the human responds with approval, your next turn must open with:

```
APPROVED: execution
NOT YET APPROVED: manual testing
Proceeding to: stage 4 (manual testing)
```

Once approved: commit (see Git workflow — "After execution approved").

**Do not squash. Do not create a PR. Proceed to stage 4.**


### 4. Manual Testing

**STOP — end your turn here.**
Tell the human that the implementation is on the `--agents-build` branch and ready for manual
testing. Ask them to test and report any issues.

Wait for the human to report issues or give approval.

**Do not proceed to stage 5 under any circumstances until the human explicitly approves manual
testing.** Issues reported, silence, or questions are not approval.

Your final output in this turn must include this exact block:

```
AWAITING APPROVAL: manual testing
Branch: {--agents-build branch name}
Unlocks: stage 5 (squash and PR) — nothing else
```

When the human responds with approval, your next turn must open with:

```
APPROVED: manual testing
Proceeding to: stage 5 (squash and PR)
```

For each issue the human reports:

1. Create `manual-testing-issue--{N}.md` in the project work directory. Document:
   - The issue as described by the human
   - Root cause (investigate if needed)
   - The fix applied
2. Fix the issue on the `--agents-build` branch.
3. Run the project quality gate (`make qa` or equivalent) and confirm it passes.
4. Commit the fix (see Git workflow — "After each manual testing fix").
5. Tell the human what was fixed and ask them to verify.

Repeat until the human gives explicit manual testing approval.


### 5. Squash and PR

Perform the squash and create the PR (see Git workflow — "Squash and PR").

**STOP — end your turn here.**
Report completion to the human with:
- The project directory path
- The agent worktree path
- The final status of each artifact
- The `--agents-build` branch name
- The squash commit SHA on the parent branch
- The PR URL
