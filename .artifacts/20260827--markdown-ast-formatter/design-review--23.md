# Design Plan Review: Canonical AST-based Markdown formatter

Iteration 23 is an independent re-review of only S02 from iteration 22. It checks the delimiter and round-trip
contract plus the requested neighboring structural guarantees.


## Source Artifact

/Users/tucker.beck/src/dusktreader/dot/.artifacts/20260827--markdown-ast-formatter/design-plan.md


## Overview

The review finds:

- **Critical**: 0
- **Significant**: 1
- **Trivial**: 0

The plan now assigns delimiter ownership, excludes delimiter spelling from normalized-AST equality, and specifies
inline and block math codecs. The delimiter contract still has an incorrect/incomplete flanking predicate, so the plan
is not approved.


## Prior Review Resolution

- **S02** ⚠: `~~` is now exclusively core strike, profile `~` is limited to complete single-character spans, profile
  precedence and fallback rejection are explicit, and delimiter metadata is source-only for normalized equality. The
  finite opener/closer rules remain incomplete because they omit the whitespace alternative required by CommonMark
  flanking and do not define the Unicode whitespace/punctuation classifiers or boundary treatment.


## Findings

### Summary

| Finding ID | Title                                           | Outcome |
| ---------- | ----------------------------------------------- | ------- |
| S02        | Finite delimiter flanking predicates incomplete |         |


### Significant

#### S02: Finite delimiter flanking predicates incomplete


#### Where

AC07-AC08 and AC12, approximately lines 175-205, 248-273, 390-411, and 450-451.


#### Issue

The plan gives run lengths, boundary locations, parity encoding, candidate ownership, and a collision rejection
rule. Its opener and closer predicates are not the complete CommonMark flanking rules. The opener permits a run when
the right neighbor is non-punctuation or the left neighbor is punctuation, but the second branch must also permit a
left whitespace neighbor. The closer has the symmetric omission: its second branch must also permit a right whitespace
neighbor. For example, a valid core span such as `*foo!*` has a closer preceded by punctuation at the source boundary,
which the stated predicate does not claim.

The plan also uses `whitespace`, `punctuation`, and absent source neighbors without defining their Unicode classifiers
or sentinel behavior. Applying the same underspecified rule to profile `==`, `^^`, `^`, and `~` leaves their exact
canonical encoding unresolved at punctuation and whitespace boundaries.


#### Impact

An implementation following the written predicate can reject valid CommonMark emphasis and strong forms, or choose
different escaping and alternate delimiters from another implementation. The resulting core and profile output cannot
reliably satisfy the stated reparse, normalized-AST, and idempotence invariants.


#### Suggestion

State the exact finite predicates, including boundary sentinels and Unicode classification. For a run, define opening
flanking as right not Unicode whitespace and (right not Unicode punctuation or left Unicode whitespace or punctuation);
define closing flanking symmetrically as left not Unicode whitespace and (left not Unicode punctuation or right Unicode
whitespace or punctuation). State how these predicates combine with the run-length, single-character profile, and
backslash-parity rules, and apply the same explicit definitions to every owned delimiter.


#### Outcome


## Notes

Inline and block math codecs, table pipe runs, label escaping, normalized delimiter metadata, `~~`/`~` and `^^`/`^`
ownership, profile precedence, nested headings, AC01-AC17 structure, raw HTML rejection, reparse/idempotence, and
optimistic multi-file writes remain covered. No separate regression finding is carried forward. No tests, builds, or
linters were run. Because S02 remains significant, the design plan is not approved.
