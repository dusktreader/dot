# Design Plan Review: Tune agent workflows and report OpenCode costs

**Iteration 01**


## Source Artifact

.artifacts/20260715--tune-agent-workflows/design-plan.md


## Overview

The review surfaced findings:

- **Critical**:    2
- **Significant**: 4
- **Trivial**:     1


## Findings

### Summary

| Finding | Title                                                  | Outcome |
| ------- | ------------------------------------------------------ | ------- |
| C01     | Architecture section has a truncated sentence          | Completed the reporting pipeline output contract. |
| C02     | Unknowns section is absent                             | Added the remaining answerable promotion unknown. |
| S01     | "Eric Butler's available estimator" is undefined       | Identified the source files, repository, and required source revision capture. |
| S02     | Model-tier names undefined in the document             | Replaced names with full provider model IDs. |
| S03     | No failure-mode AC for unreadable or absent database   | Added explicit non-zero, read-only database-failure behavior. |
| S04     | AC10 filter list is unspecified                        | Defined the approved time, directory, agent, and model filters. |
| T01     | "material" hedges the re-review trigger in AC07        | Defined the threshold as an AC-altering or code-path-adding change. |


### Critical

#### C01: Architecture section has a truncated sentence

##### Where

Architecture — line 148


##### Issue

The sentence "…groups results, and renders one consistent dataset to" ends mid-clause. The
remainder of the sentence — describing where the dataset is rendered — is missing.


##### Impact

The architecture description of the cost-reporting pipeline is incomplete. An implementer
reading this section cannot determine the output contract of the reporting view, and the
implementation plan will have to invent the missing detail rather than derive it.


##### Suggestion

Complete the sentence. For example: "…groups results, and renders one consistent dataset to
the selected output format."


##### Outcome

Completed the reporting pipeline output contract.

----

#### C02: Unknowns section is absent

##### Where

Document structure — no Unknowns section present


##### Issue

The design plan description requires an Unknowns section listing ambiguities that must be
resolved before implementation can begin. This document omits it entirely. Several genuine
unknowns are embedded in Technical Notes (OpenCode DB schema, estimator availability, linked
deployment behavior) rather than surfaced as explicit answerable questions.


##### Impact

Reviewers and the orchestrator have no structured list of open questions to resolve before
approving the plan. Unknowns buried in Technical Notes will not receive explicit resolution
tracking and may silently carry over into the implementation plan.


##### Suggestion

Add an Unknowns section before Technical Notes. At minimum, it should address:

- What is the current OpenCode SQLite schema for session records, and which fields are
  optional?
- Which version of Eric Butler's estimator will be used, and how is it obtained?
- How does the linked home-directory deployment affect atomicity guarantees during promotion?


##### Outcome

Added the remaining answerable atomic-promotion question to the plan.

----

### Significant

#### S01: "Eric Butler's available estimator" is undefined

##### Where

Acceptance Criteria — AC12, line 115


##### Issue

AC12 refers to "Eric Butler's available estimator" without identifying a package name,
version, repository, or resolution procedure if it is unavailable. "Available" is an
undefined qualifier.


##### Impact

An implementer cannot select the correct estimator without out-of-band research. If there are
multiple estimators by this author, or if the tool is updated between implementation and
review, there is no authoritative source to verify against. The AC is partially untestable as
written.


##### Suggestion

Name the estimator precisely: package name or repository URL, minimum version, and the
fallback behavior when it is not installed or cannot be loaded.


##### Outcome

Identified the precise upstream repository files and source-revision capture requirement.
----

#### S02: Model-tier names are undefined in the document

##### Where

Acceptance Criteria — AC09, lines 88–93


##### Issue

AC09 uses "Luna", "Terra", "Sol", "Zen", "DeepSeek V4 Flash", and "Kimi K2.7 Code" as
project-internal names without defining them in the document. "Zen" is used as a provider
category without explanation. A reader unfamiliar with the project's prior naming conventions
cannot evaluate whether this AC is correct or complete.


##### Impact

The AC is opaque to any reviewer who has not absorbed the prior naming context. If names
change, the AC cannot be verified without cross-referencing external documents. The
implementation plan will need to introduce these definitions somewhere; the design plan is the
right place.


##### Suggestion

Add a brief definitions list in Technical Notes or as an introductory paragraph in AC09 that
maps each tier name to its GitHub Copilot or Zen provider model ID.


##### Outcome

Replaced informal model labels with their provider-qualified model IDs.
----

#### S03: No failure-mode AC for unreadable or absent database

##### Where

Acceptance Criteria — AC10–AC12


##### Issue

AC11 mentions "unavailable" and "malformed local-data cases" in a single clause but does not
isolate them as discrete testable failure modes. There is no AC for the case where the
OpenCode SQLite database does not exist, is locked, or cannot be read due to permissions.
Technical Notes acknowledge schema evolution, but the required user-facing behavior is
unspecified.


##### Impact

Implementers have no testable target for database-failure paths. The result could be a silent
empty report, an unhandled exception, or a confusing error message — all are consistent with
AC11 as written.


##### Suggestion

Expand AC11 or add AC15 with a concrete behavioral requirement: "When the local OpenCode
database is absent, locked, or unreadable, `dt opencode costs` exits with a non-zero status
and a message identifying the path and failure reason. It does not modify or create the
database."


##### Outcome

Added a discrete, testable non-zero failure-mode requirement.
----

#### S04: AC10 filter list is unspecified

##### Where

Acceptance Criteria — AC10, line 100


##### Issue

AC10 states the command "accepts useful report filters" without naming them. Filter
selection directly affects the report schema, the implementation scope, and testability.
"Useful" is a subjective qualifier, not an observable requirement.


##### Impact

The implementation plan will have to invent the filter set without design-level guidance.
Different implementers may choose incompatible filter sets, and no AC can verify filter
correctness.


##### Suggestion

Replace "useful report filters" with the explicit set of supported filters, for example:
`--since <date>`, `--model <name>`, `--session <id>`, and `--limit <n>`.


##### Outcome

Defined `--since`, `--until`, `--directory`, `--agent`, and `--model` as the initial filter set.
----

### Trivial

#### T01: "material" hedges the re-review trigger in AC07

##### Where

Acceptance Criteria — AC07, line 73


##### Issue

AC07 limits re-review to "a material behavior, interface, data, security, or test change"
without defining what makes a change material. "Material" is a judgment word that different
reviewers will apply inconsistently.


##### Impact

Minimal in isolation, but the ambiguity could lead to unnecessary re-reviews or to reviewers
skipping re-review when a change is significant but does not feel "material" to them.


##### Suggestion

Either remove "material" (letting the listed change categories carry the full weight) or add
a parenthetical threshold, e.g. "…a behavior, interface, data, security, or test change that
alters an AC or adds a new code path".


##### Outcome

Defined materiality as a change that alters an acceptance criterion or adds a code path.

----

## Notes

- C01 and C02 are related: the truncated Architecture sentence and the missing Unknowns
  section both suggest the document was not fully reviewed before submission. Resolving both
  in a single pass is efficient.
- S01 and S03 together underspecify the cost-reporting failure surface. They can be addressed
  in the same AC revision pass.
- S02 (undefined tier names) does not block implementation for someone with project context,
  but it does make the AC unverifiable in a standalone review. Consider whether a glossary
  reference is the right fix rather than embedding definitions in AC09.
- S04 (filter list) requires a design decision from Tucker before it can be resolved. The
  reviewer cannot supply the canonical filter set.
