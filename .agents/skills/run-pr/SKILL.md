---
name: run-pr
description: Publishes a clean normal feature or task branch and creates its pull request on explicit human request.
---

# Run PR skill

Publish a ready normal feature or task branch only when the human explicitly invokes `run-pr`. This is the only
workflow that pushes a branch or creates a pull request.


## Preconditions

Operate only from a clean normal feature or task branch. Reject `main`, `master`, and any branch whose name contains
`--agents`: these are not publishable branches. Stop if the worktree is dirty, the branch is detached, or the normal
branch cannot be identified.

Read `~/.agents/instructions/github.md` before using `gh`. Confirm the authenticated `gh` account as required there,
confirm the intended remote, and determine the target base. If the base branch or whether the normal branch must be
rebased is ambiguous, ask the human and wait. Never infer either decision.


## Process

1. Verify the current normal branch, clean worktree, remote, `gh` account, and target base.
2. Check the normal branch against the confirmed base. Resolve any required rebase before publication; do not alter a
   base branch.
3. Push the normal branch without force options.
4. Create the pull request against the confirmed base with `gh pr create`.
5. Return the pull request URL.


## Restrictions

Never force-push. Never publish a temporary `--agents` branch. Do not merge into `main` or `master`. Do not push or
create a pull request unless the human explicitly invoked `run-pr` in the current request.
