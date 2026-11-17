---
name: external-review
description: Resolves GitHub pull request review comments one at a time with human approval, focused commits, pushes, and replies. Use when the human asks to address PR comments.
---

# External Review Skill

Resolve GitHub pull request comments through an explicit agent-human cycle. Work on one comment at a time, keep one
commit per addressed comment, and synchronize the GitHub discussion with the code.


## When to use

Use when the human asks to address review comments on a GitHub pull request.


## Prerequisites

The prompt may include a pull request number or URL. If omitted, resolve the pull request for the current branch during
setup. Ask if the pull request or branch is missing or ambiguous.


## Workflow phases and states

| Phase        | State                  | Transition                                                 |
| ------------ | ---------------------- | ---------------------------------------------------------- |
| Setup        | Worktree cleanliness   | Require a clean current worktree before GitHub requests    |
| Setup        | GitHub context         | Confirm account and remote                                 |
| Setup        | Pull request and base  | Resolve PR, confirm head branch, and determine base/rebase |
| Review       | Comment inventory      | Fetch and track all review comments                        |
| Review       | One-comment proposal   | Present change, message, reply, push target; get one approval |
| Review       | Implement and verify   | Make approved change, run checks, and commit one comment   |
| Publication  | Addressed comment      | Push approved commit and reply to the exact review comment |
| Publication  | No-change decision     | Post approved explanation without an empty commit          |
| Continuation | Next comment           | Advance only after the current comment is complete         |
| Handoff      | Review complete        | Report addressed comments and any remaining threads        |


### Setup phase

#### Verify worktree cleanliness

Record the current branch and check `git status --short` before making GitHub requests. Require a clean worktree. If it
is dirty, alert the human and ask them to resolve it. Stop without stashing, committing, or discarding changes.


#### Establish GitHub context

Read `~/.agents/instructions/github.md` before using `gh`. Confirm the authenticated account with `gh auth status` and
the intended remote.


#### Resolve the pull request and base

Use the supplied pull request number or URL when available. Otherwise, run `gh pr view` from the current repository to
find a pull request for the checked-out branch. If none is found, ask the human and stop. Confirm that the pull
request's head branch matches the current branch; otherwise ask the human and stop.

Determine the target base. If the base branch or whether the normal branch must be rebased is ambiguous, ask the human
and wait. Never infer either decision.


### Review phase

#### Gather comments

Fetch unresolved review threads with comment ID, author, file, line, body, and URL. Fetch top-level review bodies and
ignore dependency and CI-only comments. Track every comment in a working list, including comments that need no code
change; do not silently omit comments.


#### Discuss one comment and propose the change

For the next comment only, present a single proposal containing everything the human must approve:

1. The reviewer's complete comment.
2. Relevant code context with `file_path:line_number` references.
3. Your evaluation of validity, including evidence and any disagreement.
4. The proposed change as a precise file-level description or diff (or the reason for no change).
5. The commit message (omit for a no-change decision).
6. The exact GitHub reply text. Use the published formats below, with the commit SHA shown as `<sha>`.
7. The push target as `remote/branch` (omit for a no-change decision).

End with one question: "Approve this proposal?" Do not implement, commit, push, or reply while waiting.


#### Approval is a single gate

- One explicit approval of the proposal authorizes every step in it: edit, verify, commit, push to the stated target, and
  post the stated reply. Do not ask again for any of these steps.
- Treat "yes", "approved", "looks good", or similar as approval of the most recent proposal. Do not ask the human to
  restate it or to approve individual parts separately.
- If the human approves only part of the proposal, or asks for changes, revise the proposal and present it again once.
- Ask again only if the result materially deviates from what was approved: a different diff, a different commit
  message, a different reply, a different push target, or verification failures that force a change of approach.
  Explain the deviation and ask.
- Showing the resulting diff after implementation is informational, not a second gate.


#### Implement and verify

After approval, make only the approved change, add or update behavior-focused tests when applicable, and run the
project's required lint, typecheck, and test commands. Inspect status, diff, diff check, and recent log before
committing. Stage only files belonging to the current comment and commit with the approved message. A commit must
address one comment only. Then continue directly into the Publication phase.


### Publication phase

#### Publish an addressed comment

After the commit succeeds, push the current branch without force
options. Obtain the resulting commit SHA and reply to the exact review comment with actual paragraph breaks and a linked
commit reference:

```text
Addressed in commit [<sha>](https://github.com/<owner>/<repo>/commit/<sha>)

<brief explanation of the change>
```

Use the GitHub API or `gh` and verify the stored body does not contain literal `\\n` text. Do not mark a thread resolved
unless the human asks for that separately.


#### Reply to a no-change decision

After the human approves the proposal, reply without creating an empty commit or pushing:

```text
Won't fix: <brief explanation of why the comment does not require a code change>
```


### Continuation phase

#### Advance to the next comment

Confirm the commit and reply succeeded, or confirm the approved no-change reply succeeded. Update the working list. Move
to the next unresolved comment only after the current comment is complete.


### Handoff phase

#### Report review status

Report addressed comments, commit SHAs, no-change decisions, verification results, and remaining unresolved threads.


## Safety rules

- Never push or reply before the human approves a proposal that includes the change, commit message, response, and push target.
- Never push unrelated working-tree changes.
- Never force-push or amend commits.
- Preserve secrets and redact them from replies and logs.
- Require a clean working tree before starting and between comments. During a comment, only approved changes may be
  present.
- If unrelated changes appear, stop and ask the human to resolve them; do not stash, commit, or discard them.
- If verification exposes unrelated baseline failures, report them separately rather than mixing fixes into the current
  comment.