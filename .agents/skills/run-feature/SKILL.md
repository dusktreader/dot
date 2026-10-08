# Run Feature Skill

Coordinate a full feature workflow in an isolated agent worktree. The human's current worktree
remains the integration authority throughout the run.


## When to use

Use this skill to implement a new feature or significant change end-to-end — from business
requirements through to a reviewed, tested, and PR-ready commit.

This is a standalone skill triggered directly by humans.

Do not use when:
- Fixing a known bug → use `run-bug-fix` (full) or `run-hotfix` (quick) instead
- Addressing a gap in an already-completed implementation → use `run-fix` instead
- Addressing PR review comments → use `external-review` instead
- The work is exploratory with no clear output → use `run-architecture-audit` instead

This is the only skill that manages the full feature lifecycle from shared worktree creation through
exclusive squash integration. It never pushes or creates a PR. Post-PR work uses `external-review` and
`run-hotfix`.


## Prerequisites

Your prompt must include:

- Feature description or business requirements to implement

If not provided, ask before proceeding. Do not guess.


## Worktree setup

Before creating any artifact, journal, plan, or code, and before any artifact is emitted:

1. Invoke `create-agent-worktree` with workflow identifier `feature` before any artifact.
2. Record its resolved worktree, selected regular branch, and `worktree_created` value.
3. Put every project artifact and code change in the selected worktree. Record the worktree path and regular branch in
   every later gate and handoff.

Do not create a branch without its worktree. Do not emit a plan before setup completes.


## Project directory

Before starting, derive a `{project-name}` from the feature description:

- Kebab-case, lowercase, no special characters except hyphens
- Short and descriptive, five words or fewer
- Examples: `add-user-authentication`, `refactor-payment-module`

Run branch setup first (see Git workflow below) so `{JIRA-ID}` is known, then create
`.artifacts/{YYYYMMDD}--{JIRA-ID}--{project-name}/`. Match `{JIRA-ID}` using the same rule as the
branch-setup Jira extraction below; if the branch has no ticket (no match, or it contains
`NO-TICKET`), omit the `{JIRA-ID}` segment entirely — do not write the literal text `NO-TICKET` into
the path. All artifacts for this project are stored there.

| Artifact                               | Description                                                                                |
| -------------------------------------- | ------------------------------------------------------------------------------------------ |
| `design-plan.md`                       | Design plan                                                                                |
| `design-review--{N}.md`                | Design plan review (N = zero-padded 2 digits: 01, 02, ...)                                 |
| `implementation-plan.md`               | Implementation plan                                                                        |
| `implementation-review--{N}.md`        | Implementation plan review (N = zero-padded 2 digits: 01, 02, ...)                         |
| `implementation-journal.md`            | Execution journal                                                                          |
| `execution-review--{scope-id}--{N}.md` | Execution review (scope-id = task-NN or whole-plan; N = zero-padded 2 digits: 01, 02, ...) |
| `qa-journal.md`                        | User-directed QA changes, reasons, verification, and final QA summary                      |


## Git workflow

This skill manages its own git branch and commits throughout the workflow. Follow these rules
exactly.


### Branch and integration contract

Invoke `create-agent-worktree` with workflow identifier `feature`. It owns regular branch selection and worktree
creation. This workflow never pushes, creates a pull request, or merges into `main` or `master`. Once the regular branch
is ready, tell the human to invoke `run-pr`.


### Commits after each approved stage

After the human approves each stage, commit everything staged at that point:

```shell
git add -A
git commit -m "<message>"
```

The commit message format follows `~/.agents/instructions/git.md`:

```text
<type>(<jira-id>): <short description>

- <bullet describing what was done>
- <bullet describing what was done>
```

Stage-specific commit types:
- **After design plan approved**: `docs(<jira-id>): add design plan for {project-name}`
- **After implementation plan approved**: `docs(<jira-id>): add implementation plan for {project-name}`
- **After QA approval**: `feat(<jira-id>): implement {project-name}` (or `fix`/`refactor`/`ci`
  as appropriate)

The body bullets should summarise what the stage produced — not implementation detail.

There is no agent branch, audit branch, squash, or merge step. After QA approval, the selected regular branch is
ready for `run-pr`. If `worktree_created` is true, invoke `cleanup-agent-worktree` only to remove the temporary
worktree;
never delete the regular branch.


## Workflow state machine

This state machine is the workflow contract. Detailed stage instructions define how work in each state is performed.

| State                               | Represents                                         | Transitions                                                                                                  |
| ----------------------------------- | -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| Branch setup                        | Isolated workspace creation                        | Create worktree → Design authoring                                                                           |
| Design authoring                    | Initial design-plan drafting and agent revisions   | Design agent review                                                                                          |
| Design agent review                 | Initial adversarial design review                  | Approved → Design human feedback; findings → Design authoring                                                |
| Design human feedback               | Collaborative human plan refinement                | Revisions → same state; `feedback complete` → Design final agent review                                      |
| Design final agent review           | Consolidated adversarial review of human changes   | Approved → Design final human approval; findings → same state                                                |
| Design final human approval         | Human decision on the reviewed design              | Approved → Implementation authoring; minor revision → final agent review; material revision → human feedback |
| Implementation authoring            | Initial implementation-plan drafting and revisions | Implementation agent review                                                                                  |
| Implementation agent review         | Initial adversarial implementation-plan review     | Approved → Implementation human feedback; findings → Implementation authoring                                |
| Implementation human feedback       | Collaborative human plan refinement                | Revisions → same state; `feedback complete` → Implementation final agent review                              |
| Implementation final agent review   | Consolidated adversarial review of human changes   | Approved → Implementation final human approval; findings → same state                                        |
| Implementation final human approval | Human decision on the reviewed implementation plan | Approved → Execution; minor revision → final agent review; material revision → human feedback                |
| Execution                           | Plan-directed code and test implementation         | Agent execution review                                                                                       |
| Agent execution review              | Initial adversarial review of implemented code     | Approved → Human code review or QA; findings → Execution                                                     |
| Human code review                   | Collaborative human review of code changes         | Suggestions → same state; `feedback complete` → Final agent code review; declined → QA                       |
| Final agent code review             | Consolidated adversarial review of human changes   | Approved → Final human code approval; findings → same state                                                  |
| Final human code approval           | Human decision on the reviewed code                | Approved → QA; requested changes → Final agent code review                                                   |
| QA                                  | Human testing and acceptance of the code           | Requested code change → QA after focused verification; approved → Report                                     |
| Report                              | Workflow closeout and publication handoff          | Report completion and offer `run-pr`                                                                         |

A human-feedback state is collaborative and open-ended. `feedback complete` means the human has finished
providing feedback, not that they approve the plan. Final approval is a separate, explicit signal. Treat a
revision as material when it changes scope, requirements, architecture, acceptance criteria, task sequencing, or
other plan intent. Otherwise it is minor.


## Process

### Branch setup

Before any artifact, invoke `create-agent-worktree` with the recorded parent worktree, `{parent-branch}`, immutable
`{parent-base}`, workflow identifier `feature`, and normal-branch naming data. If the parent is `main` or `master`,
ask the human for `{TASK-ID}`, derive `{type}` and `{slug}`, and provide them to the shared skill.

Extract the Jira ID from the current parent branch name:

- Match the pattern `[A-Z]+-[0-9]+` (e.g. `FUS-123`) → use it as the Jira ID
- If the branch contains `NO-TICKET` → use `NO-TICKET` as the Jira ID
- If neither matches → no Jira ID; omit the parenthetical from commit messages

All commits during stages 1–4 are made on the selected regular branch.
Continue directly to stage 1 (design) and its approval gate. Do not stop before that gate.


### Design authoring

Before each dispatch, the principal selects the active profile and tier using the principal's routing policy, records
both values, and dispatches the generic shared role through that profile's launcher. Never encode the account or model
in a specialist role name. Ask before selecting `tier:premium`; a difficult task or failed lower tier is not approval.

Dispatch the shared `architect-planner` role with the `create-design-plan` skill, the
feature description, and the project directory.


### Design agent review

Then dispatch the shared `architect-reviewer` role with the `review-design-plan` skill,
the design plan path, and iteration `01`.

Apply trivial findings directly. Apply significant and critical findings using judgment, and flag genuinely ambiguous
findings inline with the information needed from the human. Re-dispatch an `architect-reviewer` at N+1 when changes are
substantial. Repeat until the agent reviewer approves. Record each finding's outcome in its `##### Outcome` subsection.


### Design human feedback

**STOP — end your turn here.**
The design plan is ready for human feedback. Present it without summarizing the agent findings. The human-feedback
state is collaborative: address questions and requested revisions, then stop again. Do **not** dispatch a reviewer
because of a human-directed revision.

If the design plan contains an **Unknowns** section, resolve every Unknown with explicit human input during this
state. Present Unknowns one at a time, in order, and wait for each response. Fold each resolution into the plan body
and remove it from Unknowns. Do not infer answers or present more than one Unknown in a turn. Remove the section when
all Unknowns are resolved. The same rule applies to implementation plans.


### Design final agent review

Stay in the human-feedback state until the human explicitly signals that their feedback is complete, for example,
`feedback complete` or `ready for final review`. This is not approval. When that signal arrives, dispatch an
`architect-reviewer` for a consolidated review of the current plan and all accumulated revisions. Resolve final-review
findings as a batch, record outcomes, and re-dispatch only to verify material fixes until the reviewer approves.


### Design final human approval

**STOP — end your turn here.**
Only after the final agent review is approved, present the plan for final human approval. Your final output in this
turn must include this exact block, filled in:

```text
AWAITING APPROVAL: design plan
Path: {path to design-plan.md}
Unlocks: stage 2 (implementation plan) — nothing else
Still requires separate approval before it can proceed: implementation plan, QA
```

Do not proceed to planning without an unambiguous approval signal, such as `approved`, `looks good`, or `proceed`.
Silence, a question, or a request for changes is not approval. For a minor requested revision, remain in the final
review gate: revise, re-run the agent review cycle, and request approval again. For a material requested revision,
return to the human-feedback state. Do not infer approval from the absence of an objection.

When the human responds with approval, your next turn must open with:

```text
APPROVED: design plan
NOT YET APPROVED: implementation plan, QA
Proceeding to: stage 2 (create implementation plan)
```

Once approved: commit (see Git workflow — "After design plan approved").


### Implementation authoring

Dispatch the shared `engineer-planner` role with the `create-implementation-plan` skill
and the design plan path.


### Implementation agent review

Then dispatch the shared `architect-reviewer` role with the
`review-implementation-plan` skill, the implementation plan path, and iteration `01`.

Apply trivial findings directly. Apply significant and critical findings using judgment, and flag genuinely ambiguous
findings inline with the information needed from the human. Re-dispatch an `architect-reviewer` at N+1 when changes are
substantial. Repeat until the agent reviewer approves. Record each finding's outcome in its `##### Outcome` subsection.


### Implementation human feedback

**STOP — end your turn here.**
The implementation plan is ready for human feedback. Present it without summarizing the agent findings. The
human-feedback state is collaborative: address questions and requested revisions, then stop again. Do **not** dispatch
a reviewer because of a human-directed revision.


### Implementation final agent review

Stay in the human-feedback state until the human explicitly signals that their feedback is complete, for example,
`feedback complete` or `ready for final review`. This is not approval. When that signal arrives, dispatch an
`architect-reviewer` for a consolidated review of the current plan and all accumulated revisions. Resolve final-review
findings as a batch, record outcomes, and re-dispatch only to verify material fixes until the reviewer approves.


### Implementation final human approval

**STOP — end your turn here.**
Only after the final agent review is approved, present the plan for final human approval. Your final output in this
turn must include this exact block, filled in:

```text
AWAITING APPROVAL: implementation plan
Path: {path to implementation-plan.md}
Unlocks: stage 3 (execution) — nothing else
Still requires separate approval before it can proceed: QA
```

Do not proceed to execution without an unambiguous approval signal, such as `approved`, `looks good`, or `proceed`.
Silence, a question, or a request for changes is not approval. For a minor requested revision, remain in the final
review gate: revise, re-run the agent review cycle, and request approval again. For a material requested revision,
return to the human-feedback state. Do not infer approval from the absence of an objection.

When the human responds with approval, your next turn must open with:

```text
APPROVED: implementation plan
NOT YET APPROVED: QA
Proceeding to: stage 3 (execute)
```

Once approved: commit (see Git workflow — "After implementation plan approved").


### Execution

Dispatch the shared `engineer-executor` role with the
`execute-implementation-plan` skill and the implementation plan path.

After the executor completes, the orchestrator runs the project-wide quality gate exactly once. Use a constrained,
lightweight executor to fix only straightforward QA failures that are clearly within the implementation plan's scope.
The lightweight executor must not expand the work or make design decisions. Re-run the quality gate only when such a
fix changes an acceptance criterion, introduces a new code path, or changes behavior, an interface, data, security, or
tests.


### Agent execution review

Then dispatch the shared `engineer-reviewer` role with the
`review-implementation-execution` skill, the journal path, scope `whole-plan`, and iteration `01`.

Address all findings from the review:
- Apply trivial findings directly without discussion.
- Dispatch an `engineer-executor` to fix significant and critical findings. Flag genuinely
  ambiguous ones inline.
- Record the outcome in each finding's `##### Outcome` subsection.
- Re-dispatch an `engineer-reviewer` at N+1 if changes were substantial. Repeat until the
  agent reviewer approves.

If a `CHANGELOG.md` exists in the repo root, add an entry under `## Unreleased` summarising
what was implemented. Use the implementation plan's Goal as the basis. Follow the existing
entry style in the file.


### Human code review

After the initial agent execution review is approved, ask the human whether they would like to review the changes. If
they decline, proceed directly to QA. If they opt in, use any interactive diff-review capability available in the
current runtime, or present a concise diff summary through the normal review channel.

For every human suggestion, dispatch an `engineer-executor` to implement the requested code change, run the focused
quality gate, and return to this state. Do not modify plan or review artifacts, or dispatch an adversarial reviewer,
while the human continues to provide feedback.

Stay in this state until the human explicitly signals that their feedback is complete, for example, `feedback complete`
or `ready for final review`. This is not approval.


### Final agent code review

After the human completes feedback, dispatch an `engineer-reviewer` with `review-implementation-execution` at N+1.
Resolve its findings, record each outcome, and re-dispatch the reviewer only to verify substantial fixes until it
approves.


### Final human code approval

Only after the final agent code review is approved, present the code changes for final human approval. Do not proceed to
QA without an unambiguous approval signal. If the human requests changes, dispatch an `engineer-executor` to implement
them, run the focused quality gate, return to final agent code review, and then request final approval again.

**Do not squash. Do not create a PR. Proceed directly to QA after final code approval.**


### QA

This phase begins after the human declines code review or grants final human code approval.

At this stage, the agent must stop, notify the human that the code is ready for QA, and wait for testing feedback. QA
is the human approval gate for the implementation. It does not authorize a new planning or review cycle.

Tell the human that the implementation is on the selected regular branch and ready for QA. Ask them to test it
and report any issues or requested adjustments.

**STOP — end your turn here.**

Before making the first QA change, read `.agents/artifacts/qa-journal/description.md` and render
`.agents/artifacts/qa-journal/template.md.j2` as `qa-journal.md` in the project directory. Replace all
placeholder content with the implementation path and real QA details. For every user-directed change,
append an entry recording:

- The user's issue or requested adjustment
- The reason for the change
- The files changed
- Verification performed and its result

During QA, agents and subagents MUST NOT modify the design plan, implementation plan, execution
review, or any other plan or review artifact. Do not dispatch plan reviewers, reconcile the
implementation against the plans, or start an adversarial review loop. Make only the smallest
changes needed to address the user's direction.

After each change, run the focused project quality gate and ask the human to verify the result.
Wait for the human to report more work or give explicit QA approval. Issues reported, silence, or
questions are not approval.

When the human approves QA, add a concise summary of all QA changes and their reasons at the top of
`qa-journal.md`, then commit the QA changes as one approved stage.

Your final output while waiting must include this exact block:

```text
AWAITING APPROVAL: QA
Branch: {regular branch name}
QA journal: {path to qa-journal.md}
Unlocks: publication with `run-pr` — nothing else
```

When the human responds with approval, your next turn must open with:

```text
APPROVED: QA
Proceeding to: stage 5 (squash)
```


### Report

The selected regular branch is ready for `run-pr`. If `worktree_created` is true, invoke `cleanup-agent-worktree` only
to remove the temporary worktree.

**STOP — end your turn here.**
Report completion to the human with:
- The project directory path
- The selected worktree path
- The final status of each artifact
- The regular branch name
