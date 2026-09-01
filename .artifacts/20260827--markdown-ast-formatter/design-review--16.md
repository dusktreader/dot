# Design Plan Review: Canonical AST-based Markdown formatter

Iteration 16 re-reviews the plan against iteration 15, checking prior findings and the requested parser, ownership,
serialization, policy, round-trip, idempotence, and write-safety boundaries.


## Source Artifact

/Users/tucker.beck/src/dusktreader/dot/.artifacts/20260827--markdown-ast-formatter/design-plan.md


## Overview

The review surfaced findings:

- **Critical**:    1
- **Significant**: 2
- **Trivial**:     0

The underscore ownership, fence fallback, definition-list inverse, and policy predicate revisions are present. The
supporting profile headings have regressed structurally. Canonical byte rules still leave concrete context-sensitive
cases open, and the stated complete-baseline guarantee conflicts with fail-closed extension claims.


## Prior Review Resolution

- **C01** ✗: The three supporting headings are again `####`, rather than `#####` nested under AC07 or AC12.
- **S01** ✓: AC12 assigns all CommonMark underscore delimiter-run semantics to core and makes Betterem disjoint from
  core, with longest-delimiter precedence for the overlapping caret and tilde forms.
- **S02** ⚠: Delimiter, escape, and math rules are more specific, but exact context-sensitive bytes and complete
  Betterem ownership remain underdefined; this finding is carried forward.
- **S03** ✓: The tilde fallback now has a minimum length of three, and delimiter selection follows restoration and
  normalization.
- **S04** ✓: Definition-list framing, termination, EOF behavior, and the canonical inverse remain explicit.
- **S05** ✓: The terminal-character function and finite sentence scan now cover recursive nodes, escapes, entities,
  empty nodes, links, images, code, math, and soft or hard breaks.


## Findings

### Summary

| Finding | Title                                                           | Outcome |
| ------- | --------------------------------------------------------------- | ------- |
| C01     | Supporting profile headings are not nested                      |         |
| S02     | Exact canonical productions remain incomplete                   |         |
| S06     | Baseline coverage conflicts with extension fail-closed behavior |         |


### Critical

#### C01: Supporting profile headings are not nested


#### Where

Acceptance Criteria, lines 196, 343, and 368


#### Issue

`Table serialization details`, `Block profile`, and `Inline and fence profile` use `####`, making them siblings of the
AC headings. They must be `#####` content under AC07 or AC12. This reverses the structural fix recorded in the prior
review. AC01 through AC17 are otherwise the only headings matching the `#### AC##` pattern.


#### Impact

The artifact no longer has the required nested structure. A consumer cannot treat the table rules as AC07 content or
the two profile matrices as AC12 content without applying an undocumented interpretation.


#### Suggestion

Change the three supporting headings to `##### Table serialization details`, `##### Block profile`, and `##### Inline
and fence profile`. Leave the `#### AC01` through `#### AC17` headings unchanged.


#### Outcome


----

### Significant

#### S02: Exact canonical productions remain incomplete


#### Where

AC07 through AC08, lines 143-240; the Betterem, math, and attributes rows in AC12, lines 375-380


#### Issue

The plan still defines several byte decisions by reference to an outcome rather than by a complete serialization
rule. The delimiter rule says to escape a character when concatenation would reparse as a different node, but does not
define that predicate for nested or adjacent children, source-escaped delimiters, or literal backslashes. The table
rule that a literal backslash is one byte is insufficient for a semantic backslash immediately before a cell pipe:
one backslash plus `|` reparses as an escaped pipe and loses the backslash. The Betterem row identifies a disjoint
owner but does not identify its additional syntax or canonical spelling. Inline math also lacks a body and close
escaping rule beyond the delimiter names.


#### Impact

Independent implementations can emit different bytes for valid ASTs, or emit bytes that do not reparse to the same
AST. This defeats the exact-byte, semantic-preservation, and idempotence claims for core and extension content.


#### Suggestion

Specify normative context-sensitive emission rules for delimiter runs, source escapes, literal backslashes, and table
cell pipes, including representative nested and adjacent cases. Define every Betterem production and its canonical
bytes, and define the accepted and escaped inline-math body grammar. State the reparse invariant for each rule.


#### Outcome


#### S06: Baseline coverage conflicts with extension fail-closed behavior


#### Where

AC04, lines 55-67; AC11, lines 296-304; and the block profile rows in AC12, lines 347-353


#### Issue

AC04 says that no valid CommonMark or GFM form other than the listed policy exclusions and raw HTML is rejected. The
extension rules separately reserve baseline-valid text when an exact extension opener matches and then reject missing
children or malformed metadata. For example, a CommonMark paragraph such as `!!! note` with no indented child is
claimed as an admonition and fails; a valid fence with a final registered-looking but malformed metadata group also
fails. These are not among the stated baseline exclusions.


#### Impact

The acceptance contract cannot tell an implementation whether to preserve an ambiguous source as valid baseline
Markdown or fail it as an extension. The claimed complete CommonMark/GFM coverage and the fail-closed profile behavior
therefore produce different results for the same source, making coverage fixtures and compatibility decisions
non-deterministic.


#### Suggestion

State the precedence explicitly: either permit exact extension claims to reserve and reject overlapping baseline-valid
source, then list that as an explicit profile exclusion, or require extension predicates to yield to baseline parsing
when the required extension span is incomplete. Add fixtures for both branches, including empty-child headers and
malformed registered fence metadata.


#### Outcome


## Notes

The plan has one block-dispatch statement and one inline-dispatch statement. Reference collection is a distinct
prepass, and block-attribute attachment is a distinct post-block phase rather than a duplicate dispatch. Block-math
attributes are placed on the following same-prefix line, definition-list serialization states an inverse grammar, raw
HTML rejection is explicit, normalized-fence idempotence is stated, and optimistic multi-file writes are specified.

No tests, builds, or linters were run.
