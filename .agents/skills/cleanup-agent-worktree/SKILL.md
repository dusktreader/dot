# Cleanup agent worktree

Clean up a worktree created from `main` or `master` after the workflow's completion gate succeeds.

## Required inputs

The caller provides the creation result and exact worktree path when `worktree_created` is true.

## Cleanup policy

If `worktree_created` is false, do nothing. The workflow used the selected regular parent worktree, so there is no
separate worktree or branch to remove.

If `worktree_created` is true, remove only the supplied worktree with `git worktree remove <agent-worktree>` and verify
that exact path is absent from `git worktree list`. Never delete the regular branch automatically.

Declined integration, abandoned work, and regeneration paths remain caller-controlled. Never delete branches unless the
human explicitly requests it.
