# Design Plan Review: Tune agent workflows and report OpenCode costs

**Iteration 02**


## Source Artifact

.artifacts/20260715--tune-agent-workflows/design-plan.md


## Overview

The review surfaced findings:

- **Critical**:    0
- **Significant**: 1
- **Trivial**:     1


## Prior Review Resolution

- **C01** ✓: Architecture sentence completed — "…renders one consistent dataset to the selected output format."
- **C02** ✓: Unknowns section added with the atomic-promotion symlink question.
- **S01** ✓: AC12 now names the upstream repository, source files, and source-revision capture requirement.
- **S02** ✓: AC09 replaced informal tier labels with full provider-qualified model IDs.
- **S03** ✓: AC13 added — discrete, testable non-zero failure-mode requirement for database errors.
- **S04** ✓: AC10 now enumerates `--since`, `--until`, `--directory`, `--agent`, `--model`, `--format`, and `--file`.
- **T01** ✓: AC07 re-review trigger defined as a change that alters an acceptance criterion or adds a code path.


## Findings

### Summary

| Finding | Title                                             | Outcome |
| ------- | ------------------------------------------------- | ------- |
| S01     | "by default" leaves task workflow push scope open | Made the workflow's push and PR prohibition unconditional. |
| T01     | "selects suggestively" is undefined in AC09       | Replaced the phrase with direct model-recommendation behavior. |


### Significant

#### S01: "by default" leaves task workflow push scope open

##### Where

Acceptance Criteria — AC02, line 36


##### Issue

AC02 states the task workflow "does not push or create a pull request by default." The phrase
"by default" implies that push and pull-request creation are available through some non-default
opt-in path, but no such path is defined anywhere in the plan. An implementer reading this will
need to invent — or omit — the opt-in mechanism.


##### Impact

If the intent is that push and PR are simply never performed by `run-task`, "by default" is
misleading and blocks a clean implementation boundary. If a future opt-in is intended, the
scope of that path must appear in the design. Either way, the AC as written is not fully
testable: a reviewer cannot determine whether the absence of a push flag is correct behavior
or a missing feature.


##### Suggestion

If push and PR are permanently outside `run-task`'s authority, remove "by default" and state
the prohibition unconditionally. If a future opt-in is planned, name the flag or mechanism and
describe its authority boundary.


##### Outcome

Made the workflow's push and PR prohibition unconditional.

----

### Trivial

#### T01: "selects suggestively" is undefined in AC09

##### Where

Acceptance Criteria — AC09, line 95


##### Issue

AC09 says "The principal selects suggestively." "Suggestively" is not a standard term for
model-selection behavior. It is likely intended to mean the principal proposes a model and may
escalate independently without requiring approval, but this reading requires inference.


##### Impact

Minimal — the surrounding sentences make the intent recoverable. However, the word could lead
to inconsistent behavior across agents interpreting this AC, particularly for the escalation
path.


##### Suggestion

Replace with a direct statement of what the principal does: "The principal recommends a model
based on project class and evidence, and may escalate independently without seeking approval
unless the change represents a material cost tradeoff."


##### Outcome

Replaced the phrase with direct model-recommendation behavior.

----

## Notes

- All seven prior findings are fully resolved. The plan is substantially improved.
- S01 is the only issue that could produce a genuine implementation ambiguity; it has a simple
  resolution.
- T01 is cosmetic; resolving S01 is sufficient to approve the plan.
- The final Unknown was resolved by Tucker: the home-directory deployment uses directory symlinks to this repository,
  so promotion copies validated staged files into their corresponding repository directories.
