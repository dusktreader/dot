# Design Plan Review: Tune agent workflows and report OpenCode costs

**Iteration 04**


## Source Artifact

.artifacts/20260715--tune-agent-workflows/design-plan.md


## Overview

The review surfaced findings:

- **Critical**:    0
- **Significant**: 1
- **Trivial**:     1


## Prior Review Resolution

- **S01** ✓: AC01, AC02, and the Architecture section each state "exclusively squash merge" — the integration mode is
  now unambiguous and the staleness check in AC17 is fully scoped.
- **S02** ✓: AC18 specifies the full teardown lifecycle: successful squash removes the worktree and preserves the
  local audit branch; declined or abandoned runs retain both until the human explicitly removes them.
- **T01** ✓: AC16 now reads "every human gate after the agent worktree is established" — the ordering dependency is
  explicit and the early-abort ambiguity is eliminated.


## Findings

### Summary

| Finding | Title                                               | Outcome                                                                                                                                                            |
| ------- | --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| S01     | "Regenerating" in AC17 is undefined                 | Accepted: parent drift stops the workflow; with explicit approval, regeneration discards the agent worktree and audit branch and restarts from the updated parent. |
| T01     | AC04 escalation signal not cross-referenced to AC08 | Accepted: AC04 now explicitly uses AC08's hard-signal list.                                                                                                        |


### Significant

#### S01: "Regenerating" in AC17 is undefined

**Where**

Acceptance Criteria — AC17, lines 169–171


**Issue**

AC17 offers the human two choices when the parent branch has drifted: "rebasing the agent work onto the current
parent state or regenerating the agent work." "Rebasing" has an unambiguous Git meaning. "Regenerating" does not —
it could mean re-running the entire workflow from the updated parent, re-running only the implementation phase, or
discarding the agent branch and starting fresh. The plan does not define it.


**Impact**

An implementer will have to invent regeneration semantics from scratch. If they choose a partial re-run and the
design or task plan is incompatible with the new parent state, the result may be subtly stale work presented for
integration. If they choose a full re-run they may discard valid work the human expected to preserve. This is not
a corner case — any collaborative branch where the parent advances during a long agent run will hit it.


**Suggestion**

Replace "regenerating the agent work" with a concrete description such as: "discarding the agent branch and
restarting the workflow from the updated parent branch." If partial re-run is intended, name the phases that are
repeated and which artifacts are preserved.


**Outcome**

Accepted and applied. AC17 now stops on parent drift and asks the human rather than offering a rebase path. With
explicit human approval, regeneration discards the agent worktree and local audit branch and restarts the workflow from
the updated parent. AC17 and the Architecture section prohibit silently assuming stable parent state or rebasing,
merging, discarding, overwriting, or otherwise changing human work.

----

### Trivial

#### T01: AC04 escalation signal not cross-referenced to AC08

**Where**

Acceptance Criteria — AC04, lines 57–59; AC08, lines 89–94


**Issue**

AC04 states escalation occurs "when objective evidence meets a defined escalation signal" and adds "technical area
alone does not trigger escalation." AC08 lists the hard signals that drive principal escalation. Neither AC refers
to the other, and AC04's phrase "defined escalation signal" implies the signal set is defined somewhere — but a
reader scanning only AC04 cannot find where.


**Impact**

Minimal — a careful reader will find AC08's hard-signal list and infer the connection. An implementer writing the
hack escalation path may produce a signal set that overlaps inconsistently with AC08 rather than deriving from it.


**Suggestion**

Add a cross-reference in AC04: "Escalation uses the hard signals defined in AC08." Alternatively, move the
escalation-trigger language into AC08 to consolidate the full signal set in one place.


**Outcome**

Accepted and applied. AC04 now explicitly states that escalation uses the hard-signal list in AC08.

----

## Notes

- S01 is resolved by Tucker's decision: parent drift stops the workflow; regeneration is a human-approved full restart
  from the updated parent after discarding the agent worktree and local audit branch.
- T01 is resolved by cross-referencing AC08, which remains the single hard-signal list.
- Markdown validation passed with no violations on the design plan.
