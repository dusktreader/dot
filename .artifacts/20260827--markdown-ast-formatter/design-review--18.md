# Design Plan Review: Canonical AST-based Markdown formatter

Iteration 18 re-reviews S01 and S02 from iteration 17 and checks for obvious regressions in the requested heading,
serialization, precedence, policy, round-trip, and write-safety areas.


## Source Artifact

/Users/tucker.beck/src/dusktreader/dot/.artifacts/20260827--markdown-ast-formatter/design-plan.md


## Overview

The review surfaced findings:

- **Critical**:    1
- **Significant**: 1
- **Trivial**:     0


The Betterem ownership conflict is resolved. Exact serialization rules improved but still do not establish a complete
reparse-safe algorithm for delimiter boundaries, backslash adjacency, and math bodies. Three supporting headings have
also regressed to the acceptance-criteria heading level.


## Prior Review Resolution

- **S01** ✓: AC12 and the matrix now consistently make core the sole owner of every `*` and `_` delimiter run, with
  Betterem only an option on core parsing.
- **S02** ⚠: Core collision rules, literal backslash output, table escaping, and math rules are more explicit, but
  closing-boundary collisions, extension delimiter escaping, backslash parity, and block-math delimiter collisions
  remain unspecified or contradictory.


## Findings

### Summary

| Finding | Title                                            | Outcome |
| ------- | ------------------------------------------------ | ------- |
| C01     | Supporting headings regress to AC level          |         |
| S02     | Exact delimiter and math round trips remain open |         |


### Critical

#### C01: Supporting headings regress to AC level


#### Where

Acceptance Criteria, `Canonical output` and `AC12`, lines 201, 369, and 394


#### Issue

`Table serialization details`, `Block profile`, and `Inline and fence profile` are `####` headings, the same level as
the numbered AC headings. Iteration 17 recorded these supporting headings as `#####`; the current plan has regressed
them to `####`. AC01 through AC17 remain correctly numbered, but they are no longer the only headings at that level.


#### Impact

The plan's nested structure no longer distinguishes acceptance criteria from their supporting detail. This creates an
ambiguous AC inventory for implementation planning and violates the resolved heading-structure contract.


#### Suggestion

Change `Table serialization details` to `#####` under AC07, and change `Block profile` and `Inline and fence profile`
to `#####` under AC12. Keep AC01 through AC17 as the only `#### AC##` headings.


#### Outcome


### Significant

#### S02: Exact delimiter and math round trips remain open


#### Where

AC07-AC08, AC11, and AC12-AC13, approximately lines 158-244, 317-340, and 349-477


#### Issue

The additions address the prior finding's intent but leave several exact-byte cases without an executable rule:

- The core delimiter algorithm describes escaping a right-hand child or atom and repeating until the result cannot be
  parsed. It does not define the predicate or byte choice at a closing boundary where the child ends in a delimiter and
  the enclosing close follows. "Can be parsed" is a parser-dependent stopping condition, not a finite serialization
  rule.
- Mark, caret, and tilde nodes say to emit recursively rendered children with the same delimiter, but do not specify
  how a child literal delimiter or a literal backslash adjacent to a delimiter is escaped. The general rule that a
  literal backslash emits two bytes is insufficient by itself: a semantic literal backslash followed by a literal `*`
  needs backslash-parity handling so the `*` does not become a delimiter. The table backslash-plus-pipe exception does
  not define the analogous general case.
- Inline math does not define the escape parity when a literal dollar is adjacent to an existing math backslash. Block
  math accepts `\[` bodies whose line content may be `$$`, but canonicalizes every block to `$$` delimiters, making that
  body line a canonical closing delimiter. The plan also retains math delimiter kind as AST metadata while requiring
  `$body$` and `\(body\)` to share canonical source and reparse to the identical normalized AST.


#### Impact

Independent serializers can emit different bytes or produce output that reparses into different inline or block nodes.
Nested emphasis, extension bodies, literal backslashes, math containing dollars or delimiter-like lines, and the stated
idempotence invariant therefore remain untestable for these cases.


#### Suggestion

Specify a semantic-atom serializer with explicit opening and closing boundary cases, including which side supplies the
escaped byte and how escape parity is computed. Apply the same rule, or a separately complete rule, to mark, caret, and
tilde bodies. Define the exact normalized math-body grammar and dollar/backslash encoding, then either reject or encode
`$$` lines in `\[` bodies before canonicalizing to `$$`. Finally, either normalize delimiter kind out of the compared
AST
or preserve it in canonical source; retaining source kind while emitting one source spelling cannot satisfy the reparse
invariant.


#### Outcome


## Notes

The requested profile-versus-baseline precedence remains explicit: incomplete profile spans yield to baseline parsing,
while complete spans may fail validation. Fence metadata and annotation restoration, heading policy, raw HTML rejection,
table width and pipe rules, optimistic writes, and multi-file commit behavior are stated clearly enough for this review.
The unresolved exact-byte cases above prevent a clean approval of the idempotence claim. No tests, builds, or linters
were run.
