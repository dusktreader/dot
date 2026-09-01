# Design Plan Review: Canonical AST-based Markdown formatter

Iteration 07 re-reviews the revised plan against iteration 06, using its findings as the checklist and checking for
regressions in the parser boundary, canonicalization, idempotence, and write safety.


## Source Artifact

/Users/tucker.beck/src/dusktreader/dot/.artifacts/20260827--markdown-ast-formatter/design-plan.md


## Overview

The review surfaced findings:

- **Critical**:    1
- **Significant**: 3
- **Trivial**:     0


## Prior Review Resolution

- **C01** ⚠: Dependency versions, parser options, emoji syntax, and attribute keys are now explicit, but several
  extension grammars remain non-executable.
- **C02** ✓: The plan retains the canonical Goal, Acceptance Criteria, Architecture, Unknowns, and Technical Notes
  structure.
- **S01** ✓: Fuzzy links, email addresses, and IP addresses are enabled and included in the pinned runtime contract.
- **S02** ✓: Math delimiter kinds now remain unchanged in both the AST contract and canonical source.
- **S03** ✓: Core reference definitions have an explicit grammar, canonical destination and title handling, and a
  deliberate discard-after-resolution policy.
- **S04** ⚠: Wrapping boundaries, width, and claim characters are substantially more concrete, but the dispatch still
  delegates some claims to vague extension grammar terms.
- **S05** ⚠: Tilde fallback handles backticks in info strings, but empty-info normalization is not aligned with the
  promised preservation and reparse invariants.


## Findings

### Summary

| Finding | Title                                                    | Outcome |
| ------- | -------------------------------------------------------- | ------- |
| C01     | Extension grammars are not fully executable              |         |
| S01     | Complete CommonMark coverage conflicts with restrictions |         |
| S02     | Extension relationships and placement are incomplete     |         |
| S03     | Empty fence info breaks the round-trip contract          |         |


### Critical

#### C01: Extension grammars are not fully executable


#### Where

AC05 and the Extension source matrix — approximately lines 89–227


#### Issue

The plan calls the profile immutable, but several accepted forms still lack a deterministic grammar. `COND` removes
spaces without defining which source whitespace is accepted. Key names may contain `+`, which is also the key
separator in `++KEY(+KEY)++`. Mark, caret, and tilde bodies reject “ambiguous or malformed” runs without defining
those cases, and annotations leave `text`, duplicate markers, and line mapping unspecified.


#### Impact

Independent implementations can accept different source spans or construct different AST fields while claiming the
same finite profile. This also leaves the inline claim predicate non-reproducible.


#### Suggestion

Define a complete grammar and precedence for each remaining profile form, including source whitespace, delimiter
escapes, key characters, recursive bodies, and annotation cardinality and line association. Replace subjective terms
such as “ambiguous” with explicit rejection predicates.


#### Outcome


----

### Significant

#### S01: Complete CommonMark coverage conflicts with restrictions


#### Where

AC04–AC05 and AC08 — approximately lines 44–143


#### Issue

AC04 claims complete CommonMark and GFM source coverage, while AC05 requires every core destination to be nonempty;
CommonMark permits an empty inline destination such as `[x]()`. AC05 also describes one-space list markers and AC08
only defines the backslash form of a hard break without stating whether other legal whitespace variants are accepted or
explicitly rejected as policy.


#### Impact

The implementation cannot distinguish a parser coverage requirement from an unstated style restriction. Supported
inputs may be rejected accidentally, or different implementations may choose different canonical representations.


#### Suggestion

Separate source grammar from canonical spelling. Accept and canonicalize all claimed CommonMark/GFM variants, including
empty destinations, space-based hard breaks, and legal list indentation and marker spacing, or list each excluded form
as an explicit policy rejection with fixtures.


#### Outcome


----

#### S02: Extension relationships and placement are incomplete


#### Where

The block and inline extension matrix and the serialization paragraph — approximately lines 201–227


#### Issue

The footnote row defines only definitions; the inline dispatch has no footnote-reference owner for `[^ID]`. The
abbreviation row likewise defines declarations but not usage matching or boundaries. Footnote definitions and
abbreviation definitions are both emitted after the body, but their relative canonical order is unspecified.


#### Impact

The promised first-reference footnote ordering, undefined-reference validation, abbreviation relationships, and unique
canonical bytes cannot be implemented or verified from the plan.


#### Suggestion

Add explicit inline grammars and dispatch ownership for footnote references and abbreviation uses, including exclusions
for code and other opaque spans. Define one deterministic ordering for every post-body definition family.


#### Outcome


----

#### S03: Empty fence info breaks the round-trip contract


#### Where

AC11 and AC13 — approximately lines 164–173 and 240–248


#### Issue

AC11 intentionally converts empty fence info to `text`, while AC13 says SuperFences info survives in the AST and
canonical source and requires reparsing to reproduce identical fields. The plan never states that empty info and
`text` are semantically equivalent or that the AST stores the normalized value before the equality check.


#### Impact

An accepted empty-info fence can produce a canonical document whose reparsed info field differs, breaking semantic
idempotence or silently losing source meaning.


#### Suggestion

Choose and state one invariant: normalize empty info to `text` in the AST and declare the two forms equivalent, or
preserve an empty info field and narrow the normalization claim. Align AC11, AC13, and the fence fixtures.


#### Outcome


## Notes

The pinned dependency and oracle configuration, fuzzy autolink settings, core reference policy, explicit separate block
and inline dispatch, raw code payload preservation, positional `----` separator rule, and optimistic per-file
snapshot and atomic replacement contract are otherwise clear. The plan also retains the canonical design-plan section
structure. No tests, builds, or linters were run.
