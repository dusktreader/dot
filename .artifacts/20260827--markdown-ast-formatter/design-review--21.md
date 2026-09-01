# Design Plan Review: Canonical AST-based Markdown formatter

**Iteration 21**

This iteration re-reviews only S02 from iteration 20 and checks the requested round-trip contract and structural
regressions.


## Source Artifact

/Users/tucker.beck/src/dusktreader/dot/.artifacts/20260827--markdown-ast-formatter/design-plan.md


## Overview

The review finds:

- **Critical**: 0
- **Significant**: 1
- **Trivial**: 0

The math and arbitrary table-backslash portions are substantially specified, but the delimiter codec and canonical AST
delimiter metadata remain ambiguous. S02 is partially resolved.


## Prior Review Resolution

- **S02** ⚠: Inline and block math now specify left-to-right encode/decode behavior, including block protection, and
  table escaping covers arbitrary semantic backslash runs. Label literal escaping is explicit and the parity rule
  applies
  to labels. Core, mark, caret, and tilde boundary predicates remain undefined, and delimiter metadata is not
  consistently defined for normalized-AST equality.


## Findings

### Summary

| Finding ID | Title                                              | Outcome |
| ---------- | -------------------------------------------------- | ------- |
| S02        | Delimiter codec and delimiter metadata remain open |         |


### Significant

#### S02: Delimiter codec and delimiter metadata remain open


#### Where

AC07-AC08 and AC12-AC13, approximately lines 167-185, 234-249, 354-371, 408-411, and 467-476.


#### Issue

The plan now gives a useful parity formula for semantic backslashes, explicit inline and block math codecs, and an
arbitrary-run table formula. The delimiter contract is still not finite or executable:

- `protected delimiter`, `adjacent`, `forming a longer run`, and `boundary-safe` have no exact predicates. The plan
  does not define the bytes, left/right context, maximal delimiter run, or existing-backslash parity for each opening,
  closing, and sibling boundary.
- The candidate rule for `*`/`_` and `**`/`__` does not say which delimiter changes, how its safety is determined, or
  how the fallback literal escape is encoded. It also conflicts with the earlier claim that the canonical productions
  are exactly `*children*` and `**children**`.
- Applying the same rule to mark, caret, and tilde does not define collisions among `==`, `^^`, `^`, `~`, and `~~`,
  especially where longest-delimiter precedence changes the parse.
- Math explicitly excludes source delimiter kind from normalized-AST equality, but AC13 also says that math delimiter
  kind survives in the AST and canonical source. Core `*` versus `_` spelling and any collision-selected alternative
  have no equivalent equality rule. The plan therefore does not state which delimiter metadata is semantic and which is
  source-only.


#### Impact

Independent implementations can choose different canonical bytes, or canonical bytes can reparse into different
nested delimiter nodes. AC13's normalized-AST and idempotence guarantees remain untestable for delimiter collisions,
and the metadata contradiction leaves the equality contract underspecified even though the math byte codecs themselves
are now invertible.


#### Suggestion

Replace the delimiter prose with a finite table or algorithm that defines, for every core and extension delimiter, the
opening and closing claim, left/right context, maximal-run rule, existing-backslash parity, collision-safe output, and
fallback escape bytes at every boundary. Align the canonical-production statement with the permitted underscore
alternatives. Explicitly declare whether each source delimiter spelling is retained in the AST, excluded from
normalized-AST equality, or preserved by canonical source; apply the same decision to math and core delimiter metadata.


#### Outcome


## Notes

The label escape and table-run rules are sufficient for the stated canonical encoding; no separate label or table
finding
is carried forward. No structural regression was found in the requested neighboring contracts. AC03 still rejects nested
or non-first H1s,
and AC09 retains heading hierarchy and policy checks. AC04 and AC12 retain complete-opener profile precedence over
baseline parsing. AC11 retains the fence, metadata, annotation, and collision-safe delimiter rules. AC06 retains raw
HTML rejection; AC04, AC09, and AC10 retain policy restrictions; and AC14-AC16 retain idempotence, atomic write, and
multi-file safety requirements. Those guarantees remain contingent on resolving S02. No tests, builds, or linters were
run.
