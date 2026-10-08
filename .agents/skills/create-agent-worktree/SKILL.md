# Create agent worktree

Create the regular branch and repository-local worktree used by branch-based workflows.

## Required inputs

The caller provides the repository root, parent worktree path, parent branch, immutable parent base SHA, workflow
identifier, and normal-branch naming data when the parent is `main` or `master`. Normal-branch data includes
`{type}`, `{TASK-ID}`, and `{slug}`.

## Creation policy

Record the parent worktree, parent branch, and immutable parent base before creating anything. Never use `git switch`
or otherwise mutate the human worktree.

When the parent is `main` or `master`, create the regular `{type}/{TASK-ID}--{slug}` branch from `{parent-base}` and
create its worktree beneath `<repo>/.worktrees/`. This is the branch that will be published by `run-pr`.

When the parent is already a regular branch, use that branch and its existing parent worktree directly. Do not create
an agent branch, audit branch, second worktree, squash, or merge. Agents must work from the selected regular branch.

Invoke the canonical tool below. Do not create branches or worktrees directly with ad hoc shell commands:

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

The tool checks the repository root, creates a regular branch and worktree only when starting from `main` or `master`,
and returns the selected branch and worktree. The resulting worktree is beneath `<repo>/.worktrees/` when one is created.

Never use `/tmp`, `/private/var`, or another tool-generated temporary directory for implementation worktrees.

## Caller handoff

Return and record the resolved branch, worktree path, and `worktree_created` value before the caller creates artifacts,
begins an investigation, or dispatches work. The caller owns domain-specific ticket, slug, artifact, approval, and
publishing decisions. All work proceeds directly on the selected regular branch; there is no agent-branch integration step.
