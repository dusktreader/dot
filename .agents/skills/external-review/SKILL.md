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
| Review       | One-comment discussion | Present context and proposal; wait for explicit approval   |
| Review       | Exact change approval  | Approve diff, commit message, response, and push target    |
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


#### Discuss one comment

For the next comment only:

1. Show the reviewer's complete comment.
2. Show the relevant code context with `file_path:line_number` references.
3. Evaluate whether the comment is valid, including evidence and any disagreement.
4. Propose an implementation or a reason not to change anything.
5. Stop and wait for explicit human approval before preparing a change.

Do not implement, commit, push, or reply while waiting for approval.


#### Confirm the exact change

After the human approves the approach and before editing, show the proposed diff or precise file-level change, suggested
commit message, exact GitHub response, and push target (`remote/branch`). Wait for explicit approval of this exact set.
For a no-change decision, propose an explanatory response and do not create an empty commit or push.

Stop if the human changes the approach or asks for a different commit message, response, or push target.


#### Implement and verify

After exact approval, make only the approved change, add or update behavior-focused tests when applicable, and run the
project's required lint, typecheck, and test commands. Inspect status, diff, diff check, and recent log before
committing. Stage only files belonging to the current comment and commit with the approved message. A commit must
address one comment only.


### Publication phase

#### Publish an addressed comment

After the commit succeeds and the human has explicitly approved the push target, push the current branch without force
options. Obtain the resulting commit SHA and reply to the exact review comment with actual paragraph breaks and a linked
commit reference:

```text
Addressed in commit [<sha>](https://github.com/<owner>/<repo>/commit/<sha>)

<brief explanation of the change>
```

Use the GitHub API or `gh` and verify the stored body does not contain literal `\\n` text. Do not mark a thread resolved
unless the human asks for that separately.


#### Reply to a no-change decision

After the human approves the exact response, reply without creating an empty commit or pushing:

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

- Never push before the human explicitly approves the exact change, commit message, response, and push target.
- Never push unrelated working-tree changes.
- Never force-push or amend commits.
- Preserve secrets and redact them from replies and logs.
- Require a clean working tree before starting and between comments. During a comment, only approved changes may be
  present.
- If unrelated changes appear, stop and ask the human to resolve them; do not stash, commit, or discard them.
- If verification exposes unrelated baseline failures, report them separately rather than mixing fixes into the current
  comment.