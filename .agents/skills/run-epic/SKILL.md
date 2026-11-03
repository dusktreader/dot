# Run Epic Skill

Coordinate a multi-feature initiative through an approved epic plan, complete slice design sets, sequential feature
lifecycles, integrated human acceptance, and roadmap decisions. The epic coordinator owns product-level scope and slice
readiness; `build-feature` procedure owns feature-level gates.


## When to use

Use this workflow for a new project or substantial expansion that requires several independently deliverable features
coordinated into an MVP and later roadmap. A single significant cohesive deliverable belongs in `run-feature`. Existing
bug, fix, task, PR, hack, and external-review workflows remain unchanged.


## Prerequisites

The request must provide an initiative outcome or business requirements and repository context when the work affects an
existing project. Obtain missing product decisions from the human; do not infer them. Do not create the epic artifact
until the selected worktree and regular branch are recorded.


## Artifact topology

Use `.agents/procedures/use-artifact-dir.md` in the coordinator worktree to obtain the epic artifact directory. Store
`epic-plan.md`, `epic-review--NN.md`, and `epic-deviation--NN.md` there. The plan title and register identify the epic
and all slice records.

Give each feature a stable zero-padded `FNN` identifier. Store its detailed artifacts in an `FNN-{feature-name}/`
subdirectory beneath the epic artifact directory and link that path from the epic register. Repeat `FNN` in each feature
plan title, review title, journal, deviation record, and relevant metadata. Do not embed detailed feature artifacts in
`epic-plan.md`.

Use `T01` for the MVP and `T02`, `T03`, and later IDs for approved delivery slices. Each slice register entry records
its objective, included features, prerequisite slices, state, verification result, artifact links, coordinator branch,
and coordinator worktree.


## Workflow state machine

### Worktree setup

Before creating artifacts or making plan, journal, or code changes:

1. Invoke `.agents/procedures/use-worktree.md` with `branch_type=feat`, a terse summary of the initiative, and ticket
   collected from the user.
2. Record the resolved worktree, branch, `worktree_created` value, summary, and ticket.
3. Invoke `.agents/procedures/use-artifact-dir.md` with the same `branch_type`, summary, and ticket.
4. Work only in that worktree and returned artifact directory. Do not create a nested worktree or make changes in the
   project root.

The `use-worktree` procedure owns branch selection and creation. Never create branches or worktrees with ad hoc Git
commands.


### Epic authoring

Invoke `.agents/procedures/create-epic-plan.md` with the initiative outcome, epic artifact directory, and repository
context. It owns repository inspection, product decomposition, MVP and roadmap definition, and authoring `epic-plan.md`.

Commit the approved epic plan on the coordinator branch after the epic-plan approval state passes.


### Epic agent review

Invoke `.agents/procedures/review-epic-plan.md` with the plan path, epic artifact directory, review iteration, and
prior review path when applicable. Resolve findings and repeat review after material revisions. The agent review does
not approve the epic plan for the human.


### Epic human approval

Resolve Unknowns one at a time with the human. Obtain explicit approval of the epic plan before child feature planning.
Renew approval for material changes to outcome, scope, MVP boundary, feature sequencing, or cross-cutting architecture.
Questions, reviewer approval, or silence do not constitute approval.


### Slice design set

A slice is a planned delivery increment: a selected set of features that together achieve a meaningful product outcome.
Its feature breakdown, prerequisites, and acceptance criteria are recorded in the epic plan; keep detailed feature
designs in their separate feature artifacts.

For every feature included in the current slice, invoke `.agents/procedures/build-feature.md` with
`execution_mode=epic`, `entry_stage=design`, and `exit_stage=design`, plus its `FNN`, the parent `epic-plan.md`, its
identifier-bearing feature directory, selected regular branch, and coordinator worktree. The procedure creates the
feature design, then returns control for the coordinator to assemble the design set.

Before feature implementation begins, the feature procedure creates `plan-deviations.md` from the approved design and
implementation plans in each feature directory. It records every post-plan implementation, code-review, and QA change,
whether or not the change departs from plan.

After every design passes its full individual review, present the complete set for one explicit human approval. Record
the approved feature IDs, exact design revisions, and approval evidence in the epic plan. Then run a scoped final
blocker check for each design against that set; do not request separate per-feature design approvals. If a blocker
requires a material design change, return it for human review, invalidate the affected set approval, and pause dependent
implementation until the affected set is approved again and its blocker check passes. Commit the slice design set only
after every final check passes.


### Sequential feature delivery

Process features in the approved dependency order, one at a time. For each feature, invoke
`.agents/procedures/build-feature.md` with `execution_mode=epic`, `entry_stage=implementation-planning`, and
`exit_stage=qa`, passing its immutable individually approved design, final blocker-check result, current slice
design-set approval evidence, parent epic path, `FNN`, feature directory, selected branch, and worktree. The procedure
rejects missing or stale approval evidence and runs the feature through QA. Commit each approved feature implementation
plan and approved QA changes on the coordinator branch. Do not commit review feedback or unapproved plans or QA changes.

Do not begin the next feature until the procedure returns QA approval and the human verifies the feature outcome. Record
the verification and update its `FNN` state in the epic plan.


### Feature and epic changes

The feature deviation journal records all human-directed implementation, code-review, and QA changes, whether or not
they depart from the approved plans. If a recorded change affects slice scope, dependencies, sequencing, success
criteria, integration, or another feature, create an epic-wide record from
`.agents/artifacts/epic-deviation/description.md` and its template as `epic-deviation--NN.md`. Link the feature journals
and epic record from their respective artifacts and the epic plan.

The epic record captures affected `FNN` and `TNN` IDs, product-level impact, affected dependencies, pause or
continuation decision, renewed approval requirements, and verification. Pause affected unfinished dependent work until
the impact assessment and required approval complete. Verify changed work through feature QA and integrated slice
verification.


### Integrated slice agent verification

After every slice feature passes individual human verification, verify every slice success criterion against the
integrated product. Resolve findings through the affected feature QA and deviation controls. Any unmet criterion blocks
slice closure and dependent later slices.


### Integrated slice human verification

After agent verification passes, ask the human to check every success criterion in the slice and epic plan. Record
verification evidence and the integrated result in the epic plan. An unmet criterion blocks slice closure.


### Slice acceptance

After all criteria pass, obtain explicit human acceptance and a roadmap decision. Record them in the epic plan and
commit the integrated slice outcome. T01 acceptance is required before starting any dependent T02+ slice. Do not mark
deferred features complete. An approved later slice starts as a new `run-epic` run from the accepted integrated
prerequisite state and resumes the established epic artifact directory. If prerequisite acceptance or the integrated
product state is unavailable, keep the slice blocked and emit no slice-specific artifacts.


### Handoff

Do not push, publish, create a pull request, squash, merge, or delete any branches. Handoff the branch/wortree to the
`run-pr` skill.


## Specialist dispatch

Before each dispatch, the principal selects the active profile and tier using the principal routing policy. Use generic
shared specialist roles through the selected launcher; never encode an account or model in a role name. Epic-plan
creation and review use the shared `architect-planner` and `architect-reviewer` roles. Feature design, planning,
execution, and review use the generic roles required by `build-feature`.
