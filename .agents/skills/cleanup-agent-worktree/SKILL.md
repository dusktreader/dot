# Cleanup agent worktree

Clean up the shared worktree boundary only after successful integration has completed.


## Required inputs

The caller provides the creation result and exact agent worktree path after its stale-parent check, approved squash,
and any workflow-specific completion gate have succeeded. The creation result identifies whether an audit branch exists.


## Cleanup policy

Remove only the supplied agent worktree with `git worktree remove <agent-worktree>`. Verify that exact path is absent
from `git worktree list`. If the creation result contains an audit branch, verify it remains with `git branch --list`.
Otherwise, report that no temporary audit branch was created because the normal branch was created directly from `main`
or `master`.

Audit branch deletion is forbidden unless the human explicitly requests it. Declined integration, abandoned work, and
regeneration paths remain caller-controlled and do not trigger automatic cleanup. Preserve both the agent worktree and
audit branch until explicit human cleanup when the workflow does not reach successful integration.
