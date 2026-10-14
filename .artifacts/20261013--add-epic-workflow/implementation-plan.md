# Implementation Plan: Add epic workflow

Add a planning and coordination workflow for multi-feature projects. The workflow will create and govern a durable epic
artifact, produce complete designs for the committed MVP feature set before implementation begins, and retain concise
feature briefs for later roadmap work. It will keep `run-feature` usable as the direct, standalone
workflow while providing a shared lifecycle contract for epic-owned feature execution.


## Goal

Introduce `run-epic` as the workflow for a new or substantially expanded project whose outcome requires several
independently deliverable features. An epic plan will define the total outcome, MVP boundary, discrete `FNN` feature
identifiers, feature dependencies, roadmap sequencing, and post-MVP feature briefs. Every MVP feature will
have a reviewed design plan before any MVP implementation plan or code work starts.

Keep detailed artifacts scoped to their feature. `epic-plan.md` will link every feature ID to its artifact directory and
summarize the feature's state, but will not embed the feature's design, implementation, review, journal, or QA records.
Post-MVP features remain briefs until they enter an approved planning tranche, avoiding speculative design artifacts.


## Project Commands

### Format Markdown

Command:

```shell
dt format markdown .agents .artifacts/20261013--add-epic-workflow
```

Expected Output:

All changed Markdown skill, artifact, and planning files are formatted without errors.


### Run policy-validator tests

Command:

```shell
uv run pytest tests/test_validate_staged_agent_policies.py -v
```

Expected Output:

The policy validator accepts the complete fixture set and rejects
fixtures that omit the epic workflow's required controls.


### Run the full test suite

Command:

```shell
uv run pytest
```

Expected Output:

All repository tests pass.


### Run lint and type checks

Command:

```shell
uv run ruff check src tests
uv run ty check
```

Expected Output:

Ruff reports no violations and `ty` reports no type errors.


----

## Project Standards

- [`AGENTS.md`](../../AGENTS.md)
- [Repository guide](../../.dot_agents/dot.md)
- [System-wide agent instructions](../../.agents/README.md)
- [Markdown style guide](file:///Users/tucker.beck/.agents/instructions/markdown.md)
- [File editing safety](file:///Users/tucker.beck/.agents/instructions/editing.md)
- [Git safety](file:///Users/tucker.beck/.agents/instructions/git-safety.md)
- [Python style guide](file:///Users/tucker.beck/.agents/instructions/python.md)
- [Existing standalone feature workflow](../../.agents/skills/run-feature/SKILL.md)
- [Shared worktree contract](../../.agents/skills/create-agent-worktree/SKILL.md)


## Relevant Skills

- `create-design-plan`
- `create-implementation-plan`
- `review-design-plan`
- `review-implementation-plan`
- `review-implementation-execution`
- `investigate-codebase`


## Execution

### 01: Define the epic artifact contract

Add the canonical `epic-plan` artifact definition and template. Establish it as the product-level record that owns the
feature register and MVP/roadmap progression, while retaining detailed work in feature-specific artifacts.


#### Acceptance Criteria

- AC01: The artifact definition distinguishes the epic-level outcome, scope, non-goals, success criteria,
  risks, and closure criteria from child feature design and implementation detail.
- AC02: Every feature entry uses a stable, zero-padded `FNN` identifier and records its
  outcome, tranche, priority, dependencies, state, and linked artifact directory.
- AC03: The template contains a tranche register: `T01` for the MVP and `T02+` for later approved delivery slices. Each
  tranche records its objective, included features, dependencies, state, verification
  result, artifact links, and coordinator-owned branch and worktree.
- AC04: The template contains a dedicated `T01` MVP feature set and post-MVP roadmap briefs. It documents that every
  committed MVP feature requires a complete, reviewed design plan before implementation planning or code begins.
- AC05: Artifact paths are unambiguous: an epic artifact directory contains `epic-plan.md`; each child feature has a
  separate identifier-bearing artifact directory rather than embedded detailed artifacts.


#### Steps

1. Create the implementation journal from its canonical template and record each task,
   changed file, command, and verification result from the start of execution.
2. Create `.agents/artifacts/epic-plan/description.md` with section definitions for goal, scope, success criteria,
   architecture and cross-cutting decisions, feature and tranche registers, `T01`
   MVP plan, roadmap, dependencies, risks, unknowns, and closure criteria.
3. Create `.agents/artifacts/epic-plan/template.md.j2` using the canonical headings and feature-register tables with
   explicit `FNN` identifiers and artifact links, plus a tranche register with `T01` and post-MVP `T02+` fields.
4. Create `.agents/artifacts/epic-review/description.md` and `template.md.j2`, defining the source artifact, severity
   findings, outcomes, prior-review resolution, and re-review contract for `epic-review--NN.md`.
5. Specify the naming convention for an epic directory and child feature directories, including how the feature ID is
   carried in the directory name, plan title, review title, journal, and epic register.
6. Add `epic-plan/` and `epic-review/` to the artifact catalog in `.agents/README.md`.
7. Format the new and changed Markdown files.


### 02: Add epic planning and review skills

Create focused skills for authoring and adversarially reviewing `epic-plan.md`. Do not overload design-plan
skills, because an epic plan has a distinct artifact contract and review concerns.


#### Acceptance Criteria

- AC01: `create-epic-plan` requires a project outcome or business requirements and creates only the epic artifact.
- AC02: The authoring skill investigates an existing repository when applicable, identifies independently deliverable
  features, makes the MVP boundary explicit, and records unresolved product decisions as answerable Unknowns.
- AC03: `review-epic-plan` validates MVP minimality, feature boundaries, dependencies, ordering, feature identifier
  consistency, cross-cutting architectural decisions, deferred-scope clarity, and the absence of implementation detail.
- AC04: Both skills direct authors to the canonical artifact definition and template, contain
  no placeholder text in submitted artifacts, and format Markdown before returning.
- AC05: No existing design-plan or implementation-plan authoring/review skill changes its artifact scope.


#### Steps

1. Add `.agents/skills/create-epic-plan/SKILL.md` with prerequisites, repository investigation requirements, artifact
   rendering instructions, and a clear boundary that it does not create child design plans or implementation plans.
2. Add `.agents/skills/review-epic-plan/SKILL.md` with review-artifact naming,
   findings/outcomes requirements, and the epic-specific review checklist.
3. Reference the new skills only where their actual responsibilities are invoked;
   do not claim they can author or review design-plan artifacts.
4. Format both skill files.


### 03: Extract the reusable feature lifecycle contract

Factor the leaf feature lifecycle from `run-feature` into an internal shared skill. The standalone command remains a
public wrapper, while `run-epic` can invoke the same design, planning,
execution, review, and QA rules without redefining them.


#### Acceptance Criteria

- AC01: The shared lifecycle defines the ordered gates for a feature: design authoring/review/approval,
  implementation planning/review/approval, execution/review, and human QA.
- AC02: The lifecycle accepts an explicit feature ID, parent epic artifact path, feature
  artifact directory, and an execution mode rather than relying on inferred epic state.
- AC03: The standalone `run-feature` wrapper preserves its existing direct-human entry point, isolated-worktree setup,
  branch and commit contract, artifact set, approvals, QA behavior, and `run-pr` handoff.
- AC04: Epic-coordinated lifecycle use does not create a nested worktree, alter
  the human's worktree, bypass a feature approval, or publish a child branch.
- AC05: The standalone mode begins with each feature's normal design authoring, review, final review, and human approval
  gates; the epic mode accepts an immutable, individually reviewed design plus evidence of
  explicit current-tranche design-set approval and begins at implementation planning.
- AC06: Before feature execution begins, a material change to an epic-owned design invalidates that feature's design-set
  approval, returns it to the feature design human-approval gate and final
  review, and blocks dependent implementation until the set is renewed.
- AC07: After feature execution begins, approved child plans remain immutable. Departures are recorded in the feature
  deviation artifact and, when they affect MVP scope, dependencies, sequencing, success criteria, or another feature,
  the epic-wide deviation artifact. Affected unfinished dependent work pauses until
  the epic impact assessment and any required renewed approval are complete.


#### Steps

1. Add `.agents/skills/run-feature-lifecycle/SKILL.md` as an internal composable contract, with no
   direct-human trigger language and no independent branch or publication ownership.
2. Move shared lifecycle state, gate, artifact-context, design immutability, review, and QA rules from `run-feature`
   into the internal skill, leaving wrapper-specific worktree, branch, commits, and terminal handoff in `run-feature`.
3. Define standalone and epic entry modes. Standalone begins at design authoring; for every current tranche, epic mode
   runs the individual feature design and review stages in the epic workspace, obtains explicit human approval of the
   complete tranche design set, completes final design review, and
   begins those feature records at implementation planning.
4. Before feature execution, require epic mode to invalidate a feature's set approval and return to its design human
   gate when a material design change is needed; block dependent implementation
   until the revised design set receives renewed approval.
5. After feature execution begins, keep approved child plans immutable; record departures in the feature deviation
   artifact and, when they affect the epic, the epic-wide deviation artifact. Pause affected unfinished dependent
   work until the impact assessment and any required renewed approval are complete.
6. Amend `run-feature` to identify itself as the standalone wrapper and to
   pass a blank or explicit parent-epic context to the shared lifecycle.
7. Define epic-coordinated execution as a handoff to the shared lifecycle from the selected existing epic context;
   it must use the documented worktree policy instead of creating a child worktree.
8. Search the changed policy graph for stale claims that `run-feature` is
   the only full lifecycle owner or that imply nested worktree creation.


### 04: Implement the run-epic coordinator

Create the public `run-epic` workflow. It owns the epic plan and planning gates, coordinates the complete MVP design set
before implementation, and records feature progress and roadmap
decisions without becoming a monolithic feature artifact.


#### Acceptance Criteria

- AC01: `run-epic` is selected for multi-feature, new-project, or major-expansion
  work and explicitly directs a one-feature change to `run-feature` instead.
- AC02: It establishes its selected worktree and regular branch through `create-agent-worktree`
  before emitting its epic artifact and never creates a nested child worktree.
- AC03: The workflow creates, agent-reviews, and human-approves `epic-plan.md` before child planning begins; material
  changes to product scope, MVP boundary, feature sequencing, or cross-cutting architecture require renewed approval.
- AC04: For every tranche, it creates and independently reviews a complete design plan for every included feature before
  creating an implementation plan or executing code, then stops for
  explicit human approval of the complete tranche design set.
- AC05: The epic plan is updated with each feature's identifier, artifact path, dependencies, and state while
  each feature's detailed artifacts remain in its own identifier-bearing directory.
- AC06: Post-MVP work remains a brief in the epic plan until the human approves a roadmap tranche. Each `T02+` tranche
  begins from the accepted integrated product state of every prerequisite tranche; otherwise it remains blocked. It
  completes its full individually reviewed and human-approved design set before implementation planning or code.
- AC07: Every tranche, including `T01`, requires an integrated outcome check against its success criteria, explicit
  human acceptance, and a roadmap decision. It does not automatically
  publish, create a pull request, or mark deferred features done.
- AC08: After each approved epic plan, tranche design set, feature implementation plan, and post-QA feature change, the
  workflow commits the approved stage. After integrated tranche acceptance, it conditionally invokes
  `cleanup-agent-worktree` only when `worktree_created` is true and hands the selected regular branch to `run-pr`.
- AC09: Before beginning the next feature, the workflow stops for human verification of the completed feature. A failed
  verification returns only that feature to its existing QA and deviation controls.
- AC10: Every material feature departure retains the feature-specific deviation record and creates an epic-wide
  deviation record when it affects tranche scope, dependencies, sequencing, success criteria, or another `FNN` feature.
  The epic record links affected deviations and governs dependent-work pauses and renewed tranche design-set approval.
- AC11: After all tranche features pass individual verification, the workflow stops for full human integrated
  verification against every tranche success criterion. An unmet criterion blocks tranche
  closure and all dependent later tranches until the affected work is fixed and accepted.
- AC12: Before a later approved tranche emits tranche-specific artifacts, it uses `create-agent-worktree` in its
  later-tranche mode to create and record a new coordinator branch, worktree, and `worktree_created` value from its
  accepted prerequisite baseline. It performs all tranche work there without nested feature worktrees.
- AC13: The canonical worktree tool and shared skill retain their existing regular-branch reuse behavior but support a
  validated later-tranche mode that accepts an immutable accepted-baseline SHA and
  creates a distinct regular branch and worktree from it. Tests cover both modes.


#### Steps

1. Inspect the canonical worktree tool's existing tests. Add failing tests for later-tranche mode and for preservation
   of regular-branch reuse behavior, then implement the tool support for a
   distinct branch and worktree from an immutable accepted-baseline SHA.
2. Update the shared worktree skill contract to document later-tranche mode, its required baseline, its distinct branch
   and worktree result, and its prohibition on nested worktrees. Run the focused tool tests and confirm both modes pass.
3. Create `.agents/skills/run-epic/SKILL.md` with its selection criteria, prerequisites, branch/worktree contract, epic
   and feature directory naming, artifact inventory, commit policy, and no-publication boundary.
4. Add a state machine for epic authoring, epic review, epic human approval, current-tranche design-set authoring/review
   and human approval, sequential feature lifecycle execution, integrated verification, and later-tranche planning.
5. Define feature and tranche derivation so `FNN` and `TNN` identifiers appear
   in directories, plans, reviews, journals, and the epic registers.
6. Specify one-at-a-time Unknown resolution and explicit approval blocks for the epic plan and each tranche design set.
7. Define the feature verification stop after every completed feature and the full integrated verification stop after
   all tranche features pass. Require the user to verify each criterion, route failures to the affected feature's QA and
   deviation controls, and block tranche closure and dependent tranches until explicit acceptance.
8. Add an epic-wide deviation artifact definition and template. Require it to cross-reference feature deviations and
   record affected feature IDs, the product-level impact, the pause or
   continuation decision, renewed approval needs, and verification.
9. Define how a later approved tranche verifies its accepted prerequisite baseline, uses later-tranche worktree mode
   before tranche-specific artifacts, creates and individually reviews every included feature design, obtains explicit
   human approval of the complete tranche design set, and then performs its feature work without nested worktrees.
10. Define how the coordinator records an implementation-ready design set, child lifecycle handoff context, integrated
    verification, and later roadmap revisions without editing approved child design or implementation plans.
11. Define stage commits for approved epic and tranche design sets, feature implementation plans, and post-QA feature
    changes. After integrated acceptance, require a final approved commit, conditional
    `cleanup-agent-worktree`, and a `run-pr` handoff without automatic publishing.
12. Format the new workflow skill.


### 05: Integrate workflow selection and parent-feature conventions

Update the principal policy and the standalone feature workflow so the new epic model is discoverable and unambiguous.


#### Acceptance Criteria

- AC01: The principal selects `run-epic` only when several independently deliverable features need coordinated MVP and
  roadmap planning, and selects `run-feature` for one significant cohesive deliverable.
- AC02: The artifact-class policy identifies epic plans as planning artifacts
  with agent review and explicit human approval under the epic workflow.
- AC03: `run-feature` documents optional parent epic context and feature identifiers
  without requiring them for a directly invoked standalone feature.
- AC04: Feature artifact, review, journal, and QA references can be traced from
  a feature ID in `epic-plan.md` without relying on branch names alone.
- AC05: Existing bug, task, hack, fix, hotfix, PR, and external-review workflow selection remains unchanged.


#### Steps

1. Update `.agents/agents/principal.md` artifact classes and workflow-selection
   guidance with the epic workflow's selection boundary and human-gate policy.
2. Amend the `run-feature` overview, project-directory convention, and handoff metadata
   to clarify its standalone wrapper role and optional `FNN`/parent-epic linkage.
3. Add only necessary cross-references from relevant workflow documentation;
   avoid implying that unrelated workflows become epic children.
4. Search `.agents` for contradictory exclusivity claims or references to unknown epic artifacts and resolve them.
5. Format all changed Markdown files.


### 06: Extend staged policy validation and tests

Make `run-epic` a first-class staged-policy workflow. Validator rules must enforce its lifecycle without
incorrectly requiring publication or allowing duplicated child worktree plumbing.


#### Acceptance Criteria

- AC01: The complete validator fixture includes `run-epic` and succeeds against the actual shared policy documents.
- AC02: Validation rejects an epic workflow missing pre-artifact worktree setup, epic plan creation/review/approval, MVP
  design-set approval, shared lifecycle use, feature-ID convention,
  integrated MVP validation, or `run-pr` handoff language.
- AC03: Validation rejects `run-epic` instructions that create direct Git worktree/branch
  plumbing, publish, create a pull request, or permit nested worktrees.
- AC04: Validation applies generic shared-role and principal-routing checks
  to the epic workflow only where it actually dispatches specialist agents.
- AC05: Tests preserve existing coverage for every current workflow and use
  fixture helpers that remain accurate as the policy inventory expands.


#### Steps

1. Extend the fixture inventory and add focused negative tests that remove each epic control or add forbidden nested
   worktree and publication instructions. Run the focused module
   and confirm the new tests fail before validator changes.
2. Add a separate epic requirement set and include `run-epic` in the validator's required lifecycle inventory,
   branch-workflow checks, and dispatch-path set without treating leaf-workflow phrases as interchangeable.
3. Re-run the focused validator test module and correct wording or validation patterns until the real
   policy fixture passes and every negative fixture fails with an actionable message.


### 07: Verify the complete policy graph

Format and validate every changed artifact, skill, and policy test. Review the final diff for lifecycle ownership,
approval gates, artifact traceability, and preservation of standalone feature behavior.


#### Acceptance Criteria

- AC01: `dt format markdown` completes for all modified Markdown paths.
- AC02: Focused validator tests and the full pytest suite pass.
- AC03: Ruff and type checking pass.
- AC04: The final diff contains no direct Git worktree creation outside the shared tool, no automatic publication, no
  nested-worktree instruction, no placeholder artifact content, and no stale standalone-only feature claim.
- AC05: The implementation journal records executed commands, outcomes, changes, and any human-directed deviations.
- AC06: A scenario-based policy walkthrough records the state transition, approval evidence, worktree owner, and
  resulting artifact for standalone features; a two-feature MVP design set; a material design change; a post-MVP
  tranche; an existing branch; a newly created worktree; and a failed child review.


#### Steps

1. Run Markdown formatting, focused policy-validator tests, full pytest,
   Ruff, and type checking using the commands in this plan.
2. Walk through and record the required standalone, MVP, design-change, roadmap-tranche, branch, worktree, and
   failed-review scenarios. Resolve every contradictory state transition before independent review.
3. Inspect the diff and test output against the acceptance criteria, focusing on
   workflow boundaries and the new feature-identifier traceability contract.
4. Dispatch the independent implementation review prescribed by the workflow and resolve findings before human QA.


----

## Unknowns

No blocking unknowns remain. The workflow will use an epic-owned selected worktree during epic planning and the shared
feature lifecycle without nested worktrees; standalone `run-feature` continues to own its independent worktree setup.


## Technical Notes

### Source design

This plan implements [`design-plan.md`](design-plan.md). Execution must not begin until the design plan and this
implementation plan have completed their respective review and explicit human-approval gates.


### Artifact topology

Use one epic directory at `.artifacts/{YYYYMMDD}--{epic-name}/` and one child feature directory at
`.artifacts/{YYYYMMDD}--{epic-name}--FNN-{feature-name}/`. The epic feature register links each child directory. Every
detailed feature artifact carries the same `FNN` identifier in its title and relevant metadata.


### Approval model

The epic plan is reviewed by an epic reviewer and explicitly approved by the human. The workflow then creates all MVP
feature design plans and their individual reviews, presents the complete MVP design set for one explicit human approval,
and only then permits a feature implementation plan. Each feature still retains its own implementation-plan
approval and QA approval. Post-MVP roadmap entries are briefs, not stub design plans.


### Lifecycle ownership

`run-epic` owns product decomposition, MVP design readiness, roadmap progression, and integrated milestone validation.
The internal lifecycle owns feature-level gates. `run-feature` remains the direct standalone wrapper around that
lifecycle and preserves its own branch/worktree setup and `run-pr` handoff. `run-epic`
never invokes an unchanged standalone `run-feature` as a nested child workflow.
