# Implementation Plan Review: Carve work-specific configuration into private work-dot repository

**Iteration 06**


## Source Artifact

.artifacts/20260713--carve-out-work-agents-file/implementation-plan.md


## Overview

Both findings from iteration 05 are fully resolved. One new significant finding surfaced on the
agent-instructions constraint introduced in this review brief (`creds set` exposure in agent guidance
violates design plan AC26). One trivial markdown finding noted.

- **Critical**:    0
- **Significant**: 1
- **Trivial**:     1


## Prior Review Resolution

- **S01** ✓: Task 05 AC02 now reads "prints the value of the named field within `Settings.credentials`
  to stdout" and AC03 reads "does not name a field in `Settings.credentials` (not in top-level
  `Settings`)". Step 2 now says "Retrieves the value by resolving `key` against `settings.credentials`
  … not against top-level `Settings` fields." Language aligns with Task 04's parallel ACs.
- **T01** ✓: Task 08 AC07 now reads "which is added in Task 09". Misdirection corrected.


## Findings


### Summary

| Finding | Title                                                                        | Outcome |
| ------- | ---------------------------------------------------------------------------- | ------- |
| S01     | Task 14 directs agents to configure credentials, violating design plan AC26  |         |
| T01     | Technical Notes bold quasi-headings are multi-sentence, require `####`       |         |


### Significant


#### S01: Task 14 directs agents to configure credentials, violating design plan AC26

##### Where

Execution — Task 14 — Acceptance Criteria — AC03, AC05 — approximately lines 1318–1324;
Task 14 — Steps — steps 3 and 4 — approximately lines 1339–1351


##### Issue

Design plan AC26 is explicit: agent guidance covers credential *retrieval* only (`creds fetch`);
it does not, by default, instruct agents to configure or set credentials via `creds set`,
`settings bind`, or otherwise. The only exception is existing guidance that has a justified need to
set a credential — in which case that instruction *may remain*, but no *new* agent-facing set guidance
is added by this migration.

Task 14 violates this constraint in three places:

1. **AC03** requires that `dot` agent instructions document "how to configure personal secrets via
   both `dt settings bind` (batch) and `dt creds set <key> <value>` (individual, non-echo)." This
   directs an agent to both credential-setting paths — neither of which is fetch.

2. **AC05** requires that `work-dot` agent instructions document "how to configure work secrets via
   both `wdt settings bind` (batch) and `wdt creds set <key> <value>` (individual, non-echo)."
   Same problem for the work layer.

3. **Steps 3 and 4** add guidance text that includes the phrases "configured via `dt settings bind`
   (batch) or `dt creds set <key> <value>` (individual, safe for interactive use)" and "Configure
   them via `wdt settings bind …` (batch) or `wdt creds set <key> <value>` (individual, safe for
   interactive use)" directly into agent instruction files.

The design plan's Technical Notes reinforce the constraint:
> "Agent-guidance updates … cover credential *retrieval* only (`creds fetch`); [they do] not, by
> default, instruct agents to configure credentials via `creds set` or `settings bind`. Where existing
> agent guidance has a justified need to set a credential, that instruction may remain, but no new
> agent-facing set guidance is added by this migration."

No justification is given in Task 14 for the set guidance; it is added purely to expose the `creds
set` surface to agents, which the design plan explicitly prohibits.


##### Impact

An implementor following Task 14 as written adds configuration instructions to agent guidance files,
producing agent-facing text that tells agents how to call `creds set` and `settings bind`. Agents
reading those files during a session will treat credential configuration as an available action rather
than an operator-only task. This creates a leak surface: an agent instructed to "configure" a
credential could invoke `creds set` and write a value without operator awareness. The design plan
accepted the `creds fetch` stdout risk explicitly but treated `creds set` as an operator-only path
for exactly this reason.


##### Suggestion

Revise AC03 to cover retrieval only:

> AC03: Agent instructions in `dot` document how to retrieve personal secrets via `dt creds fetch
> <key>`. They do not instruct agents to configure credentials.

Revise AC05 to match:

> AC05: Agent instructions in `work-dot` document how to retrieve work secrets via `wdt creds fetch
> <key>`. They do not instruct agents to configure credentials.

Revise step 3 to remove the configuration clause:

> In `dot`'s agent instructions, add a note: "Personal secrets are retrieved via `dt creds fetch
> <key>`. Work secrets (if McGraw Hill configuration is installed) use `wdt creds fetch <key>`
> analogously. Do not read `~/.agents/credentials.json` directly."

Revise step 4 to remove the configuration clause:

> In `work-dot/.agents/instructions/work.md`, add: "Work secrets are retrieved via
> `wdt creds fetch <key>`. Do not read plaintext credential files."

If a separate operator-facing document (not agent guidance) needs to describe the `creds set`
path, that is appropriate and unaffected by this constraint. The migration guide in Task 13 already
covers this for operators.


##### Outcome


----


### Trivial


#### T01: Technical Notes bold quasi-headings are multi-sentence, require `####`

##### Where

Execution — Task 04 Technical Notes — approximately lines 576–602; Task 06 Technical Notes —
approximately lines 780–800; similar occurrences in Tasks 05 and 13.


##### Issue

Multiple Technical Notes sections use the pattern `**Bold label (ACxx)**:` as a heading for a
multi-sentence paragraph, for example `**Nested credentials sub-model (AC02)**:` followed by
three or four sentences. The markdown style guide states that a bold subject followed by a colon
is acceptable only when the full item fits on one line (≤ 120 characters including the leading
`- `), and that content requiring more than one sentence must be promoted to a `###` or `####`
subsection.


##### Suggestion

Convert each multi-sentence bold quasi-heading block in Technical Notes to a `####` subsection.
For example:

```markdown
#### Nested credentials sub-model (AC02)

The design plan AC17 requires credentials to nest under a dedicated sub-model …
```

This applies to every Technical Notes bold-label entry that spans more than one sentence.


##### Outcome


----


## Notes

S01 is the only change required for plan approval. It is a wording correction to two ACs and two
steps in Task 14 — no structural rework is needed elsewhere. The fix is unambiguous and can be
applied without human input: remove all "configure via `creds set` / `settings bind`" language from
agent-facing instructions and ACs, leaving only the `creds fetch` retrieval path. Operator-facing
configuration guidance already lives in Task 13's migration document and is unaffected.

T01 requires reformatting Technical Notes blocks in several tasks; it does not affect testability
or correctness and does not block execution.

All other constraints from the review brief are clear in the plan:

- **Command behavior (`creds set`)**: Tasks 04 and 05 ACs fully cover no-echo success (AC07/AC07),
  non-zero unknown-key failure with diagnostic on stderr (AC06/AC06), nested-only write scoping
  (AC06), byte-identical settings on failure (AC06 — "byte-identical verification in tests"), and
  non-revealing acknowledgement (AC07). Help-text ACs (AC14/AC08) satisfy design plan AC23.
- **Nested scope**: All `creds fetch` and `creds set` ACs now consistently reference
  `WorkSettings.credentials` (Task 04) and `Settings.credentials` (Task 05) as the exclusive
  lookup target, never top-level fields or arbitrary paths.
- **No-echo/no-mutation/cross-store tests**: Task 04 AC15–AC18 and Task 05 AC11–AC14 enumerate
  unit tests for successful fetch, missing-key error, empty-value error, set with known key
  (non-echo acknowledgement), unknown-key with byte-identical settings, nested-only write scoping,
  and cross-store isolation. Coverage is complete.
- **Migration boundary**: Task 13 AC02 itemizes the full rollback-safe sequence ending with
  `creds fetch` validation before deletion of the legacy file; Task 13 Technical Notes reinforce
  that the legacy file remains on disk until Phase 5. The gate is well-defined.
- **Agent instructions (fetch-only)**: Task 11 AC03 and its implementation steps correctly limit
  the `work.md` file to `wdt creds fetch` guidance only. S01 above identifies the violation in
  Task 14's documentation pass; Task 11 is clean.
