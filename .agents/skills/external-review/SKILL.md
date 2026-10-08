---
name: external-review
description: Resolves GitHub pull request review comments one at a time with human approval, focused commits, pushes, and replies.
---

# External review skill

Resolve review comments from someone else's GitHub pull request through an explicit agent-human cycle. Work on one
comment at a time, preserve one commit per addressed comment, and keep the GitHub discussion synchronized with the code.


## When to use

Use this skill when the human asks to address code review comments from a GitHub pull request.

Do not use this skill for an internal review of a proposed change or implementation. Use `internal-review` for that
workflow.


## Prerequisites

The prompt must include a pull request number or URL. Determine the repository, pull request branch, and current
worktree from the local checkout. Ask if the pull request or branch is ambiguous.


## Core workflow

### 1. Gather comments

1. Confirm the active GitHub account with `gh auth status`.
2. Fetch unresolved review threads, including comment ID, author, file, line, body, and URL.
3. Fetch top-level review bodies and ignore dependency and CI-only comments.
4. Track every comment in a working list. Do not silently omit comments that will not change code.


### 2. Work through comments one at a time

For the next comment only:

1. Show the reviewer’s complete comment.
2. Show the relevant code context with `file_path:line_number` references.
3. Evaluate whether the comment is valid, including evidence and any disagreement.
4. Propose an implementation or a reason not to change anything.
5. Stop and wait for explicit human approval before editing.

Do not implement, commit, push, or reply while waiting for approval.


### 3. Confirm the exact change

After the human approves the approach and before editing, show:

- the proposed diff or precise file-level change
- the suggested commit message
- the exact GitHub response

Use one commit for each addressed comment. For a no-change decision, propose the explanatory GitHub response and do not
create an empty commit.

Stop again if the human changes the approach or asks for a different commit or response.


### 4. Implement and verify

After approval:

1. Make only the approved change for the current comment.
2. Add or update behavior-focused tests when applicable.
3. Run the project’s required lint, typecheck, and test commands. Use the canonical project commands.
4. Inspect status, diff, diff check, and recent log before committing.
5. Stage only files belonging to the current comment.
6. Commit with the approved message.

A commit must address one comment only.


### 5. Publish and reply

After the commit succeeds:

1. Push the current branch to its configured remote. Never force-push, amend, or push unrelated changes.
2. Obtain the resulting commit SHA.
3. Reply to the exact review comment with actual paragraph breaks and a linked commit reference:

```text
Addressed in commit [<sha>](https://github.com/<owner>/<repo>/commit/<sha>)

<brief explanation of the change>
```

Use the GitHub API or `gh` and verify the stored body does not contain literal `\\n` text.

For a no-change decision, reply instead:

```text
Won't fix: <brief explanation of why the comment does not require a code change>
```

Do not mark a thread resolved unless the human asks for that separately.


### 6. Continue

1. Confirm the commit and reply succeeded.
2. Update the working list.
3. Move to the next unresolved comment only after the current comment is complete.
4. At the end, report addressed comments, commit SHAs, no-change decisions, verification results, and any remaining
   unresolved threads.


## Safety rules

- Never push before the human approves the exact change, commit message, and response.
- Never push unrelated working-tree changes.
- Never force-push or amend commits.
- Preserve secrets and redact them from replies and logs.
- Keep the working tree clean between comments whenever possible.
- If verification exposes unrelated baseline failures, report them separately rather than mixing fixes into the current
  comment.
