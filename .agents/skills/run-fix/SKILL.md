# Run Fix Skill

Apply a human-authorized, understood fix. This thin wrapper owns worktree and artifact setup, commits, and final
reporting; `.agents/procedures/apply-fix.md` owns the fix lifecycle.


## When to use

Use when the human understands the defect or missed requirement and explicitly requests a targeted fix. Use `triage-bug`
first when diagnosis is needed; triage must return explicit human authorization to remediate before this workflow
proceeds. Use `run-task` for bounded non-bug changes, `run-feature` for new or broad feature work, and `external-review`
for PR review feedback.


## Prerequisites

The prompt must include the fix description and indicate the expected outcome. Ask if either is unclear.


## Workflow phases

### Setup

Invoke `.agents/procedures/use-worktree.md` with branch type `fix`, a concise summary, and ticket if provided. Work only
in the selected worktree.

Invoke `.agents/procedures/use-artifact-dir.md` in the selected worktree with the same summary, `branch_type=fix`, and
ticket used for `use-worktree`. Use its returned path for all fix artifacts.


### Fix lifecycle

Invoke `.agents/procedures/apply-fix.md` once with `fix_origin=standalone`, `entry_stage=plan`, `exit_stage=qa`, the
human fix request, fix artifact directory, and selected worktree/branch.


### Completion

After QA approval and the caller-owned QA commit, report the fix artifact directory, branch/worktree, review outcome, QA
status, and artifact paths. Leave the worktree and branch intact. Suggest a new session for follow-on work; the
artifacts provide sufficient context. Do not push, publish, create a pull request, merge, or squash.
