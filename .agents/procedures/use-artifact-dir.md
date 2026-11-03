# Use Artifact Directory

Create or reuse one dated artifact directory for a task using the same inputs as its worktree selection.


## Required inputs

Provide the same `summary`, `branch_type`, and optional `ticket` used with `.agents/tools/use-worktree.py`. When
resuming an existing worktree, use the exact inputs that selected its branch.


## Create or reuse the directory

From the selected worktree, run `.agents/tools/create-artifact-dir.py` with the same values:

```shell
.agents/tools/create-artifact-dir.py --type fix --ticket ABC-123 "Fix close leak"
```

Omit `--ticket` when none was provided to `use-worktree.py`. The tool builds the directory key directly from
`branch_type`, optional `ticket`, and normalized `summary`; it does not inspect or construct a branch name. It returns
the absolute `.artifacts/{YYYYMMDD}--{artifact-key}` path.

The tool reuses the unique existing dated directory for that task. If multiple matching directories exist, stop and ask
the human which directory to keep; do not choose one or create another.


## Pass the path to contributors

Record the returned path and pass it unchanged to every agent, procedure, and workflow stage that writes artifacts. Do
not reconstruct the path or derive a new date. When resuming a workflow, run the tool again with the original inputs to
recover the existing path.

For workflows that do not create a worktree, provide the task's branch type, summary, and ticket, and run the tool from
the intended worktree.
