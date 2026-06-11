---
name: run-implementation
description: Orchestrates the full implementation workflow from feature description to reviewed code.
---

# Run Implementation Skill

Coordinate the full implementation workflow: design, implementation planning, execution, and review.


## Prerequisites

Your prompt must include:

- Feature description or business requirements to implement

If not provided, ask before proceeding. Do not guess.


## Project directory

Before starting, derive a `{project-name}` from the feature description:

- Kebab-case, lowercase, no special characters except hyphens
- Short and descriptive (under 50 characters)
- Examples: `add-user-authentication`, `refactor-payment-module`

Create `.agents/work/{YYYYMMDD}-{HHmmss}--{project-name}/`. All artifacts for this project are stored there.

| Artifact                                  | Description                                                                                |
| ----------------------------------------- | ------------------------------------------------------------------------------------------ |
| `design-plan.md`                          | Design plan                                                                                |
| `design-review--{N}.md`                   | Design plan review (N = zero-padded 2 digits: 01, 02, ...)                                 |
| `implementation-plan.md`                  | Implementation plan                                                                        |
| `implementation-review--{N}.md`           | Implementation plan review (N = zero-padded 2 digits: 01, 02, ...)                         |
| `implementation-journal.md`               | Execution journal                                                                          |
| `execution-review--{scope-id}--{N}.md`    | Execution review (scope-id = task-NN or whole-plan; N = zero-padded 2 digits: 01, 02, ...) |


## Git workflow

This skill manages its own git branch and commits throughout the workflow. Follow these rules
exactly.


### 0. Branch setup (before any work)

Check the current branch:

- If it is `main` or `master`: **STOP immediately.** Tell the human agents must not work
  directly on main/master and ask them to create a topic branch first. Do not proceed.
- Otherwise: create an `--agents` branch from the current branch:
  ```shell
  git switch -c {current-branch}--agents
  ```

Extract the Jira ID from the current (parent) branch name:
- Match the pattern `[A-Z]+-[0-9]+` (e.g. `FUS-123`) → use it as the Jira ID
- If the branch contains `NO-TICKET` → use `NO-TICKET` as the Jira ID
- If neither matches → no Jira ID; omit the parenthetical from commit messages

All commits during the workflow are made on the `--agents` branch.


### Commits after each approved stage

After the human approves each stage, commit everything staged at that point and push:

```shell
git add -A
git commit -m "<message>"
git push -u origin {current-branch}--agents
```

The commit message format follows `~/.agents/instructions/git.md`:

```text
<type>(<jira-id>): <short description>

- <bullet describing what was done>
- <bullet describing what was done>
```

Stage-specific commit types and scopes:
- **After design plan approved**: `docs(<jira-id>): add design plan for {project-name}`
- **After implementation plan approved**: `docs(<jira-id>): add implementation plan for {project-name}`
- **After execution approved**: `feat(<jira-id>): implement {project-name}` (or `fix`/`refactor`/`ci`
  etc. as appropriate to the work)

The body bullets should summarise what the stage produced — not implementation detail.

Push is permitted as part of this workflow. The global "never push" default is explicitly
overridden here.


### Final squash onto parent branch

After the human approves the final execution and the CHANGELOG is updated, squash all
`--agents` commits onto the parent branch as a single commit:

1. Propose a squash commit message to the human following the same format. **Wait for explicit
   approval before proceeding.**
2. Once approved:
   ```shell
   git switch {parent-branch}
   git merge --squash {parent-branch}--agents
   git commit -m "<approved message>"
   ```
3. Do NOT delete the `--agents` branch — it is preserved as the full commit history.
4. Do NOT push the parent branch — that is the human's decision.


## Process

### 1. Design

Run branch setup (see Git workflow above) before doing anything else.

Dispatch an `architect-planner` subagent with the `create-design-plan` skill, the feature
description, and the project directory.

Then dispatch an `architect-reviewer` subagent with the `review-design-plan` skill, the design
plan path, and iteration `01`.

Address all findings from the review:
- Apply trivial findings directly without discussion.
- Apply significant and critical findings using judgment. If a finding is genuinely ambiguous —
  where the correct resolution depends on information only the human has — flag it inline and
  note what you need. Do not stop the workflow for findings you can resolve yourself.
- Record the outcome in each finding's `##### Outcome` subsection.
- Re-dispatch an `architect-reviewer` at N+1 if changes were substantial. Repeat until the
  agent reviewer approves.

**STOP — end your turn here.**
The design plan is ready for human review. Present it to the human. Do not summarize the agent
findings — the human will read the plan directly. Wait for the human to ask questions, request
revisions, or give approval.

**Do not proceed to planning under any circumstances until the human responds with an
unambiguous approval signal** — a message such as "approved", "looks good", "proceed", or
similar. Silence, a question, or a request for changes is NOT approval. If the human asks
a question or requests a revision, address it and stop again. Do not interpret the absence
of objection as approval.

Once approved: commit and push (see Git workflow — "After design plan approved").


### 2. Plan

Dispatch an `engineer-planner` subagent with the `create-implementation-plan` skill and the
design plan path.

Then dispatch an `architect-reviewer` subagent with the `review-implementation-plan` skill, the
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

Once approved: commit and push (see Git workflow — "After implementation plan approved").


### 3. Execute

Dispatch an `engineer-executor` subagent with the `execute-implementation-plan` skill and the
implementation plan path.

Then dispatch an `engineer-reviewer` subagent with the `review-implementation-execution` skill,
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

Once approved: commit and push (see Git workflow — "After execution approved"), then perform the
final squash onto the parent branch.


### 4. Report

Report completion to the human with:
- The project directory path
- The final status of each artifact
- The `--agents` branch name and the squash commit SHA on the parent branch
