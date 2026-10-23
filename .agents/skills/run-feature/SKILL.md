# Run Feature Skill

Coordinate a standalone feature from design through QA on its selected regular branch. The shared
`run-feature-lifecycle` skill owns feature-level stage gates; this wrapper owns standalone
worktree setup, approved-stage commits, and the final `run-pr` handoff.


## When to use

Use this workflow for one significant, cohesive feature or change that needs design, implementation planning, execution
review, and human QA. A multi-feature initiative with an MVP and roadmap belongs in `run-epic`. Bug,
fix, hotfix, task, PR, and external-review requests retain their existing workflows.

This is a standalone skill triggered directly by humans. Epic coordination
invokes `run-feature-lifecycle` directly and does not nest this wrapper.


## Prerequisites

The prompt must include a feature description or business requirements. If missing, ask before proceeding.


## Worktree setup

Before any artifact is created, or before a journal, plan, or code change:

1. Invoke `create-agent-worktree` with workflow identifier `feature`.
2. Record the resolved worktree, selected regular branch, and `worktree_created` value.
3. Put every project artifact and code change in that selected worktree.
   Do not create a nested worktree or mutate the human's worktree.

The shared worktree tool owns branch selection and creation.
Never create branches or worktrees with ad hoc Git commands.


## Project directory and artifacts

Derive a short lowercase kebab-case project name from the feature description. After branch setup, create
`.artifacts/{YYYYMMDD}--{JIRA-ID}--{project-name}/`. If the branch has no ticket or contains
`NO-TICKET`, omit the ticket segment. Keep all artifacts in that directory.

| Artifact                              | Description                                   |
| ------------------------------------- | --------------------------------------------- |
| `design-plan.md`                      | Feature design                                |
| `design-review--NN.md`                | Individual design reviews                     |
| `implementation-plan.md`              | Feature implementation plan                   |
| `implementation-review--NN.md`        | Implementation-plan reviews                   |
| `implementation-journal.md`           | Execution journal                             |
| `plan-deviations.md`                  | Human-directed departures from approved plans |
| `execution-review--{scope-id}--NN.md` | Execution reviews                             |
| `qa-journal.md`                       | User-directed QA changes and verification     |

A standalone feature may have an optional parent epic path and stable `FNN` identifier. Record both when supplied, but
do not require them for direct standalone use. Use `FNN` consistently in the feature plan title, review titles, journal,
deviation and QA records, and epic linkage. Detailed feature artifacts stay in this feature directory.


## Git workflow

The selected regular branch is the work branch. All approved-stage commits occur on it. Never push, create a pull
request, or merge into `main` or `master`; the human invokes `run-pr` after completion. Use commit messages from
`~/.agents/instructions/git.md` with stage types `docs` for approved design and implementation
plans, and `feat`, `fix`, `refactor`, or `ci` as appropriate for approved QA changes.

After the single human approval and passing final blocker check for each plan, commit that approved stage. After QA
approval, commit QA changes. Do not commit review feedback, unapproved plans, or unapproved QA changes. If
`worktree_created` is true, invoke `cleanup-agent-worktree` only after the workflow
closes and only to remove the worktree; never delete the regular branch.


## Process

### Branch setup

Inspect the parent worktree and branch. If the parent branch is `main` or `master`, obtain the required task ID and
branch naming data from the human. Otherwise reuse the selected regular branch and existing worktree. Invoke
`create-agent-worktree` with the parent worktree, parent branch, immutable parent base, workflow identifier `feature`,
and naming data when required. Record its complete result before emitting artifacts.

Extract a ticket ID matching `[A-Z]+-[0-9]+` from the parent branch. Use `NO-TICKET`
when present; otherwise omit the ID from artifact paths and commit messages.


### Standalone lifecycle

Invoke `.agents/skills/run-feature-lifecycle/SKILL.md` with explicit context:

- `execution_mode`: `standalone`
- `entry_stage`: `design`
- `feature_artifact_dir`: the project directory above
- `feature_id`: the supplied `FNN` identifier or explicit `None`
- `parent_epic_artifact`: the supplied epic-plan path or explicit `None`
- Selected regular branch and worktree, plus `worktree_created`

The lifecycle begins with design authoring and applies the individual design, implementation-plan, execution-review,
code review, and QA gates. Require one explicit human approval of each revised plan before its scoped final blocker
check; a passing check proceeds without a second human approval. Preserve the other applicable gates. The principal
selects the profile and tier before dispatch using the principal's routing policy, then uses the shared
`architect-planner` role, shared `architect-reviewer` role, and the generic shared lifecycle roles through the selected
profile's launcher. Do not encode account or model names in role names.
The wrapper commits approved plan stages as described above.


### Report and handoff

After explicit QA approval, report the project directory, selected worktree, regular branch, and final artifact status.
If `worktree_created` is true, conditionally invoke `cleanup-agent-worktree` to remove the temporary worktree. Hand the
clean regular branch to the human for `run-pr`; do not publish, create a PR, squash, merge, or delete the branch.
