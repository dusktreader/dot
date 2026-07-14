# Design Plan Review: Carve work-specific configuration into a private work-dot repository

**Iteration 06**


## Source Artifact

.artifacts/20260713--carve-out-work-agents-file/design-plan.md


## Overview

The review surfaced the following findings:

- **Critical**:    0
- **Significant**: 0
- **Trivial**:     0


## Prior Review Resolution

- **T01** ✓: "neither CLI reads it, writes it, nor removes it" — "nor" is now correct at line 494.
- **T02** ✓: AC22 (formerly AC21) now names `dt creds fetch <key>` and `wdt creds fetch <key>` explicitly by scope,
  and uses "creds" rather than "secrets" throughout, closing both the naming gap and the terminology
  inconsistency that was implicit in the prior review's suggestions.


## Findings

### Summary

| Finding | Title | Outcome |
| ------- | ----- | ------- |

No findings.


## Notes

**`creds fetch` terminology is consistent throughout.** Every occurrence in the AC section (AC18, AC19, AC22,
AC23, AC24, AC26), the Architecture section (Credentials model, Rollout and compatibility, Testing and
validation strategy), and the Technical Notes uses `creds fetch` without exception. The term "secrets" does
not appear anywhere in the document. The prior review's T02 suggestion inadvertently used "secrets fetch" —
the revised plan corrects to "creds fetch," which is the right term.

**Application-owned command framing is correct.** The Goal paragraph, AC17, AC18, AC19, and the Decisions list
all state plainly that `creds` is an application-owned command group, not a Typerdrive built-in. The phrase
"application-owned `creds` command group" appears verbatim in the Decisions list. No invented Typerdrive
"secrets" API surface is assumed anywhere.

**Nested credentials settings-model requirement is fully specified.** AC17 fixes the structural requirement
(a `credentials` attribute whose value is a structured sub-model), AC18 and AC19 require `creds fetch` to
resolve against that nested model, AC21 requires `configure` to seed entries under the nested model and
emit notices directing use of `settings bind`, and AC24 requires `settings bind` to target the nested
sub-model via dotted paths. The Architecture section mirrors this in the Credentials model subsection. The
requirement is stated at design level without prescribing class names or field names.

**Safe migration with settings bind is sound.** AC24 and AC25 together enforce a rollback-safe order: both
CLIs installed and configured, `settings bind` executed and targeting the nested credentials sub-model,
`creds fetch` validated for every required key, and only then `~/.agents/credentials.json` deleted in a
single identified step. AC21 ensures `configure` seeds but never overwrites, so re-runs are safe. The
four-step sequence in the Rollout section maps exactly onto this ordering with no contradiction.

**No invented Typerdrive API.** The plan explicitly defers the question of how `settings bind` reaches into
a nested sub-model to the implementation plan, and states clearly that no Typerdrive "secrets" primitive is
assumed. The Risks and decisions section and Technical Notes both call this out as an implementation
constraint, not a design assumption.

**No regressions from prior approved content.** The plan's existing AC01–AC15 (repository split, agent
context, Git configuration, Jira retention) are unchanged from iteration 04, which was approved without
findings. The credentials ACs AC16–AC26 carry forward cleanly from the version reviewed in iteration 05,
with the T01 and T02 corrections applied.

**Plan is approved.** All focused review criteria are met, no prior findings remain open, and no new
findings were identified. Implementation planning may proceed.
