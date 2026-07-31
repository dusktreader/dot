# Create agent worktree

Create the shared branch and isolated-worktree lifecycle boundary for branch-based workflows.


## Required inputs

The caller provides the repository root, parent worktree path, parent branch, immutable parent base SHA, workflow
identifier, and normal-branch naming data when the parent is `main` or `master`. Normal-branch data includes
`{type}`, `{TASK-ID}`, and `{slug}`.


## Creation policy

Record the parent worktree, parent branch, and immutable parent base before creating anything. Never use `git switch`
or otherwise mutate the human worktree.

When the parent is `main` or `master`, create the normal `{type}/{TASK-ID}--{slug}` branch from `{parent-base}` and
use that normal branch directly as `{agent-branch}`. There is no audit branch in this mode.

When the parent is an existing normal branch, use `{parent-branch}--agents-{workflow}` as the audit branch. Check
both local branch names and `git worktree list` for collisions. If that unnumbered audit branch is retained, select
the next unused zero-padded suffix, such as `{parent-branch}--agents-{workflow}-02`.

Invoke the canonical tool below. Do not create branches or worktrees directly with ad hoc shell commands. The tool is
the single source of truth for branch naming, collision handling, and repository-local placement:

```shell
python3 ~/.agents/tools/create-agent-worktree.py \
  --repository <repo-root> \
  --parent-worktree <parent-worktree> \
  --parent-branch <parent-branch> \
  --parent-base <parent-base> \
  --workflow <workflow> \
  --type <type> \
  --task-id <TASK-ID> \
  --slug <slug>
```

The tool checks the repository root, allocates the branch, and creates the matching worktree. The resulting path must
be exactly `<repo-root>/.worktrees/<agent-branch>`. It rejects temporary or sibling worktree locations and cleans up a
new branch if worktree creation fails.

Never use `/tmp`, `/private/var`, or another tool-generated temporary directory for implementation worktrees.


## Caller handoff

Return and record the resolved agent branch, agent worktree path, and whether an audit branch was created before the
caller creates artifacts, begins an investigation, or dispatches work. The caller owns all domain-specific ticket,
slug, artifact, approval, and squash decisions.
