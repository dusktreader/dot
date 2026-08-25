# Design Plan Review: Carve work-specific configuration into a private work-dot repository

**Iteration 01**


## Source Artifact

.artifacts/20260713--carve-out-work-agents-file/design-plan.md


## Overview

The review surfaced the following findings:

- **Critical**:    0
- **Significant**: 4
- **Trivial**:     3


## Findings

### Summary

| Finding | Title                                                           | Outcome  |
| ------- | --------------------------------------------------------------- | -------- |
| S01     | AC19 "prompts the operator" is ambiguous about interaction mode | Resolved |
| S02     | `wdt configure` failure behavior not described in architecture  | Resolved |
| S03     | `wdt secrets fetch` behavior defined by analogy, not AC         | Resolved |
| S04     | Tension between AC02 independence claim and architecture caveat | Resolved |
| T01     | Missing blank line before `## Unknowns` heading                 | Resolved |
| T02     | Missing blank line before `## Technical Notes` heading          | Resolved |
| T03     | Long cell content in migration inventory wraps awkwardly        | Resolved |


### Significant

#### S01: AC19 "prompts the operator" is ambiguous about interaction mode


#### Where

Acceptance Criteria — AC19, line 162


#### Issue

AC19 states that `wdt configure` "prompts the operator to populate them out-of-band." It is
unclear whether "prompts" means an interactive terminal prompt that blocks for input, a printed
advisory message that the user reads and acts on later, or something else. These are meaningfully
different behaviors with different testability and scripting implications.


#### Impact

Implementers will have to guess which behavior is intended. If interactive prompting is chosen but
the caller is a script or CI, `wdt configure` may block indefinitely. If a printed advisory is
chosen but the caller expects interactive completion, the operator may not notice the seeds were
left empty.


#### Suggestion

Replace "prompts the operator to populate them out-of-band" with a precise description. For
example: "prints a notice to stderr naming each empty entry and exits successfully, leaving the
operator to populate the values using `wdt secrets set`."


#### Outcome

Resolved. AC19 was rewritten to state that `wdt configure` is fully non-interactive. On
initialization it prints a notice to stderr for each missing or empty work secret, naming the
secret and directing the operator to populate it via the `wdt secrets` interface. It never blocks
for input and, absent any other error, exits successfully even when every secret is still empty.


----

#### S02: `wdt configure` failure behavior not described in architecture


#### Where

Architecture — Configuration invocation flow, lines 198–206


#### Issue

AC04 states that `dt configure` "surfaces its success or failure in the normal `dt configure`
output." The architecture describes the subprocess invocation pattern but does not describe what
"surface" means: does `dt configure` exit non-zero when `wdt configure` fails? Does it print
the subprocess stderr? Does it treat a non-zero `wdt configure` exit as fatal or advisory?

This is a behavioral contract that will be needed by both the `dt` implementation and any test
that validates the integration.


#### Impact

Implementers will have to invent the failure-handling semantics. Without a defined contract, the
`dt configure` and `wdt configure` integration is only half-specified, and tests for AC04's
failure branch cannot be written from this design.


#### Suggestion

Add a sentence to the Configuration invocation flow section: for example, "If `wdt configure`
exits non-zero, `dt configure` prints the subprocess output with a labeled prefix and exits
non-zero with a distinct exit code." Alternatively, add an AC covering the failure path
explicitly.


#### Outcome

Resolved per user decision. AC04 and the Configuration invocation flow section now specify: if
`wdt` is present on PATH and `wdt configure` exits non-zero, `dt configure` reprints the
subprocess's stdout and stderr under a labeled prefix identifying the work layer and exits
non-zero itself. If `wdt` is absent from PATH, `dt configure` remains a silent successful no-op
with no work-related output at all.


----

#### S03: `wdt secrets fetch` behavior defined by analogy, not AC


#### Where

Acceptance Criteria — AC17, line 149; Architecture — Secret storage model, line 239


#### Issue

AC17 fully specifies `dt secrets fetch` behavior (stdout-only, no formatting, missing key exits
non-zero with stderr message). For `wdt`, it appends: "`wdt` provides an analogous command for
work secrets." Defining a work-CLI requirement by analogy rather than by explicit AC creates a
gap: if the two CLIs diverge in some edge case, it is unclear which is correct.


#### Impact

AC17 cannot be used directly as a test target for `wdt`. Any subtle difference in behavior
(exit codes, error message wording, key lookup semantics) will require judgment calls during
implementation rather than reference to a clear requirement.


#### Suggestion

Either: (a) promote the `wdt secrets fetch` requirement into a standalone AC that mirrors AC17
verbatim with `wdt` substituted, or (b) add a general AC stating that every `dt secrets`
sub-command has an exact behavioral counterpart in `wdt secrets` with the same contract, and
reference that AC from AC17.


#### Outcome

Resolved. AC17 was tightened and a new AC17a was added stating that `wdt secrets fetch <key>`
matches `dt secrets fetch <key>` exactly: raw value on stdout, missing key exits non-zero with an
error on stderr and nothing on stdout, and exit codes match. AC17a also asserts the general parity
rule that every `wdt secrets` sub-command shares the contract of its `dt secrets` counterpart and
differs only in which secret store it operates against.


----

#### S04: Tension between AC02 independence claim and architecture caveat


#### Where

Acceptance Criteria — AC02, line 36; Architecture — Configuration invocation flow, line 203


#### Issue

AC02 states that "`wdt` has no runtime dependency on `dt` being installed." The architecture
states that "running `wdt configure` before `dt configure` on a fresh machine is unsupported
and out of scope." These are compatible only if `wdt configure` does not fail when `dot` assets
are absent — it just produces an incomplete or incorrect result rather than erroring. But
"unsupported and out of scope" is ambiguous: does `wdt configure` detect the missing base layer
and abort, or does it proceed and leave a broken state silently?


#### Impact

Implementers writing `wdt configure` need to know whether to assert the presence of `dot`
assets. If they add a guard (which violates AC02's independence claim), or if they skip the
guard (which may leave a broken state), both choices conflict with some part of the spec.


#### Suggestion

Clarify the architecture sentence: either "Running `wdt configure` before `dt configure` on a
fresh machine is unsupported — `wdt configure` does not check for base layer presence and the
result is undefined" (preserving AC02), or explicitly note that the unsupported ordering is
out of scope and `wdt configure` may emit a warning if expected base paths are absent without
treating it as a hard dependency.


#### Outcome

Resolved. AC02 and AC03 were strengthened, and the Configuration invocation flow section was
rewritten, so that `wdt configure` is genuinely standalone: it has no runtime dependency on `dt`
or any `dot`-owned file, creates its own required target parent directories, and arranges for the
work shell rc to be sourced by the login shell on its own. It does not read or write any
dot-owned asset. The unsupported-ordering caveat now clearly states that `wdt configure` does not
check for base-layer presence and does not fail on its absence — the end-to-end workflow is what
is unsupported, not the `wdt configure` invocation itself.


----

### Trivial

#### T01: Missing blank line before `## Unknowns` heading


#### Where

Unknowns section — line 334


#### Issue

The `## Unknowns` heading is preceded by only one blank line after the final paragraph of the
Architecture section. The markdown style guide requires two blank lines before a heading when
it is not immediately following its parent heading.


#### Impact

Minimal — formatting only. Does not affect content.


#### Suggestion

Add a second blank line between the end of the Risks and decisions subsection and the
`## Unknowns` heading.


#### Outcome

Resolved. Two blank lines now precede `## Unknowns` in the design plan.


----

#### T02: Missing blank line before `## Technical Notes` heading


#### Where

Technical Notes section — line 342


#### Issue

The `## Technical Notes` heading is preceded by only one blank line after the Unknowns
section content. Same violation as T01.


#### Impact

Minimal — formatting only.


#### Suggestion

Add a second blank line between the Unknowns content and the `## Technical Notes` heading.


#### Outcome

Resolved. Two blank lines now precede `## Technical Notes` in the design plan.


----

#### T03: Long cell content in migration inventory wraps awkwardly


#### Where

Architecture — Migration inventory table, line 265


#### Issue

The "Destination" cell "Deleted from `dot`; work-specific behavior belongs in `work-dot`" is
longer than the other cells and breaks the horizontal rhythm of the table. Tables should keep
cell content short per the markdown style guide.


#### Impact

Minimal — readability only.


#### Suggestion

Shorten the cell to "Deleted from `dot`; moved to `work-dot`" and rely on the row's Category
column ("Hardcoded work Jira identity in client code") to carry the context.


#### Outcome

Resolved. The Destination cell for the "Hardcoded work Jira identity in client code" row now reads
"Deleted from `dot`; moved to `work-dot`" as suggested.


----

## Notes

S01 and S03 are related: both arise from behavior that is described informally rather than
pinned as a testable contract. Resolving S01 first (clarify `wdt configure` prompt behavior)
will make S03 easier to resolve consistently.

S02 requires a human decision: whether `dt configure` treats `wdt configure` failure as fatal
or advisory is a product-level choice, not a purely technical one. This should be resolved in
the design rather than left to the implementation plan.

S04 is low-stakes given that Tucker is the only user and the ordering constraint is clearly
stated — but it is worth a one-sentence clarification to prevent implementer hesitation.

The overall plan is strong. The Goal is clear and well-scoped, the migration inventory is
thorough, the risk disclosures are honest, and the architectural decisions are well-motivated.
No Critical findings.
