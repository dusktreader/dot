# Design Plan Review: Canonical AST-based Markdown formatter

Iteration 17 re-reviews the plan against iterations 15 and 16, limited to prior findings and the requested parser,
ownership, serialization, round-trip, policy, idempotence, and write-safety checks.


## Source Artifact

/Users/tucker.beck/src/dusktreader/dot/.artifacts/20260827--markdown-ast-formatter/design-plan.md


## Overview

The review surfaced findings:

- **Critical**:    0
- **Significant**: 2
- **Trivial**:     0

The structural heading regression and the baseline-versus-extension precedence issue are resolved. Fence metadata and
annotation round-trip, block-math attributes, definition-list inversion, policy predicates, raw HTML rejection,
idempotence, writes, and the single-dispatch phase model remain explicit. Betterem ownership still contradicts the
core underscore claim, and exact delimiter and math bytes remain underdefined.


## Prior Review Resolution

- **C01** ✓: `Table serialization details`, `Block profile`, and `Inline and fence profile` are `#####` headings under
  AC07 or AC12; AC01 through AC17 are the only `#### AC##` headings.
- **S01** ⚠: The ownership prose assigns all CommonMark underscore runs to core and makes Betterem disjoint, but the
  Betterem matrix row still claims `_body_` and `__body__` source runs.
- **S02** ⚠: Delimiter and escape rules are more specific, but collision predicates, literal-backslash emission,
  Betterem delimiter bytes, and inline and block math body serialization remain incomplete.
- **S03** ✓: Tilde fallback uses `max(3, longest consecutive tilde run + 1)` after restoration and normalization.
- **S04** ✓: Definition-list framing, termination, EOF behavior, and the canonical inverse remain explicit.
- **S05** ✓: Terminal-character and sentence predicates cover recursive nodes, escapes, entities, empty nodes, links,
  images, code, math, extension atoms, and soft or hard breaks.
- **S06** ✓: An incomplete extension span yields to baseline parsing; a complete recognized span may fail child or
  metadata validation.


## Findings

### Summary

| Finding | Title                                             | Outcome |
| ------- | ------------------------------------------------- | ------- |
| S01     | Betterem still overlaps core underscore ownership |         |
| S02     | Exact core and extension bytes remain incomplete  |         |


### Significant

#### S01: Betterem still overlaps core underscore ownership


#### Where

AC12 ownership rules and the Betterem and smartsymbols row, approximately lines 328-342 and 382.


#### Issue

The ownership prose says core owns all CommonMark underscore delimiter-run semantics and that Betterem never claims an
underscore run. The matrix then says Betterem owns `_body_` and `__body__`, which are underscore runs and valid
CommonMark emphasis and strong forms in ordinary contexts. Those claims cannot simultaneously satisfy the one-owner and
core/Betterem-disjointness requirements.


#### Impact

Implementers cannot determine which dispatcher owns these inputs. They may double-parse them, or treat valid mixed and
nested CommonMark underscore runs as ordinary text, breaking complete baseline coverage and AST-preserving rendering.


#### Suggestion

Choose one source owner and state it consistently in the ownership prose, matrix, and dispatch. To retain core ownership
of CommonMark, remove `_body_` and `__body__` from Betterem's source grammar and define only Betterem syntax whose claim
predicate is disjoint from CommonMark. If Betterem owns underscore syntax instead, give it all underscore delimiter-run
semantics and remove the core claim.


#### Outcome


#### S02: Exact core and extension bytes remain incomplete


#### Where

AC07-AC08 and the Math, Betterem, and Mark/caret/tilde rows in AC12, approximately lines 158-240 and 379-382.


#### Issue

The plan still uses non-executable byte rules in several required cases. "Would merge" does not define the delimiter
collision predicate across nested and adjacent nodes, and "escaped according to its context" does not define literal
backslash emission. Betterem and the mark/caret/tilde extensions defer to recursive rendering without defining all
delimiter-boundary bytes. Inline math says that both input delimiters preserve body semantics while canonicalizing to
`$...$`, but does not define escaping of a body dollar or backslash. Block math likewise lacks a complete canonical body
and newline rule.


#### Impact

Independent implementations can emit different canonical bytes or produce bytes that reparse into different inline or
block extension nodes. Nested emphasis, escaped delimiters, math containing delimiter characters, and literal
backslashes therefore remain incompatible with the exact-byte and idempotence claims.


#### Suggestion

Specify a finite serializer rule for each core and extension node. Define the delimiter-collision predicate and exact
escape count at every child and sibling boundary, literal-backslash handling in each context, and the canonical body
grammar for both inline and block math after delimiter normalization. State the reparse invariant for nested, adjacent,
escaped, and delimiter-containing examples.


#### Outcome


## Notes

The requested phase model is explicit: one block dispatch, one inline dispatch, a reference prepass, and a block-
attribute post-phase. The plan also explicitly covers exact `#####` supporting headings, AC01-AC17 numbering, core and
extension ownership intent, fence metadata and annotations, block-math attributes, definition-list inversion, policy
predicates, raw HTML, normalized-fence idempotence, and optimistic writes. No tests, builds, or linters were run.
