# Design Plan Review: Install manifest dependency ordering

**Iteration 01**


## Source Artifact

.agents/work/20260623-182800--install-manifest-deps/design-plan.md


## Overview

The review surfaced the following findings:

- **Critical**:    0
- **Significant**: 3
- **Trivial**:     3


## Findings

### Summary

| Finding | Title                                                              | Outcome |
| ------- | ------------------------------------------------------------------ | ------- |
| S01     | Settings dependency parity is an open unknown, not a confirmed AC  |         |
| S02     | AC07 conflates runtime skip behavior with ordering — needs clarity |         |
| S03     | Failure gate scope is underspecified for settings                  |         |
| T01     | AC02 uses passive construction hiding the actor                    |         |
| T02     | Architecture uses bold quasi-headings for multi-sentence content   |         |
| T03     | Missing two blank lines before `### Manifest schema enrichment`    |         |


### Significant

#### S01: Settings dependency parity is an open unknown, not a confirmed AC

##### Where

Acceptance Criteria — AC05 (line 59); Unknowns — "Settings dependency model parity" (line 179)


##### Issue

AC05 states definitively that "The settings section behaves the same way as the tools section" with
its own independent resolver. At the same time, the Unknowns section calls out "confirm that settings
should support dependencies in this iteration rather than tools only" as a decision still needed. These
two sections contradict each other: the AC treats settings parity as a resolved fact while the Unknowns
section explicitly marks it as unresolved.

If the unknown is genuinely open, AC05 should not exist yet. If it has been resolved in favor of
inclusion, the unknown should be removed or marked with its resolution.


##### Impact

An implementer reading the AC will build settings support. An implementer reading the Unknowns section
will wait for a decision. This contradiction makes the scope of the feature ambiguous and will cause
confusion during implementation planning.


##### Suggestion

Either:

1. Remove AC05 and the settings-related portions of AC09 and AC10 until the unknown is resolved, or
2. Remove the "Settings dependency model parity" unknown and restate it as a resolved decision in
   Technical Notes: "Settings support dependencies in this iteration, using the same mechanism as tools
   with a separate per-section resolver."


##### Outcome


----

#### S02: AC07 conflates runtime skip behavior with ordering — needs clarity

##### Where

Acceptance Criteria — AC07 (line 74)


##### Issue

AC07 states "skipping happens after ordering, not before." This sentence describes an implementation
constraint (the sequencing of two internal phases) rather than an observable system behavior or outcome.
The AC is framed as a behavioral guarantee but the testable claim is unclear: what does an end user or
test observe that confirms skip decisions happen "after" ordering?

The intent is presumably that a skipped entry's dependents are still installed in the computed order
(rather than the order shifting to fill the gap), but the AC does not say that.


##### Impact

An implementer cannot write a test that directly observes "skipping happens after ordering." The AC as
written is not testable in the sense required by the design plan definition. This will surface as an
ambiguous or untestable test case during implementation planning.


##### Suggestion

Rewrite AC07 to state the observable outcome:

> When one or more entries are skipped at runtime, the remaining entries are installed in the same
> relative order as if the skipped entries had run. The skip decision for each entry is evaluated in
> the resolved order, not before ordering is computed.


##### Outcome


----

#### S03: Failure gate scope is underspecified for settings

##### Where

Architecture — "Failure gate" (line 155); Acceptance Criteria — AC08, AC09, AC10 (lines 87–105)


##### Issue

AC08, AC09, and AC10 each say the error "exits without running any installation script in the affected
section." For the tools section this is unambiguous. For the settings section the phrase "installation
script" is a misfit: settings run application scripts, not installation scripts. More importantly, the
Architecture section's "Failure gate" description says "a bad declaration in the settings section aborts
before any setting runs" but the AC wording says "installation script" throughout, which creates a
terminology inconsistency between the AC and architecture.

This is also the point where the open Settings parity unknown (S01) creates the most concrete harm: if
the human decides settings are out of scope, AC08–AC10 as written still reference "the affected section"
ambiguously.


##### Impact

The inconsistent terminology ("installation script" vs. "setting") makes it harder to verify the ACs
against the settings path during implementation. A reviewer of the implementation plan could reasonably
dispute whether a settings-section abort satisfies the AC wording.


##### Suggestion

Reword AC08, AC09, and AC10 to replace "installation script in the affected section" with "entry in
the affected section." For example, AC08 becomes: "…exits without processing any entry in the affected
section." This is neutral across tools and settings and matches the architectural language.


##### Outcome


----

### Trivial

#### T01: AC02 uses passive construction hiding the actor

##### Where

Acceptance Criteria — AC02 (line 33)


##### Issue

"…a manifest that uses none of the new dependency-declaration mechanism produces exactly the same
install behavior as before this feature: the same entries run, in an order consistent with the
file-as-written, and **the existing test suite passes without modification**."

The last clause shifts from a behavioral claim about `dt configure` to a claim about the test suite
passing. The test suite is not a system actor; it is a verification mechanism. Stating it as part of
the AC mixes the requirement with its verification method.


##### Impact

Minor. An implementer knows what is meant, but the AC is slightly impure by the definition's standard
(an AC must describe a system behavior, not a test artifact).


##### Suggestion

Remove the test-suite clause entirely. The AC is fully stated by "produces exactly the same install
behavior as before this feature: the same entries run, in an order consistent with the file-as-written."


##### Outcome


----

#### T02: Architecture uses bold quasi-headings for multi-sentence content

##### Where

Architecture — "Dependency resolver" subsection (lines 132–139)


##### Issue

The dependency resolver's three responsibilities are formatted as a bulleted list where each item uses a
bold subject followed by multi-sentence content. The markdown style guide explicitly prohibits this
pattern: "Never use a bold subject as a quasi-heading for a multi-sentence paragraph inside a list."

The three items ("Validate the graph", "Detect cycles", "Produce a stable order") each carry a full
sentence of elaboration, qualifying them as multi-sentence items that should be promoted to `####`
subsections.


##### Impact

Trivial formatting violation. The content is readable but does not conform to the project style guide.


##### Suggestion

Convert the three bulleted responsibilities to `####` subsections within the "Dependency resolver"
`###` section, or — if the content of each item genuinely fits on one line after trimming — condense
each item to a single short sentence.


##### Outcome


----

#### T03: Missing two blank lines before `### Manifest schema enrichment`

##### Where

Architecture — line 118


##### Issue

The `## Architecture` heading's introductory paragraph ends on line 115 and is followed by a single
blank line before `### Manifest schema enrichment` on line 118. The markdown style guide requires two
blank lines before a heading when the parent heading has content (which it does here — the introductory
paragraph).


##### Impact

Trivial formatting violation.


##### Suggestion

Add a second blank line between the introductory paragraph and the `### Manifest schema enrichment`
heading.


##### Outcome


----

## Notes

S01 is the most structurally significant finding because it creates a contradiction between the AC and
the Unknowns section. It must be resolved before the Unknowns section can be considered complete or
before an implementation plan can be written with confidence about the feature's scope. Resolving S01
will also clarify whether S03's terminology concern affects tools only or both sections.

S02 requires human input: only the author knows whether the intended guarantee is (a) dependents of a
skipped entry still run in computed order, (b) the resolved order is never re-computed after skips, or
(c) something else entirely.

T02 and T03 can be fixed mechanically with no design decisions required.
