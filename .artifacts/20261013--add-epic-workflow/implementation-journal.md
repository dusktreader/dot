# Implementation Journal: Add epic workflow

A running record of execution for the approved epic-workflow implementation plan.


## Source plan

`.artifacts/20261013--add-epic-workflow/implementation-plan.md`


## Status

**Incomplete**: All implementation tasks are complete; full-project `ty check` and independent review remain blocked.


## Tasks

### Task 01: Define the epic artifact contract

#### Status

**Complete**


#### Overview

Added canonical epic-plan and epic-review definitions and templates,
documented artifact naming, and cataloged both types.


#### Steps taken

- Created this journal before implementation changes.
- Defined product-level epic sections, FNN feature identity, tranche
  records, T01 design gates, and separate child paths.
- Defined epic review findings, severity, outcomes, re-review resolution, and naming.
- Added epic artifact types to `.agents/README.md`.
- Ran `uv run dt format markdown` on the changed artifact definitions, catalog, and journal.


#### Files modified

- CREATED: `.agents/artifacts/epic-plan/description.md`
- CREATED: `.agents/artifacts/epic-plan/template.md.j2`
- CREATED: `.agents/artifacts/epic-review/description.md`
- CREATED: `.agents/artifacts/epic-review/template.md.j2`
- UPDATED: `.agents/README.md`
- UPDATED: `.artifacts/20261013--add-epic-workflow/implementation-journal.md`


#### Acceptance criteria validation


#### Satisfied AC01: Epic-level artifact sections

`.agents/artifacts/epic-plan/description.md` defines goal, scope, success criteria, architecture, registers,
risks, unknowns, dependencies, and closure criteria separately from child details.


#### Satisfied AC02: Feature register fields and identifiers

`.agents/artifacts/epic-plan/description.md` requires stable zero-padded FNN identity,
outcome, tranche, priority, dependencies, state, and artifact directory.


#### Satisfied AC03: T01 and later tranche register

The epic-plan description and template define the T01 MVP and T02+ tranches with objective, included features,
dependencies, state, verification, artifact links, and coordinator branch/worktree fields.


#### Satisfied AC04: MVP set and post-MVP briefs

The T01 description and template require complete individual designs and explicit design-set approval before
implementation planning; post-MVP features remain briefs until approved as a tranche.


#### Satisfied AC05: Unambiguous epic and feature artifact paths

`.agents/artifacts/epic-plan/description.md` defines `.artifacts/{YYYYMMDD}--{epic-name}/` and
separate `.artifacts/{YYYYMMDD}--{epic-name}--FNN-{feature-name}/` child directories.


### Task 02: Add epic planning and review skills

#### Status

**Complete**


#### Overview

Added the epic authoring and adversarial review skills, with artifact-only scope and explicit gates.


#### Steps taken

- Added repository investigation and outcome decomposition requirements to the epic authoring skill.
- Added epic-specific review checklist, severity findings, outcomes, re-review, and artifact contract.
- Kept existing design-plan and implementation-plan skill scopes unchanged.
- Ran `uv run dt format markdown` on both new skills and this journal.


#### Files modified

- CREATED: `.agents/skills/create-epic-plan/SKILL.md`
- CREATED: `.agents/skills/review-epic-plan/SKILL.md`
- UPDATED: `.artifacts/20261013--add-epic-workflow/implementation-journal.md`


#### Acceptance criteria validation


#### Satisfied AC01: Authoring prerequisites and scope

`.agents/skills/create-epic-plan/SKILL.md` requires a product outcome
or business requirements and limits output to `epic-plan.md`.


#### Satisfied AC02: Repository investigation and product decomposition

The authoring skill requires existing-repository investigation, independently meaningful
features, an explicit T01 MVP, answerable Unknowns, and concise later briefs.


#### Satisfied AC03: Epic-specific adversarial review

`.agents/skills/review-epic-plan/SKILL.md` evaluates MVP minimality, boundaries, dependencies,
sequencing, IDs, architecture, roadmap clarity, and implementation-detail separation.


#### Satisfied AC04: Canonical artifacts, complete content, and Markdown formatting

Both skills refer to their canonical descriptions and templates, require removal
of template content, and run `dt format markdown` before completion.


#### Satisfied AC05: Existing design-plan skill scope remains unchanged

The existing `create-design-plan` and `review-design-plan` files were inspected and left unchanged;
epic skills explicitly refer to feature-scoped design review as separate work.


### Task 03: Extract the reusable feature lifecycle contract

#### Status

**Complete**


#### Overview

Moved feature-level stages and safety gates into an internal lifecycle contract while
retaining `run-feature` as the standalone worktree, commit, and handoff wrapper.


#### Steps taken

- Defined explicit standalone and epic modes, entry stages, FNN identity,
  feature directory, parent epic, branch, and approval evidence inputs.
- Specified design and implementation authoring, independent review, human approval, final
  review, execution review, optional code review, QA, and immutable-plan controls.
- Added design-set invalidation and dependent-work pause rules before
  execution, plus feature and epic deviations after execution starts.
- Rewrote `run-feature` to call the shared lifecycle directly without changing standalone gates, artifact inventory,
  branch/worktree setup, approved-stage commit policy, QA approval, or run-pr handoff.
- Searched `.agents` for standalone-only lifecycle ownership and nested-worktree
  claims; removed the run-feature exclusivity statement.
- Ran `uv run dt format markdown` on both workflow skills and this journal.


#### Files modified

- CREATED: `.agents/skills/run-feature-lifecycle/SKILL.md`
- UPDATED: `.agents/skills/run-feature/SKILL.md`
- UPDATED: `.artifacts/20261013--add-epic-workflow/implementation-journal.md`


#### Acceptance criteria validation


#### Satisfied AC01: Ordered feature lifecycle gates

`.agents/skills/run-feature-lifecycle/SKILL.md` defines ordered design, implementation
planning, execution, review, and QA states with explicit transitions.


#### Satisfied AC02: Explicit lifecycle context and execution mode

The lifecycle invocation contract requires explicit mode, entry stage, feature ID,
parent epic path, artifact directory, branch/worktree, and epic approval evidence.


#### Satisfied AC03: Standalone run-feature behavior preserved

`.agents/skills/run-feature/SKILL.md` retains standalone entry, isolated worktree setup, artifacts,
approval and commit rules, QA gate, and conditional cleanup plus `run-pr` handoff.


#### Satisfied AC04: Epic lifecycle has no child-worktree or publication ownership

The internal lifecycle explicitly disclaims branch, worktree, commit, cleanup,
and publication ownership and states it never mutates the human worktree.


#### Satisfied AC05: Standalone and epic lifecycle entry modes

Standalone begins at design. Epic design set entry requires individually reviewed designs plus
current human set approval before immutable designs enter implementation planning.


#### Satisfied AC06: Pre-execution design change invalidates set approval

The lifecycle invalidates affected design-set approval and pauses dependent
implementation until individual final review and renewed set approval.


#### Satisfied AC07: Post-execution immutable plans and deviation controls

The lifecycle freezes approved plans once execution begins and requires feature deviations plus epic-wide
impact records and dependent-work pauses when scope or cross-feature impacts arise.


### Task 04: Implement the run-epic coordinator

#### Status

**Complete**


#### Overview

Added the epic coordinator and deviation record contracts, plus the
later-tranche worktree mode from an immutable accepted commit SHA.


#### Steps taken

- Added test-first coverage for later-tranche worktree creation, invalid baselines,
  and regular-branch reuse; confirmed the tests failed against the original CLI.
- Extended the canonical tool to validate linked worktrees and full commit SHAs, create a distinct
  branch/worktree from the accepted baseline, and retain regular mode branch reuse.
- Ran `uv run pytest --no-cov tests/test_create_agent_worktree.py -q`; all five tests passed.
- Documented later-tranche mode, required baseline, distinct sibling worktree, result, and no-nested-worktree contract.
- Added the epic coordinator state machine, artifact topology, approvals, feature lifecycle integration, human
  verification, integrated acceptance, stage commits, deviation control, and later-tranche progression.
- Added the epic-wide deviation artifact definition and template and cataloged it.
- Formatted the changed Markdown files and journal.


#### Files modified

- UPDATED: `.agents/tools/create-agent-worktree.py`
- CREATED: `tests/test_create_agent_worktree.py`
- UPDATED: `.agents/skills/create-agent-worktree/SKILL.md`
- CREATED: `.agents/skills/run-epic/SKILL.md`
- CREATED: `.agents/artifacts/epic-deviation/description.md`
- CREATED: `.agents/artifacts/epic-deviation/template.md.j2`
- UPDATED: `.agents/README.md`
- UPDATED: `.artifacts/20261013--add-epic-workflow/implementation-journal.md`


#### Acceptance criteria validation


#### Satisfied AC01: Workflow selection boundary

`.agents/skills/run-epic/SKILL.md` selects multi-feature MVP and roadmap
work and directs a single cohesive deliverable to `run-feature`.


#### Satisfied AC02: Selected branch and worktree established before epic artifact

The coordinator requires `create-agent-worktree` to return the selected branch,
worktree, and creation flag before any epic or feature artifact.


#### Satisfied AC03: Epic plan review and human approval

The state machine requires epic authoring, independent agent review, explicit human
approval, and renewed approval for material product changes before child planning.


#### Satisfied AC04: Complete tranche design set before implementation

Every included feature receives an individual design and review; the complete set receives explicit
human approval and final individual reviews before any implementation plan or code.


#### Satisfied AC05: Traceable feature register and separate detailed artifacts

The coordinator defines FNN-bearing feature directories and titles, traces child artifacts
from the epic register, and keeps detailed feature records outside `epic-plan.md`.


#### Satisfied AC06: Later-tranche baseline and design gates

Later roadmap work remains brief until approved; the coordinator verifies accepted prerequisite state, creates the later
worktree from its immutable SHA before tranche artifacts, and repeats the full design-set gate.


#### Satisfied AC07: Integrated tranche acceptance and roadmap decision

Each tranche requires success-criterion verification, explicit human acceptance, and a recorded
roadmap decision; no feature is automatically published or marked complete by deferral.


#### Satisfied AC08: Stage commits, conditional cleanup, and run-pr handoff

The coordinator commits approved epic/design/feature-plan/QA stages and integrated acceptance, cleans up only when
`worktree_created` is true, and hands the regular branch to `run-pr` without publication.


#### Satisfied AC09: Human verification after each completed feature

The coordinator stops after every feature for explicit human outcome verification;
failures return only that feature to its QA and deviation controls.


#### Satisfied AC10: Epic-wide deviation and dependent-work controls

`.agents/artifacts/epic-deviation/description.md` requires affected FNN/TNN IDs, feature-deviation
links, impact, pause or continue decision, renewed approvals, and verification.


#### Satisfied AC11: Full integrated tranche verification

The coordinator requires human pass/fail evidence against every tranche
criterion; any unmet criterion blocks closure and dependent tranches.


#### Satisfied AC12: Later-tranche worktree from accepted prerequisite baseline

The later-tranche process creates a sibling coordinator worktree from the accepted
baseline before tranche artifacts, without creating nested feature worktrees.


#### Satisfied AC13: Worktree tool supports later-tranche and regular-branch modes

`tests/test_create_agent_worktree.py` verifies exact accepted-SHA checkout, distinct branch/worktree, unchanged parent
state, invalid baseline rejection, required-baseline handling, parent validation, regular
branch reuse, and regular branch creation from a parent base; all ten tests passed.


### Task 05: Integrate workflow selection and parent-feature conventions

#### Status

**Complete**


#### Overview

Added epic workflow routing and approval policy to the principal and updated relevant feature-stage skill references.


#### Steps taken

- Added the epic plan artifact class and explicit epic-plan and tranche design-set human approval gates.
- Routed multiple independently deliverable MVP/roadmap features to
  `run-epic` and one cohesive significant feature to `run-feature`.
- Documented the accepted-baseline sibling-worktree exception in principal worktree policy.
- Updated only feature-stage skills invoked through the shared lifecycle to reference standalone and epic modes.
- Verified `run-feature` optional FNN and parent-epic context,
  feature artifact inventory, and run-pr handoff from Task 03.
- Searched `.agents` for stale lifecycle exclusivity, invalid nested-worktree rules, and epic artifact references.
- Ran `uv run dt format markdown` for the changed policy files.


#### Files modified

- UPDATED: `.agents/agents/principal.md`
- UPDATED: `.agents/skills/create-design-plan/SKILL.md`
- UPDATED: `.agents/skills/review-design-plan/SKILL.md`
- UPDATED: `.agents/skills/create-implementation-plan/SKILL.md`
- UPDATED: `.agents/skills/review-implementation-plan/SKILL.md`
- UPDATED: `.agents/skills/execute-implementation-plan/SKILL.md`
- UPDATED: `.agents/skills/review-implementation-execution/SKILL.md`
- UPDATED: `.artifacts/20261013--add-epic-workflow/implementation-journal.md`


#### Acceptance criteria validation


#### Satisfied AC01: Principal epic versus feature selection

`.agents/agents/principal.md` selects `run-epic` for multi-feature MVP/roadmap
work and `run-feature` for one significant, cohesive deliverable.


#### Satisfied AC02: Epic artifact approval policy

The principal classifies epic plans as planning artifacts and requires review and explicit human
approval under `run-epic`, including approval of each tranche's complete design set.


#### Satisfied AC03: Optional parent epic context on run-feature

`.agents/skills/run-feature/SKILL.md` accepts an optional FNN and parent
`epic-plan.md` path; neither is required for standalone invocation.


#### Satisfied AC04: Feature artifact traceability by identifier

The run-feature artifact contract and shared lifecycle repeat supplied FNN values
in feature plans, reviews, journals, deviations, QA records, and epic linkage.


#### Satisfied AC05: Existing unrelated workflow selection is unchanged

The principal's existing task, bug, fix, hotfix, PR, hack, and external-review workflow guidance
remains intact; only the run-epic and run-feature selection boundary was added.


### Task 06: Extend staged policy validation and tests

#### Status

**Complete**


#### Overview

Added a first-class epic policy requirement set, lifecycle checks, branch/worktree checks,
dispatch validation, and negative fixtures while preserving existing workflow coverage.


#### Steps taken

- Added run-epic and run-feature-lifecycle to the staged policy fixture inventory.
- Added a separate epic control set for pre-artifact worktree setup, epic authoring/review/approval, design-set
  approval, lifecycle use, FNN identity, integrated verification, later tranches, deviations, and `run-pr` handoff.
- Added lifecycle input, immutability, and worktree-ownership checks for the shared feature lifecycle.
- Included run-epic in branch-workflow and specialist-dispatch checks; required
  the principal route only because run-epic dispatches specialist roles.
- Added negative tests for each epic control, forbidden direct Git worktree operations, nested child
  worktrees, automatic publication, missing shared roles, and missing principal routing.
- Confirmed new tests failed before validator changes. Corrected run-feature's retained pre-artifact,
  branch cleanup, and principal-routing wording to satisfy its existing contract.
- Ran `uv run pytest --no-cov tests/test_validate_staged_agent_policies.py -q`; all 84 tests passed.
- Ran `uv run ruff check` on the validator, its tests, and worktree tool tests; it passed.


#### Files modified

- UPDATED: `tools/validate_staged_agent_policies.py`
- UPDATED: `tests/test_validate_staged_agent_policies.py`
- UPDATED: `.agents/skills/run-feature/SKILL.md`
- UPDATED: `.artifacts/20261013--add-epic-workflow/implementation-journal.md`


#### Acceptance criteria validation


#### Satisfied AC01: Complete fixture includes run-epic

`test_validator_accepts_shared_role_fixture` passes with both `run-epic`
and `run-feature-lifecycle` in the staged policy inventory.


#### Satisfied AC02: Missing epic lifecycle controls are rejected

`test_validator_rejects_missing_epic_workflow_control` removes each required setup, planning, approval, design-set,
lifecycle, identifier, integration, later-tranche, and handoff control and confirms actionable failures.


#### Satisfied AC03: Forbidden worktree, publication, and nesting instructions are rejected

`test_validator_rejects_forbidden_epic_worktree_or_publication_instruction` rejects nested worktrees,
direct `git worktree` plumbing, automatic publication, and direct push instructions.


#### Satisfied AC04: Shared-role and principal-routing validation follows actual dispatch

Epic and lifecycle skills are checked for generic shared roles; tests reject missing epic roles and missing principal
routing. Other non-dispatch policy classes do not gain a new routing requirement.


#### Satisfied AC05: Existing workflow coverage and accurate fixture helpers

The existing validator tests remain in the fixture suite and pass alongside the new tests; `write_fixture` inventories
both new workflow skills and the full staged-role fixtures. Focused result: 84 passed.


### Task 07: Verify the complete policy graph

#### Status

**Incomplete**: Full `ty check` reports 78 diagnostics in pre-existing files, and no independent subagent dispatch tool
is available in this session. The changed Python files pass targeted `ty` checks.


#### Overview

Formatted changed Markdown, completed focused and full test runs, reviewed the policy graph, and walked through the
required lifecycle scenarios. Full pytest and Ruff pass; full-project
type checking remains blocked by unrelated baseline diagnostics.


#### Steps taken

- Ran `uv run dt format markdown .agents .artifacts/20261013--add-epic-workflow`; restored only unrelated clean
  `.agents` files that the broad formatter changed. Formatted all authored Markdown and the project artifact directory.
- Ran `uv run pytest --no-cov tests/test_validate_staged_agent_policies.py -v`; 84 passed.
- Ran `uv run pytest --no-cov tests/test_create_agent_worktree.py -q`; 10 passed.
- Ran `uv run pytest`; 467 passed, two existing warnings, 78.98% coverage.
- Ran `uv run ruff check src tests`; passed. Focused Ruff checks for the changed Python tools and tests also passed.
- Ran `uv run ty check`; it reported 78 diagnostics in unrelated existing code, tests, and missing optional modules.
- Ran targeted `uv run ty check` on the changed validator and worktree tool files and their tests; passed.
- Ran `git diff --check`; passed.
- Performed a diff-first policy review. An independent review dispatch was unavailable in this session.


#### Files modified

- UPDATED: `tests/test_create_agent_worktree.py`
- UPDATED: `.artifacts/20261013--add-epic-workflow/design-review--01.md`
- UPDATED: `.artifacts/20261013--add-epic-workflow/design-review--02.md`
- UPDATED: `.artifacts/20261013--add-epic-workflow/design-review--03.md`
- UPDATED: `.artifacts/20261013--add-epic-workflow/design-review--04.md`
- UPDATED: `.artifacts/20261013--add-epic-workflow/implementation-review--02.md`
- UPDATED: `.artifacts/20261013--add-epic-workflow/implementation-review--03.md`
- UPDATED: `.artifacts/20261013--add-epic-workflow/implementation-review--05.md`
- UPDATED: `.artifacts/20261013--add-epic-workflow/implementation-review--06.md`
- UPDATED: `.artifacts/20261013--add-epic-workflow/implementation-journal.md`


#### Acceptance criteria validation


#### Satisfied AC01: Changed Markdown is formatted

`dt format markdown` completed for all authored `.md` files and the project artifact directory. The formatter does not
accept `.md.j2` paths; the canonical templates use the repository's Markdown structure and Jinja variables.


#### Satisfied AC02: Focused validator and full test suite pass

Focused policy validation passed with 84 tests; worktree tooling tests passed
with 10 tests; the complete suite passed with 467 tests and 78.98% coverage.


#### Unsatisfied AC03: Ruff and type checks pass

`uv run ruff check src tests` passed. Full `uv run ty check` reported 78 diagnostics, including unresolved optional
modules and existing type errors in `src/dot_tools` and unrelated tests. The changed Python files pass `uv run ty check
tools/validate_staged_agent_policies.py tests/test_validate_staged_agent_policies.py tests/test_create_agent_worktree.py
.agents/tools/create-agent-worktree.py`. No reported diagnostic refers to a changed file.


#### Satisfied AC04: Final policy diff preserves lifecycle and safety boundaries

`git diff --check` passed. The staged-policy tests reject direct worktree plumbing, nested feature worktrees, automatic
publication, missing human gates, missing dispatch roles, and missing epic routing. The epic workflow uses only the
shared worktree contract and retains explicit human approval, design-set, feature QA, and integrated acceptance gates.


#### Satisfied AC05: Journal records commands, outcomes, and deviations

This journal records task outcomes, focused and final commands, formatter scope, and verification results.
No plan deviations were requested; implementation stayed within the approved plan.


#### Satisfied AC06: Required policy scenarios are walked through

| Scenario               | State transition and approval evidence                                                                                                       | Worktree owner                                         | Resulting artifact                                                 |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ | ------------------------------------------------------------------ |
| Standalone feature     | Standalone mode enters design; human approves design, implementation plan, and QA                                                            | `run-feature` wrapper selects the regular worktree     | FNN-linked feature design, plan, journal, reviews, and QA records  |
| Two-feature MVP        | F01 and F02 are individually designed/reviewed; human approves the complete T01 design set before final reviews and implementation planning  | Epic coordinator                                       | T01 epic register plus separate F01 and F02 artifact directories   |
| Material design change | Before execution, invalidate set approval, pause dependents, obtain renewed human approval, and final-review affected designs                | Epic coordinator                                       | Revised feature design and renewed T01 design-set evidence         |
| Post-MVP tranche       | Require accepted prerequisite state; pass its immutable SHA to later-tranche mode before creating T02 artifacts                              | Later-tranche coordinator branch/worktree              | T02 register entry and separate FNN feature directories            |
| Existing branch        | Regular mode verifies the selected branch and reuses its worktree with `worktree_created=false`                                              | Existing feature branch owner                          | No second worktree; artifacts remain in the selected worktree      |
| Newly created worktree | From main/master, regular mode creates a branch and worktree from the immutable parent base                                                  | Shared worktree tool; workflow coordinator owns result | Regular branch and repository-local coordinator worktree           |
| Failed child review    | Findings return to the current feature stage; material plan changes require renewed human approval; no execution starts while review is open | Epic coordinator                                       | Updated feature review and, if needed, human-approved revised plan |
