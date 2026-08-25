# Implementation Plan Review: Tune agent workflows and report OpenCode costs

**Iteration 04**


## Source Artifact

.artifacts/20260715--tune-agent-workflows/implementation-plan.md


## Overview

The review surfaced findings:

- **Critical**:    0
- **Significant**: 0
- **Trivial**:     1


## Prior Review Resolution

- **S01** ✓: Task 05 Technical Notes (lines 431–434) now defines "staged OpenCode variants" as the complete
  model-specific specialist definitions under `.config/opencode/agents` — seven specialist roles per dispatch context
  (work GPT variants, work Claude variants, personal variants), each with fixed model frontmatter pointing to one
  canonical `.agents/agents` role description.
- **S02** ✓: Task 07 AC02 was rewritten to separate lifecycle fixtures from model-policy fixtures. The lifecycle case
  list (feature, task, hack, stale-parent, successful-cleanup, declined-run, abandoned-run) is retained. The model
  policy half now reads "Separate model-policy fixtures cover every staged OpenCode variant and its fixed dispatch
  context," which is now resolvable against the definition added for S01.
- **T01** ⚠: Task 06 AC06 was rewritten to add "from the defined staged OpenCode variant inventory." The variant
  inventory reference is now grounded, but the substantive overlap with Task 05 AC04 (principal ownership of model
  choice, escalation, risk, and Zen prevention) is unresolved. AC06 still does not name a worktree-specific observable
  that Task 05 AC04 does not already assert. Carried forward as T01 below at Trivial severity.
- **T02** ✓: Task 07 Step 3 was rewritten into two distinct sentences — one for running the fixture suite and
  validating the staged tree, and one for confirming `git diff -- .agents` is empty. The scope conflation is resolved.


## Findings

### Summary

| Finding | Title                                                  | Outcome |
| ------- | ------------------------------------------------------ | ------- |
| T01     | Task 06 AC06 still overlaps Task 05 AC04 substantively |         |


### Trivial

#### T01: Task 06 AC06 still overlaps Task 05 AC04 substantively


#### Where

Task 06 — Acceptance Criteria — AC06 — approximately line 456.


#### Issue

AC06 now reads: "Staged guidance selects model-specific specialist variants from the defined staged OpenCode variant
inventory, assigns model choice, escalation, risk classification, and approval decisions to the principal, and prevents
a work-project dispatch from selecting a Zen model." Task 05 AC04 already asserts: "Staged principal, executor,
investigator, planner, reviewer, workflow, and review policies assign risk and model decisions to the principal and
enforce the work-project versus personal-project model menus." Both criteria assert the same policy constraint
(principal ownership plus Zen exclusion). Task 06 AC06 adds no observable behavior specific to worktree creation,
integration gates, or the lifecycle changes that are Task 06's subject matter.


#### Impact

An executor completing Task 06 has no worktree-scoped check to verify. If model dispatch is already asserted by
Task 05 AC04, a later execution review will either mark AC06 redundant or accept Task 06 as done without verifying
any worktree-specific observable. The criterion does not block implementation, but it will produce a coverage gap at
review time.


#### Suggestion

Replace AC06 with a worktree-specific observable: "Worktree creation, gate prompts, integration steps, and cleanup
instructions in the staged `run-feature` and `run-task` guidance contain no model-selection language, deferring model
choice entirely to the principal dispatch policy documented in Task 05 AC04."


#### Outcome


----

## Notes

T01 is cosmetic and does not block execution of Tasks 06 or 07. It can be deferred and resolved inline or addressed in
the next plan revision. All Critical and Significant findings from prior iterations are resolved. The plan is
approvable as-is for execution.
