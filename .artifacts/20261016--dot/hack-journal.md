# Share Git command execution

This journal records the shared Git command helper refactor and its verification.


## Change

- Moved `_run_git` into `src/dot_tools/git_tools.py` and made it wrap Git failures with command and diagnostic context.
- Reused the helper in `worktree_tools.py` and for Git staging/status in `GitManager.resolve_conflicts`.
- Added tests for standard output, Git command failures, launch failures, and conflict-resolution Git calls.
- Corrected the worktree summary helper to call the imported `inflection.parameterize` function.


## Verification

- `uv run pytest`: 453 passed.
- `uv run ruff check src tests`: passed.
- `uv run ty check src/dot_tools/git_tools.py src/dot_tools/worktree_tools.py`: passed.
- Whole-repository `uv run ty check` still reports existing diagnostics outside these changes.
