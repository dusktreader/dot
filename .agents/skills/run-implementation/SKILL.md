---
name: run-implementation
description: Orchestrates the full implementation workflow from feature description to reviewed code.
---

# Run Implementation Skill

Coordinate the full implementation workflow across five stages: design, planning, execution,
manual testing, and PR creation.


## When to use

Use this skill to implement a new feature or significant change end-to-end — from business
requirements through to a reviewed, tested, and PR-ready commit.

This is a standalone skill triggered directly by humans.

Do not use when:
- Fixing a known bug → use `run-bug-fix` (full) or `run-hotfix` (quick) instead
- Addressing a gap in an already-completed implementation → use `run-fix` instead
- Addressing PR review comments → use `review-pr` instead
- The work is exploratory with no clear output → use `run-architecture-audit` instead

This is the only skill that manages the full `--agents-build` branch lifecycle from creation
through to PR. Post-PR work uses `review-pr` and `run-hotfix`.


## Prerequisites

Your prompt must include:

- Feature description or business requirements to implement

If not provided, ask before proceeding. Do not guess.


## Project directory

Before starting, derive a `{project-name}` from the feature description:

- Kebab-case, lowercase, no special characters except hyphens
- Short and descriptive (under 50 characters)
- Examples: `add-user-authentication`, `refactor-payment-module`

Create `.agents/work/{YYYYMMDD}-{HHmmss}--{project-name}/`. All artifacts for this project are
stored there.

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


### 0. Branch setup (before any work)

Check the current branch:

- If it is `main` or `master`: **STOP immediately.** Tell the human agents must not work
  directly on main/master and ask them to create a topic branch first. Do not proceed.
- Otherwise: create a `--agents-build` branch from the current branch:
  ```shell
  git switch -c {current-branch}--agents-build
  ```

Extract the Jira ID from the current (parent) branch name:
- Match the pattern `[A-Z]+-[0-9]+` (e.g. `FUS-123`) → use it as the Jira ID
- If the branch contains `NO-TICKET` → use `NO-TICKET` as the Jira ID
- If neither matches → no Jira ID; omit the parenthetical from commit messages

All commits during stages 1–4 are made on the `--agents-build` branch.


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


### Squash and PR (stage 5 only)

After the human approves manual testing, squash all `--agents-build` commits onto the parent
branch and create a PR:

1. Propose a squash commit message to the human following the same format. **Wait for explicit
   approval before proceeding.**
2. Once approved:
   ```shell
   git switch {parent-branch}
   git merge --squash {parent-branch}--agents-build
   git commit -m "<approved message>"
   ```
3. Do NOT delete the `--agents-build` branch — it is preserved locally as the full commit history.
4. Push the parent branch to origin:
   ```shell
   git push origin {parent-branch}
   ```
5. Determine the PR base branch:
   - The parent branch is a feature branch (e.g. `fix/FUS-337-...`), not `main`. Use `git
     log --oneline {parent-branch} ^main --` to confirm commits exist, then use `main` as
     the base in the common case where the feature branch was cut from `main`.
   - If the feature branch was cut from a non-main branch: ask the human which branch to
     use as the PR base before proceeding.
6. Create the PR. The title is the squash commit subject line. The body is the squash commit
   body (the bullet list). Extract them from the commit:
   ```shell
   git log -1 --format="%s" {parent-branch}   # subject → --title
   git log -1 --format="%b" {parent-branch}   # body    → --body
   ```
   Then create:
   ```shell
   gh pr create --base <base-branch> --head {parent-branch} \
     --title "<subject>" --body "<body>"
   ```
7. Return the PR URL to the human.


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

If the design plan contains an **Unknowns** section, every Unknown must be resolved with explicit
human input before the plan is approved. Present each Unknown to the human **one at a time**, in
order. Wait for the human's response to each before presenting the next. Do not assume an answer,
do not infer resolution from a related discussion, and do not resolve multiple Unknowns in a single
turn. Only after every Unknown has received an explicit human response may the plan be presented
for final approval.

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

Once approved: commit and push (see Git workflow — "After execution approved").

**Do not squash. Do not create a PR. Proceed to stage 4.**


### 4. Manual Testing

**STOP — end your turn here.**
Tell the human that the implementation is on the `--agents-build` branch and ready for manual
testing. Ask them to test and report any issues.

Wait for the human to report issues or give approval.

**Do not proceed to stage 5 under any circumstances until the human explicitly approves manual
testing.** Issues reported, silence, or questions are not approval.

For each issue the human reports:

1. Create `manual-testing-issue--{N}.md` in the project work directory. Document:
   - The issue as described by the human
   - Root cause (investigate if needed)
   - The fix applied
2. Fix the issue on the `--agents-build` branch.
3. Run the project quality gate (`make qa` or equivalent) and confirm it passes.
4. Commit and push the fix (see Git workflow — "After each manual testing fix").
5. Tell the human what was fixed and ask them to verify.

Repeat until the human gives explicit manual testing approval.


### 5. Squash and PR

Perform the squash and create the PR (see Git workflow — "Squash and PR").

**STOP — end your turn here.**
Report completion to the human with:
- The project directory path
- The final status of each artifact
- The `--agents-build` branch name
- The squash commit SHA on the parent branch
- The PR URL
