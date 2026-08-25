# Implementation Plan Review: Tune agent workflows and report OpenCode costs

**Iteration 01**


## Source Artifact

.artifacts/20260715--tune-agent-workflows/implementation-plan.md


## Overview

The review surfaced findings:

- **Critical**:    0
- **Significant**: 3
- **Trivial**:     4


## Findings

### Summary

| Finding | Title                                                              | Outcome                                                   |
| ------- | ------------------------------------------------------------------ | --------------------------------------------------------- |
| S01     | Task 06 ACs are not directly testable without a validator contract | Defined the validator entry point, arguments, and checks. |
| S02     | Unknowns do not include the `opencode.db` path-discovery rule      | Resolved the default path and excluded a new CLI option.  |
| S03     | Task 05 has no focused test command or validation step in commands | Added the canonical staged-policy validator command.      |
| T01     | Project Commands uses `bash` language hint instead of `shell`      | No action required; the finding was a false alarm.        |
| T02     | Task 04 Technical Notes uses bold quasi-heading for single note    | Left acceptable prose unchanged.                          |
| T03     | Task 05 AC03 references design plan ACs by label without quoting   | Added the referenced acceptance-criterion titles.         |
| T04     | `opencode_costs.py` module path inconsistency in Technical Notes   | Documented the verified flat-domain-module convention.    |


### Significant

#### S01: Task 06 ACs are not directly testable without a validator contract


#### Where

Execution — Task 06 — Acceptance Criteria — lines 397–405


#### Issue

AC01–AC04 each describe something the validator must detect, but the plan never specifies
where the validator lives, what command invokes it, or what its output contract is. AC03 says
"Validation detects work-project dispatches using a Zen model" without defining what text
pattern or structural marker constitutes a Zen model reference in a policy file. AC04 says
"Validation detects policy text that permits live edits" without identifying what patterns
constitute prohibited text. A tester cannot write a failing fixture test without this
contract.


#### Impact

Task 06 tests will either be vacuous string searches or will require the executor to
re-derive the contract, producing a validator that may not match the design intent.


#### Suggestion

Add a Technical Notes subsection to Task 06 that names the validator entry point, its
arguments, and the exact patterns or heuristics used for Zen-model detection and live-edit
detection. Alternatively, move the contract definition into an earlier task and reference it
here.


#### Outcome

Defined the validator entry point, arguments, and checks.

----

#### S02: Unknowns do not include the `opencode.db` path-discovery rule


#### Where

Unknowns — lines 480–487


#### Issue

Task 01 step 3 says "Decide and document the database discovery order, using an explicit CLI
option only if the design or existing conventions require it." This is an open design
decision, not a note-taking step. The design plan (AC10) specifies `--database` is not in
the option list, but Task 01 leaves discovery open. The Unknowns section lists the estimator
revision and schema fields but omits the discovery mechanism, which affects the CLI contract
and tests.


#### Impact

The executor may ship a discovery rule that conflicts with AC10 or requires schema changes to
the CLI tests, forcing a correction pass.


#### Suggestion

Add an Unknown: "Confirm the default database path and whether `--database` is a supported
option. Resolve from schema inspection and design plan AC10 before Task 02."


#### Outcome

Resolved the default database path and excluded a new CLI option.

----

#### S03: Task 05 has no focused test command or validation step in commands


#### Where

Project Commands — lines 25–145; Execution — Task 05 — Steps — lines 361–379


#### Issue

The Project Commands section includes `### Verify the staged policy tree` but that command
only confirms the directory exists and compares the diff. Task 05 step 9 says "Run the staged
policy validation and review commands from Task 07," but Task 07 contains no separately
documented command in Project Commands — the linting and test commands are for Python code,
not staged policy. There is no documented command that runs the policy validator from Task 06
at the Project Commands level, so the executor has no canonical invocation to cite in the
journal.


#### Impact

The executor will have to improvise the validation invocation or skip it, and the reviewer
cannot reproduce the result from the documented commands alone.


#### Suggestion

Add a `### Run staged policy validator` subsection under Project Commands with the expected
invocation once the validator is implemented in Task 06. It can note the dependency on Task 06
completion. Alternatively, include the invocation in Task 05's Technical Notes.


#### Outcome

Added the canonical staged-policy validator command.

----

### Trivial

#### T01: Project Commands uses `bash` language hint instead of `shell`


#### Where

Project Commands — multiple fenced code blocks (e.g., line 36, 50, 63)


#### Issue

The markdown style guide requires `shell` as the language hint for shell commands, not `bash`
or `sh`. All code blocks under Project Commands use ` ```shell ` — reviewing the raw text
confirms this is correct, but the `### Inspect the local OpenCode schema` block at lines 103–107
and `### Verify the staged policy tree` at lines 135–140 should also be verified for
consistency.

On inspection all code blocks do use ` ```shell `. This finding is superseded — no violation.


#### Suggestion

No action required.


#### Outcome

No action required; the finding was a false alarm.

----

#### T02: Task 04 Technical Notes uses bold subject for a two-sentence paragraph


#### Where

Execution — Task 04 — Technical Notes — lines 330–332


#### Issue

The Technical Notes paragraph beginning "Prefer a new `src/dot_tools/opencode_costs.py`…"
is a multi-sentence paragraph following a plain paragraph, not inside a list. This is
acceptable, but the opening instruction "Follow existing Typer registration patterns" and
"existing test conventions" could be clearer as a short list.


#### Suggestion

Minor: split into two short bullet items for readability, or leave as-is.


#### Outcome

Left acceptable prose unchanged.

----

#### T03: Task 05 AC03 references design plan AC labels without quoting section titles


#### Where

Execution — Task 05 — Acceptance Criteria — line 349


#### Issue

AC03 says "satisfy AC02 through AC04 of the design plan." Design plan AC labels are not
numbered sequentially in the same namespace as this plan's task ACs. The reference is
unambiguous when reading both documents, but an implementer working only from the
implementation plan cannot resolve "AC02 through AC04 of the design plan" without the design
document. The full titles or a parenthetical description would make the criterion self-contained.


#### Suggestion

Expand to: "satisfy design plan AC02 (`run-task` controls), AC03 (`run-hack` authority), and
AC04 (evidence-led escalation), including gates, Git authority, final QA ownership, and
escalation signals."


#### Outcome

Added the referenced acceptance-criterion titles.

----

#### T04: `opencode_costs.py` proposed module path may conflict with the package layout


#### Where

Technical Notes — Proposed file layout — line 494


#### Issue

The proposed path `src/dot_tools/opencode_costs.py` places a multi-concern domain module at
the top level of the package. The plan also lists `src/dot_tools/cli/opencode.py`, which
follows the established sub-package pattern. If the existing package has sub-packages for
other domains, a flat module at `dot_tools/opencode_costs.py` is inconsistent.
The plan acknowledges this with "Adjust names only if repository inspection requires it," but
does not record whether inspection was performed.


#### Suggestion

Add a note in the Technical Notes or Task 01 to confirm the package layout during
investigation and record the outcome before Task 04 begins. The proposed path is fine if the
package is flat; flag it as a deviation if sub-packages are the norm.


#### Outcome

Documented the verified flat-domain-module convention.

----

## Notes

T01 was a false alarm on closer inspection — all code blocks use `shell`. S01 and S03 are
related: both stem from the policy validator contract being deferred to Task 06 without an
earlier placeholder in Project Commands or a forward reference that makes the execution steps
self-contained. Resolving S01 (add a validator contract to Task 06 Technical Notes) likely
makes S03 straightforward to address. S02 is independent and low-cost to fix. None of these
findings block execution of the Python tasks (01–04, 07–08); they primarily affect Task 05
and Task 06 fidelity.
