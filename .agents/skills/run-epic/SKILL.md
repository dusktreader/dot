# Run Epic Skill

Coordinate a multi-feature initiative through an approved epic plan, complete slice design sets, sequential feature
lifecycles, integrated human acceptance, and roadmap decisions. The epic coordinator owns product-level
scope and slice readiness; `run-feature-lifecycle` owns feature-level gates.


## When to use

Use this workflow for a new project or substantial expansion that requires several independently deliverable features
coordinated into an MVP and later roadmap. A single significant cohesive deliverable belongs in `run-feature`. Existing
bug, fix, hotfix, task, PR, hack, and external-review workflows remain unchanged.


## Prerequisites

The request must provide an initiative outcome or business requirements and repository context when the work affects an
existing project. Obtain missing product decisions from the human; do not infer them. Do not
create the epic artifact until the selected worktree and regular branch are recorded.


## Worktree and branch ownership

Before emitting any epic or feature artifact, invoke the shared `create-agent-worktree` skill with the repository root,
selected parent worktree, parent branch, immutable parent base, workflow `epic`, and normal-branch naming data when the
parent is `main` or `master`. Record the resolved regular branch, worktree path,
and `worktree_created` result in the epic plan and coordinator context.

When starting from `main` or `master`, use the tool-created regular branch and worktree. When starting from an existing
regular branch, use that selected branch and worktree directly. Never create a nested child worktree. Run every feature
lifecycle inside the coordinator-owned slice worktree and never alter the human's worktree.

After an accepted slice is handed to `run-pr`, later roadmap slices remain planned entries in the same epic plan. Resume
`run-epic` with the existing epic artifact directory and the accepted integrated product state. Create the later slice's
feature artifacts under that epic's established feature paths and update the same epic register. Never create a second
epic artifact directory for the same initiative. If prerequisite acceptance or the integrated product
state is unavailable, keep the slice blocked and emit no slice-specific artifacts.

Do not create branches or worktrees directly or through ad hoc
commands. Do not give feature lifecycles worktree ownership.


## Artifact topology

Use one epic directory: `.artifacts/{YYYYMMDD}--{epic-name}/`. Store `epic-plan.md`, `epic-review--NN.md`, and
`epic-deviation--NN.md` there. The plan title and register identify the epic and all slice records.

Give each feature a stable zero-padded `FNN` identifier. Its separate artifact directory is
`.artifacts/{YYYYMMDD}--{epic-name}--FNN-{feature-name}/`. Link that path from the epic register. Repeat `FNN` in each
feature plan title, review title, journal, deviation record, QA journal, and relevant metadata. Feature designs,
implementation plans, reviews, journals, deviations, and QA records stay in the
feature directory. Do not embed detailed feature artifacts in `epic-plan.md`.

Use `T01` for the MVP and `T02`, `T03`, and later IDs for approved delivery slices. Each slice register entry records
its objective, included features, prerequisite slices, state, verification
result, artifact links, coordinator branch, and coordinator worktree.


## Approval and commit policy

The epic plan is a planning artifact. Dispatch the shared `architect-planner` role with `create-epic-plan`, then the
shared `architect-reviewer` role with `review-epic-plan`. Resolve findings and record outcomes. Stop for explicit human
approval before child feature planning. Re-review material changes. Renew approval for material changes to
outcome, scope, MVP boundary, feature sequencing, or cross-cutting architecture.

Before any implementation planning or code in a slice, complete and fully review a design plan for every included
feature. Present the complete, individually reviewed design set together and obtain one explicit human approval for that
exact set. Then run a scoped final blocker check on each approved design; do not request separate per-feature design
approvals. No feature implementation plan begins until every check passes. Commit the
approved epic plan and each approved slice design set on the coordinator branch.

Each feature receives one human approval of its exact revised implementation plan, followed by a scoped final blocker
check. A passing check opens execution without another human gate. Preserve execution review, code review option, QA,
and plan immutability. Commit each approved feature implementation plan. After the human accepts feature QA and verifies
the feature outcome, commit the completed feature stage and any human-approved QA changes.

Commit only approved stages. After the integrated slice outcome receives explicit human acceptance, make the final
approved slice commit. Never automatically publish, push, create a pull request, squash, merge, or delete the regular
branch. After epic completion, conditionally invoke `cleanup-agent-worktree` only when
`worktree_created` is true, then hand the selected regular branch to `run-pr`.


## Workflow state machine

| State                               | Gate and transition                                                                              |
| ----------------------------------- | ------------------------------------------------------------------------------------------------ |
| Worktree setup                      | Shared tool returns selected regular branch, worktree, and creation flag before artifacts        |
| Epic authoring                      | Create epic plan and product-level feature/slice registers                                       |
| Epic agent review                   | Resolve findings and repeat review when changes are material                                     |
| Epic human approval                 | Stop for explicit approval; material product changes renew this gate                             |
| Slice design authoring              | Create and fully review every included feature design                                            |
| Slice agent review                  | Review cross-feature dependencies, integration, ordering, and slice readiness                    |
| Slice human approval                | Approve the exact complete design set once                                                       |
| Slice final design check            | Check approved designs for major blockers; material changes renew affected set approval          |
| Feature implementation planning     | Author plans from immutable designs and current slice approval evidence                          |
| Feature plan agent review           | Resolve full-review findings and repeat review when changes are material                         |
| Feature plan human approval         | Approve the exact revised feature plan once                                                      |
| Feature final plan check            | Check major blockers; pass opens execution, blockers return to human review                      |
| Feature execution                   | Execute the approved feature plan and record the implementation journal                          |
| Feature agent review                | Review implementation against the feature plan and resolve findings                              |
| Feature human review                | Present completed feature changes for human review before QA                                     |
| Feature QA and verification         | Human approves QA and verifies this feature before the next feature starts                       |
| Integrated slice agent verification | Verify every slice success criterion against the integrated product and resolve findings         |
| Integrated slice human verification | Human verifies every slice success criterion after agent verification passes                     |
| Slice acceptance                    | Record explicit acceptance and roadmap decision; only accepted prerequisites unlock later slices |
| Later-slice setup                   | Validate prerequisite acceptance and resume the established epic artifact directory              |
| Handoff                             | Final approved commit, conditional worktree cleanup, and `run-pr` handoff                        |

Resolve Unknowns one at a time with the human. Obtain explicit approval of the epic plan and each complete slice design
set. Silence, questions, reviewer approval, or approval of an individual design do not substitute for these gates.


## Slice lifecycle

### Epic plan

Inspect the existing repository where applicable. Identify independently deliverable features, stable `FNN` IDs,
dependencies, sequencing, product-level cross-cutting decisions, and the smallest useful T01 MVP. Keep later features as
briefs until a roadmap slice is approved. Read `.agents/artifacts/epic-plan/description.md` and render
`.agents/artifacts/epic-plan/template.md.j2`; replace every template value and example.
Create only `epic-plan.md` at this stage. Run `dt format markdown` before review.

Review using `.agents/artifacts/epic-review/description.md` and its template. Reviews use `epic-review--NN.md`, unique
findings with severity, evidence, impact, concrete resolution, outcome, and prior-review
resolution. The agent review does not approve the epic plan for the human.


### Complete slice design set

For every feature included in the current slice, invoke `.agents/skills/run-feature-lifecycle/SKILL.md` with explicit
context: `execution_mode=epic`, `entry_stage=design`, its `FNN`, the parent `epic-plan.md`, its identifier-bearing
feature directory, selected regular branch, and coordinator worktree. The lifecycle creates and fully agent-reviews the
feature design; it does not request a separate per-feature human approval.
The coordinator retains all detailed artifacts in the child directory.

After every design has passed its full individual review, present the complete set for one explicit human approval.
Record the approved feature IDs, exact design revisions, and approval evidence in the epic plan. Then request a scoped
final blocker check for each design against that set. If a blocker requires a material design change, return it to human
review, invalidate the affected set approval, and pause dependent implementation until the affected complete set is
approved again and its blocker check passes. Commit the slice design set only after every final check passes.


### Sequential feature delivery

Process features in the approved dependency order, one at a time. For each feature, invoke the shared lifecycle in epic
mode at `entry_stage=implementation-planning`, passing its immutable individually approved design, final blocker-check
result, current slice design-set approval evidence, parent epic path, `FNN`, feature directory, selected branch, and
worktree. The lifecycle must reject missing or stale approval evidence. Complete the plan's full agent review, obtain
one human approval of the exact revised plan, and pass its final blocker check before
execution. Commit the plan after that check passes; do not add another human gate.

Dispatch the shared `engineer-executor` role through the principal-selected profile and tier for execution, and the
shared `engineer-reviewer` role for execution review. Preserve all lifecycle code-review, plan-immutability, deviation,
and QA gates. Do not begin the next feature when the current feature
lacks explicit human QA approval and outcome verification.

After each feature's QA, stop for human verification of that feature's outcome. Ask the human to check its acceptance
criteria and report pass or fail. A failure returns only that feature to its existing QA and deviation controls. Record
the result and evidence in its feature records and update its FNN state in the epic plan before proceeding.


### Feature and epic deviations

After feature execution starts, do not edit approved child plans. Record each material departure in that feature's
`plan-deviations.md`. If it affects slice scope, dependencies, sequencing, success criteria, integration, or another
feature, also create an epic-wide record from `.agents/artifacts/epic-deviation/description.md` and its template as
`epic-deviation--NN.md`. Link the feature deviations and epic record from their respective artifacts and the epic plan.

The epic deviation identifies affected `FNN` and `TNN` IDs, product-level impact, affected dependencies, pause or
continuation decision, renewed approval requirements, and verification. Pause affected unfinished dependent work until
the impact assessment and required approval complete. Verify changed
work through feature QA and integrated slice verification.


### Integrated verification and roadmap

After every slice feature passes individual human verification, stop for full integrated human verification against
every success criterion in the slice and epic plan. Ask for an explicit pass or fail for each criterion. Record the
evidence and integrated result in the epic plan. Any unmet criterion blocks slice closure and all dependent later
slices; return only affected work to its existing feature QA and deviation controls.

After all criteria pass, obtain explicit human acceptance and a roadmap decision. T01 acceptance is required before
starting any dependent T02+ slice. Do not mark deferred features complete. An approved later slice starts as a new
`run-epic` run from the accepted integrated prerequisite state and
repeats the complete design-set and feature lifecycle gates.


## Specialist dispatch

Before each dispatch, the principal selects the active profile and tier using the principal routing policy. Use generic
shared specialist roles through the selected launcher; never encode an account or model in a role name. Epic-plan
creation and review use the shared `architect-planner` and `architect-reviewer` roles. Feature design, planning,
execution, and review use the generic roles required by `run-feature-lifecycle`.


## Completion

Do not close a slice until every feature and integrated criterion passes and the human explicitly accepts the outcome.
Record the roadmap decision, selected coordinator branch and worktree, `worktree_created`, and links to epic and feature
artifacts. Make the final approved commit, conditionally clean up only the created worktree, and hand the selected
regular branch to `run-pr`. The workflow does not publish or create a pull request.
