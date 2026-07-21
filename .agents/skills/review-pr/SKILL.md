# Review PR Skill

Work through open review comments on a pull request. Triage each comment by severity and
source, address bugs and clear fixes autonomously, escalate non-trivial decisions to the
human, apply all approved fixes in a dedicated review branch, and reply to every comment
with the outcome.


## When to use

Use this skill when a PR has open review comments — from human reviewers or automated code
reviewers (e.g. Copilot) — that need to be triaged and addressed.

This is a standalone skill triggered directly by humans after a PR is open.

Do not use when:
- The PR has no review comments and only needs CI fixes → use `run-hotfix` instead
- The work is pre-PR → use `run-feature` or `run-fix` instead
- The review is of a plan artifact, not code → use `review-implementation-plan` or
  `review-design-plan` instead

This skill calls `review-code` internally for code quality assessment. Each round of review comments is a new cycle.


## Prerequisites

Your prompt must include:

- PR number or URL
- The parent feature branch the PR was created from

If not provided, ask before proceeding. Do not guess.


## Project directory

Derive `{project-name}` from the PR title or branch name, prefixed with `pr-review-`
(e.g. `pr-review-reprocess-items`), five words or fewer. Determine the next review cycle number N by
counting existing `pr-review--{N}.md` artifacts in any existing project work directory for this PR.

All artifacts for this review cycle are stored in the same project work directory as the
original implementation (if one exists) or, if none exists, in a new
`.artifacts/{YYYYMMDD}--{JIRA-ID}--{project-name}/` directory. For a new directory, extract `{JIRA-ID}`
by matching `[A-Z]+-[0-9]+` against the parent feature branch name (e.g. `FUS-123`); if the branch
contains `NO-TICKET`, or no ticket pattern is found, omit the `{JIRA-ID}` segment entirely — do not
write the literal text `NO-TICKET` into the path. The artifact for this cycle is:

| Artifact              | Description                                                       |
| --------------------- | ----------------------------------------------------------------- |
| `pr-review--{N}.md`   | Triage table, findings, decisions, and outcomes (N = zero-padded  |
|                       | 2 digits: 01, 02, ...)                                            |


## Git workflow

Before fetching comments, invoke `create-agent-worktree` with workflow identifier `review`, the parent worktree,
`{parent-branch}`, immutable `{parent-base}` SHA, and the review cycle as naming data. Perform all comment triage
artifacts, fixes, commits, and QA in `{agent-worktree}` on the agent branch `{agent-branch}`.

All fix commits are made on `{agent-branch}`.

The audit branch is **local only**. Do not push it to origin. It is preserved after the squash.

After all fixes are approved and the quality gate passes, compare the recorded parent worktree,
branch, and base SHA with the current parent. If any differ, stop and present the stale-parent
state to the human. Never silently rebase, merge, discard, overwrite, or alter human work. If the
human approves regeneration, retain the agent worktree and audit branch until explicit human cleanup, and
restart from the updated parent.

After the stale-parent check and human approval of the squash message, squash locally onto the
normal parent branch:

```shell
git -C {parent-worktree} merge --squash {agent-branch}
git -C {parent-worktree} commit -m "<review-fixes message>"
```

After a successful squash, invoke `cleanup-agent-worktree` with the creation result and agent worktree. It must remove
only the agent worktree and retain the audit branch locally indefinitely only when the creation result says one exists;
otherwise it reports that no temporary audit branch was created. Never delete it automatically. Only explicit human
cleanup may delete the branch. If integration is declined or the run is abandoned, retain both the worktree and branch
until explicit human cleanup.


## Process

### 1. Fetch comments

Fetch all open review comments from the PR:

```shell
gh api repos/{owner}/{repo}/pulls/{pr}/comments \
  --jq '.[] | {id: .id, path: .path, line: (.line // .original_line), body: .body, user: .user.login, url: .html_url}'
```

Also fetch any top-level PR review bodies:

```shell
gh pr view {pr} --comments
```

Ignore bot-generated dependency review comments and CI status comments. Focus on code
review comments from humans and automated code reviewers (e.g. Copilot).


### 2. Triage

For each comment, classify:

- **Source**: `human` or `bot` (Copilot, automated reviewer, etc.)
- **Severity**: `critical` (incorrect behaviour, data loss, crash, security), `significant`
  (design concern, performance, API contract), or `trivial` (style, naming, nit). Both
  `critical` and `significant` must be addressed before the PR can merge; `trivial` items
  are addressed at the principal's discretion.
- **Disposition**: one of:
  - `auto-fix` — clear, unambiguous fix; no human input needed
  - `discuss` — non-trivial; requires human decision before acting
  - `won't-fix` — clearly out of scope or already addressed; reply and close

Write `pr-review--{N}.md` in the project work directory. Read
`.agents/artifacts/pr-review/description.md` for the canonical section definitions, and render
`.agents/artifacts/pr-review/template.md.j2` to produce the initial file. Replace all dummy
content — every line drawn from the retro encabulator — with real content for this review cycle.
The rendered file must contain no placeholder text when submitted.


### 3. Escalate non-trivial comments

**STOP — end your turn here.**
Present the triage table to the human. For every comment marked `discuss`, explain the
tradeoff and ask for a decision. For every comment marked `won't-fix`, confirm the reasoning.

Wait for explicit human responses on all `discuss` and `won't-fix` items before proceeding.
Do not interpret silence as approval. Do not resolve multiple `discuss` items in a single
turn — present them one at a time if there are dependencies between them.

Before ending your turn, verify every item in this checklist:
- [ ] I have presented the triage table to the human in this turn
- [ ] I have NOT applied any fixes or started any code changes
- [ ] I am ending my turn now and will not act again until the human responds

Update the `pr-review--{N}.md` artifact with the human's decisions before moving on.


### 4. Apply fixes

For each comment with disposition `auto-fix` or human-approved fix:

1. Implement the fix on `{agent-branch}`.
2. Run `make qa` and confirm it passes.
3. Commit the fix:
   ```shell
   git add -A
   git commit -m "fix: <short description of fix>"
   ```
4. Record the commit SHA in the `pr-review--{N}.md` artifact against the comment.

Group logically related fixes into a single commit where it makes the history cleaner.
Each commit must still pass `make qa` on its own.


### 5. Squash and reply

After all fixes are committed and `make qa` passes on the full branch:

1. Propose a squash commit message to the human. **Wait for approval.**
2. Run the stale-parent check, squash locally onto the parent branch, and remove only the agent
   worktree after the squash succeeds (see Git workflow).
3. For each addressed comment, reply on GitHub:

```text
Addressed in <short-sha>

   <One or two sentences describing what was changed and why.>
```

   Use:
   ```shell
   gh api repos/{owner}/{repo}/pulls/{pr}/comments/{comment-id}/replies \
     -f body="Addressed in <sha>\n\n<summary>"
   ```

4. For each `won't-fix` comment, reply:

```text
Won't fix: <brief rationale>
   ```

5. Re-request review from any human reviewers who left comments (skip bots):
   ```shell
   gh pr edit {pr} --add-reviewer <handle>
   ```


### 6. Report

Report completion to the human with:
- The `pr-review--{N}.md` artifact path
- The squash commit SHA on the parent branch
- A summary of what was addressed, what was declined, and any deferred items

After the local squash, direct the user to run-pr to publish the parent branch.
