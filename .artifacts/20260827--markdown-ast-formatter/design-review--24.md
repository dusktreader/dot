# Design Plan Review: Canonical AST-based Markdown formatter

Iteration 24 is a final independent re-review of only S02 from iteration 23. It checks the revised flanking contract
and the requested neighboring invariants without expanding scope.


## Source Artifact

/Users/tucker.beck/src/dusktreader/dot/.artifacts/20260827--markdown-ast-formatter/design-plan.md


## Overview

The review finds:

- **Critical**: 0
- **Significant**: 1
- **Trivial**: 0

S02 is partially resolved. The plan now states the Unicode classifiers and the complete CommonMark boolean forms, but
its boundary sentinel still disagrees with CommonMark. The plan is not approved.


## Prior Review Resolution

- **S02** ⚠: The omitted whitespace alternatives, Unicode classifications, and sentinel behavior are now explicit.
  However, a missing neighbor is defined as non-whitespace and non-punctuation, which rejects valid punctuation-edge
  delimiter runs under the stated CommonMark contract.


## Findings

### Summary

| Finding ID | Title                                    | Outcome |
| ---------- | ---------------------------------------- | ------- |
| S02        | Boundary sentinel is not CommonMark-safe |         |


### Significant

#### S02: Boundary sentinel is not CommonMark-safe


#### Where

AC04, AC07-AC08, and AC12, approximately lines 175-201, 253-327, and 395-415.


#### Issue

The revised predicates correctly include the Unicode whitespace and punctuation alternatives, but the plan defines a
missing neighbor at a source boundary as non-whitespace and non-punctuation. CommonMark treats the beginning and end
as whitespace for flanking purposes. Consequently, a delimiter adjacent to punctuation at a document boundary is not
recognized by the finite codec. For example, `*(foo)*` and `*foo!*` contain valid core emphasis, but the opening or
closing `*` can fail the stated predicate because the other neighbor is punctuation and the boundary sentinel is not
whitespace.


#### Impact

The serializer can reject valid CommonMark input or emit a form that does not reparse to the same AST. This violates
the complete parser-coverage, normalized-AST, and idempotence contracts at exactly the boundary cases S02 is intended
to define.


#### Suggestion

Define the missing neighbor before a run as Unicode whitespace and the missing neighbor after a run as Unicode
whitespace, with punctuation false, matching CommonMark's boundary behavior. Retain the stated Python Unicode
classifiers and apply the corrected boundary values consistently to core and profile delimiter runs, including
backslash parity and the single-character profile restrictions.


#### Outcome


## Notes

AC01-AC17 are sequential. The requested checks found no separate regression in nested heading structure, AC numbering,
core/profile delimiter ownership, math, table, or label codecs, profile precedence, raw HTML rejection, idempotence, or
optimistic write safety. No tests, builds, or linters were run.
