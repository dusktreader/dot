# Design Plan Review: Carve work-specific configuration into a private work-dot repository

**Iteration 08**


## Source Artifact

.artifacts/20260713--carve-out-work-agents-file/design-plan.md


## Overview

This is a focused re-review scoped to AC29/AC30 (bare `creds` group behavior) and the adequacy
of their testing coverage. No prior findings are carried forward; earlier reviews are considered
resolved.

The review surfaced findings:

- **Critical**:    0
- **Significant**: 0
- **Trivial**:     1


## Findings


### Summary

| Finding | Title                                                           | Outcome |
| ------- | --------------------------------------------------------------- | ------- |
| T01     | AC30 help-output identity claim could be tightened              |         |


### Trivial


#### T01: AC30 help-output identity claim could be tightened

##### Where

Acceptance Criteria — AC30, line 303


##### Issue

AC30 states that the bare `dt creds` invocation displays help output "exits zero, with the same
pure-wrapper contract as AC29 (no default action, no store access, help output identical to `dt
creds --help`)." The phrase "help output identical to `dt creds --help`" is correct in intent but
technically the identity claim is between `dt creds` (bare) and `dt creds --help`, not between
`dt creds` and `wdt creds`. AC29 makes the analogous intra-CLI claim for `wdt`. The cross-CLI
parity requirement is that both CLIs exhibit the same _contract_, not that their help text is
identical string-for-string (they will differ in `dt` vs `wdt` label). The current wording is
unambiguous on close reading but slightly awkward.


##### Impact

Minimal. No implementer is likely to misread this as requiring byte-for-byte identical help
strings across `dt` and `wdt`. The implementation plan should not be affected.


##### Suggestion

Rewrite the parenthetical as: "(no default action, no store access, and bare invocation produces
the same output as `dt creds --help`)." Drop the phrase "with the same pure-wrapper contract as
AC29" or rephrase it to "following the same pure-wrapper contract defined in AC29."


##### Outcome


----

## Notes

All four focal areas pass review:

1. **Help is automatic and exits zero.** AC29 and AC30 each require the bare invocation to display
   the group's help output and exit zero. No conditional logic or flag required. ✓

2. **No default credential store action.** Both ACs explicitly state the group "carries no default
   action of its own, performs no credential read or write when invoked bare, and never touches the
   credentials store." The testing section reinforces this with a byte-identical store assertion. ✓

3. **`dt`/`wdt` parity.** AC30 explicitly adopts AC29's full contract ("same pure-wrapper
   contract as AC29") and adds only the intra-CLI help-identity claim (`dt creds` = `dt creds
   --help`). The symmetry is complete. ✓

4. **Testing adequacy.** The Testing and Validation Strategy section (lines 483–486) explicitly
   covers bare-invocation tests for both CLIs: exit zero, help output on stdout, and
   byte-identical credentials store. All three observable properties from AC29/AC30 are addressed
   at the unit level. Integration and manual acceptance do not need to repeat this coverage. ✓

T01 is cosmetic. The plan is approvable as written.
