# Implementation Plan Review: Tune agent workflows and report OpenCode costs

**Iteration 03**


## Source Artifact

.artifacts/20260715--tune-agent-workflows/implementation-plan.md


## Overview

The review surfaced findings:

- **Critical**:    0
- **Significant**: 2
- **Trivial**:     2


## Prior Review Resolution

Review--02 carried zero findings. No prior findings required re-evaluation.


## Findings

### Summary

| Finding | Title                                                             | Outcome |
| ------- | ----------------------------------------------------------------- | ------- |
| S01     | "Staged OpenCode variants" is undefined across Tasks 06–07        |         |
| S02     | Task 07 AC02 fixture scope is unverifiable without variant list   |         |
| T01     | Task 06 AC06 duplicates Task 05 AC04 without worktree specificity |         |
| T02     | Task 07 Step 3 checksums assertion conflates two distinct scopes  |         |


### Significant

#### S01: "Staged OpenCode variants" is undefined across Tasks 06–07


#### Where

Task 06 — AC06 and Step 7; Task 07 — AC02, Step 2, Step 3; Task 05 — Step 10; approximately
lines 452, 473, 499, 512, 513, 413.


#### Issue

The phrase "staged OpenCode variants" appears in six locations across Tasks 05, 06, and 07 as
if it names a concrete, bounded set of files or configurations. No section of the plan defines
what these variants are, how many exist, what distinguishes them, or where they live in the
staged tree. Task 07 AC02 requires fixture coverage "including each staged OpenCode variant"
and Task 06 AC06 requires that "staged guidance works with staged OpenCode variants" — neither
criterion is testable until the variants are enumerated.


#### Impact

Task 07 AC02 cannot be confirmed complete because an executor has no list against which to
check fixture coverage. The validator extension in Task 07 Step 2 has no scope. An implementer
will either guess at the variant set and under-cover it, or ask the human for clarification
mid-task and stall the run. Design plan AC09 requires work-project and personal-project model
menus to be correctly separated — this gap means the staged enforcement of that boundary cannot
be validated systematically.


#### Suggestion

Add a single definition either in Task 05 Technical Notes or the top-level Technical Notes
that names the variant set — for example: "Staged OpenCode variants are the two dispatch
contexts defined in AC09: work-project (GitHub Copilot provider) and personal-project
(OpenCode Zen provider). The staged model-policy file must carry explicit dispatch rules for
both." Replace every occurrence of "each staged OpenCode variant" with the defined set name or
list the specific dispatch-context files.

If the variants are workflow-class variants (feature/task/hack) rather than provider contexts,
say that explicitly. The plan should not use one label for two different scopes.


#### Outcome


----

### Significant

#### S02: Task 07 AC02 fixture scope is unverifiable as written


#### Where

Task 07 — Acceptance Criteria — AC02 — approximately line 499.


#### Issue

AC02 requires fixture coverage for "feature, task, hack, stale-parent, successful-cleanup,
declined-run, abandoned-run, and principal/model-policy fixtures, including each staged
OpenCode variant." The AC is partially well-formed: the lifecycle cases are enumerable. But
"including each staged OpenCode variant" is appended as a modifier to the fixture list without
explaining whether each variant needs its own fixture, each fixture must be exercised per
variant, or only the model-policy fixtures vary by variant. Combined with the undefined variant
set from S01, this AC cannot be checked off by an executor with confidence.


#### Impact

The validator suite may be accepted as complete with partial coverage. A later promotion
review would find gaps in work-project versus personal-project enforcement, defeating the
purpose of Task 07.


#### Suggestion

Resolve S01 first. Then rewrite AC02 to separate lifecycle fixtures from model-policy
fixtures: "Fixture coverage includes the full lifecycle matrix (feature, task, hack,
stale-parent, successful-cleanup, declined-run, abandoned-run) and two model-policy
dispatch-context fixtures (work-project GitHub Copilot and personal-project Zen), each
exercised as a distinct minimal staged tree."


#### Outcome


----

### Trivial

#### T01: Task 06 AC06 duplicates Task 05 AC04 without adding worktree specificity


#### Where

Task 06 — Acceptance Criteria — AC06 — approximately line 452.


#### Issue

AC06 states "staged guidance works with staged OpenCode variants and assigns model choice,
escalation, risk classification, and approval decisions to the principal without allowing a
work-project dispatch to select a Zen model." Task 05 AC04 already asserts "staged principal,
executor, investigator, planner, reviewer, workflow, and review policies assign risk and model
decisions to the principal and enforce the work-project versus personal-project model menus."
The two criteria cover the same policy constraint. Task 06 AC06 contributes no worktree-specific
observable behavior — it could be removed without losing any coverage unique to Task 06.


#### Suggestion

Either remove Task 06 AC06 and rely on Task 05 AC04 for model policy coverage, or rewrite it
as a worktree-specific criterion: "Worktree creation, gate prompts, and cleanup steps in the
staged `run-feature` and `run-task` guidance do not reference model selection, deferring that
decision entirely to the principal dispatch policy."


#### Outcome


----

### Trivial

#### T02: Task 07 Step 3 checksums assertion conflates staged and source scopes


#### Where

Task 07 — Steps — Step 3 — approximately line 513.


#### Issue

Step 3 ends with "Compare `.agents` checksums before and after and confirm no unrelated source
or staging files changed." The validator already asserts that tracked `.agents` is unchanged
(Task 07 AC04). Adding a checksum comparison of source `.agents` in the same step that runs
fixture validation mixes two distinct concerns: staged-tree correctness and live-tree
non-modification. The instruction is also ambiguous — "before and after" what operation, and
does "staging files changed" mean the staging root or the source?


#### Suggestion

Split into two clear sentences: "Run the validator against the complete staged tree with the
canonical command and assert a clean exit. Confirm `git diff -- .agents` is empty after
validation to verify the validator performed no write operations."


#### Outcome


----

## Notes

S01 and S02 are related: resolving S01 (defining the variant set) is a prerequisite for
resolving S02 (tightening AC02 scope). Both can be addressed with a single definition addition
and a two-sentence AC rewrite — no structural changes to the plan are needed.

T01 and T02 are cosmetic and do not block execution. They can be deferred to the next plan
revision or addressed inline if the implementer prefers a clean plan before starting Tasks
06–07.

Completed work in Tasks 01–05 and the cost-command implementation is unaffected by these
findings. Tasks 08–10 are likewise unaffected. Only Tasks 06 and 07 require attention before
execution of those tasks.
