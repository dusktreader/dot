# Design Plan Review: Carve work-specific configuration into a private work-dot repository

**Iteration 05**


## Source Artifact

.artifacts/20260713--carve-out-work-agents-file/design-plan.md


## Overview

The review surfaced the following findings:

- **Critical**:    0
- **Significant**: 0
- **Trivial**:     2


## Prior Review Resolution

- **All findings** ✓: Iteration 04 returned zero findings and approved the plan. This iteration is a
  focused re-review scoped to the newly added credentials migration requirements: bind-before-delete
  ordering (AC23), safe handling and deletion of `~/.agents/credentials.json` (AC24), and agent
  instructions using `dt`/`wdt secrets fetch` (AC25).


## Findings

### Summary

| Finding | Title                                            | Outcome |
| ------- | ------------------------------------------------ | ------- |
| T01     | Grammar error in Technical Notes credential note |         |
| T02     | AC21 does not name the directing CLIs            |         |


### Trivial

#### T01: Grammar error in Technical Notes credential note


#### Where

Technical Notes — lines 441–443 (`"neither CLI reads it, writes it, or removes it"`)


#### Issue

"reads it, writes it, or removes it" uses "or" in a negative context where "nor" is grammatically correct.
The intended meaning is "neither CLI reads it, writes it, nor removes it."


#### Impact

Minimal — the meaning is clear despite the error, but the construction is non-standard and could read
awkwardly in a formal document.


#### Suggestion

Replace "neither CLI reads it, writes it, or removes it" with "neither CLI reads it, writes it, nor
removes it."


#### Outcome


----

#### T02: AC21 does not name the directing CLIs


#### Where

Acceptance Criteria — AC21, lines 190–193


#### Issue

AC21 states that agent instructions "direct readers to fetch secrets through the appropriate CLI" but
does not name `dt` and `wdt` explicitly. AC25 supplies that detail, but AC21 in isolation leaves
"appropriate CLI" undefined. A reader verifying AC21 in isolation cannot determine what to look for in
the updated guidance.


#### Impact

Minimal — AC25 fully specifies the CLI-by-scope split, so no implementation ambiguity exists. The gap
is a clarity issue within AC21's own text, not a coverage gap.


#### Suggestion

Append to AC21: "Personal-secret guidance names `dt secrets fetch`; work-secret guidance names
`wdt secrets fetch`."


#### Outcome


----

## Notes

**New credentials ACs are structurally sound.** AC23 (bind-before-delete), AC24 (validated deletion of
`~/.agents/credentials.json`), and AC25 (agent guidance using CLI-mediated fetch) are internally
consistent, mutually reinforcing, and free of implementation-level detail. The four-step migration
sequence in the Rollout section of the Architecture maps exactly onto AC23 and AC24 with no contradiction.

**Migration inventory is consistent.** The `~/.agents/credentials.json` row and the
"Agent-facing credential-file read instructions" row in the migration table correctly reflect AC24 and
AC21/AC25 respectively.

**No implementation leakage detected.** The new ACs and the rollout narrative correctly defer the specific
settings fields, argument shapes, and required key enumeration to the implementation plan. The phrase
"The specific settings fields and argument shapes surface during implementation planning" in AC23 is
appropriate scoping language, not hedging.

**T01 and T02 are independent.** Neither finding affects the other; both are safe to address in a
single editing pass.
