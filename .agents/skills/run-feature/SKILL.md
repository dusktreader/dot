# Run Feature Skill

Coordinate a standalone feature from design through QA on its selected regular branch. The shared `build-feature`
procedure owns feature-level stage gates; this wrapper owns standalone worktree setup, approved-stage commits, and the
final `run-pr` handoff.


## When to use

Use this skill for one significant, cohesive feature or change that needs design, implementation planning, execution
review, and human QA. A multi-feature initiative with an MVP and roadmap belongs in `run-epic`. Bug, fix, task, PR, and
external-review requests retain their existing workflows.

This is a standalone skill triggered directly by humans. Epic coordination invokes `build-feature` directly and does not
nest this wrapper.


## Prerequisites

The prompt must include a feature description or business requirements. If missing, ask before proceeding.


## Workflow state machine

### Worktree setup

Before any artifact is created, or before a journal, plan, or code change:

1. Invoke the `use-worktree` procedure with the `feat` branch type, a terse summary of the task, and ticket collected
   from the user.
2. Record the resolved worktree and branch.
3. Work only in that worktree. Make changes there and put artifacts there. Do not create a nested worktree! Do not make
   changes in the project root!

The `use-worktree` procedure owns branch selection and creation. Never create branches or worktrees with ad hoc Git
commands.


### Feature lifecycle

After branch setup, invoke `.agents/procedures/use-artifact-dir.md` in the selected worktree with the same summary and
ticket used for `use-worktree` and `branch_type=feat`. Keep all feature artifacts in the returned directory. Follow the
artifact names and inventory in `.agents/procedures/build-feature.md`.

Invoke `.agents/procedures/build-feature.md` with `execution_mode=standalone`, `entry_stage=design`, `exit_stage=qa`,
the project artifact directory, `feature_id=None`, `parent_epic_artifact=None`, and the selected branch and worktree.
Follow the procedure for all feature lifecycle stages and gates; it owns the deviation journal.

The selected worktree branch is the work branch. Commit each approved plan stage after its human approval and passing
final blocker check. Use commit messages from `~/.agents/instructions/git.md` with stage type `docs` for approved design
and implementation plans. Do not commit review feedback or unapproved plans.


### QA approval

Wait for explicit human QA approval before closing the feature. The `build-feature` procedure records all QA changes in
`plan-deviations.md`; commit approved QA changes using `feat`, `fix`, `refactor`, or `ci` as appropriate. Do not commit
unapproved QA changes.


### Handoff

After explicit QA approval, report the project directory, selected worktree/branch, and final artifact status. Leave the
worktree and branch intact. Hand the branch to the human for `run-pr`; do not push, publish, create a PR, squash, merge,
or delete the branch.
