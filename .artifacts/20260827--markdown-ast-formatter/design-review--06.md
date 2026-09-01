# Design Plan Review: Canonical AST-based Markdown formatter

Iteration 06 re-reviews the revised plan against iteration 05, using its findings as the checklist and checking the
parser boundary, canonicalization, idempotence, and write-safety guarantees for regressions.


## Source Artifact

/Users/tucker.beck/src/dusktreader/dot/.artifacts/20260827--markdown-ast-formatter/design-plan.md


## Overview

The review surfaced findings:

- **Critical**:    1
- **Significant**: 5
- **Trivial**:     0


## Prior Review Resolution

- **C01** ⚠: Direct versions, parser options, oracle extension options, and several lexical grammars are now explicit,
  but the emoji catalog and remaining open lexical fields are not identified as exact, versioned contract data.
- **C02** ✓: The noncanonical top-level section is gone; the plan now uses the required Goal, Acceptance Criteria,
  Architecture, Unknowns, and Technical Notes sections.
- **S01** ✓: Block and inline dispatch are separate, each has one authoritative order, and malformed claimed openers
  fail closed.
- **S02** ✓: AC04 now distinguishes complete parser coverage from the H1, hierarchy, heading-style, and bold-subject
  policy rejections.
- **S04** ⚠: The extension matrix now defines substantially more source and output behavior, but core reference
  definition serialization and some extension relationships remain unspecified.
- **S05** ⚠: Width, whitespace, entity, destination, title, and code-span rules are more concrete, but the wrapping
  atomization and claim predicates are still not executable enough for deterministic output.


## Findings

### Summary

| Finding | Title                                                            | Outcome |
| ------- | ---------------------------------------------------------------- | ------- |
| C01     | Finite profile data is not fully identified                      |         |
| S01     | GFM bare autolinks conflict with the pinned options              |         |
| S02     | Math delimiter preservation contradicts canonical bytes          |         |
| S03     | Reference definitions lack a canonical source contract           |         |
| S04     | Inline wrapping and lexical claims remain underspecified         |         |
| S05     | Backtick-only fences cannot represent every accepted info string |         |


### Critical

#### C01: Finite profile data is not fully identified


#### Where

AC05 and the finite lexical contract and extension matrices — approximately lines 66–245


#### Issue

The plan pins the named package versions and most parser options, but `PROFILE_EMOJI_CATALOG` is only a symbolic
reference to a “checked-in emoji fixture.” It gives no artifact identity, revision, digest, or exact contents that
define the accepted shortcode vocabulary. Attribute `key` names also have no lexical grammar, while AC08 refers to a
“constrained grammar in AC14,” which does not define one.


#### Impact

Two conforming implementations can accept different shortcodes or attribute spellings while claiming the same finite
profile. Compatibility fixtures and canonical output therefore still lack a reproducible acceptance boundary.


#### Suggestion

Identify the emoji catalog by an exact repository artifact and immutable version or digest, and define every open
profile lexical field, including attribute keys. Pin any oracle defaults that affect source parsing rather than relying
on unspecified library defaults.


#### Outcome


----

### Significant

#### S01: GFM bare autolinks conflict with the pinned options


#### Where

AC04–AC05 and Architecture — approximately lines 48–100 and 317–333


#### Issue

AC04 promises complete GFM autolink coverage, including bare autolinks. The authoritative runtime configuration sets
`fuzzy_link`, `fuzzy_email`, and `fuzzy_ip` to `false`, which disables the linkify recognition normally used for
scheme-less URLs, bare email addresses, and fuzzy IP forms. The architecture assigns core GFM tokenization to
`markdown-it-py` and does not describe a separate formatter-owned recognizer that restores those forms.


#### Impact

The pinned configuration cannot satisfy the stated GFM baseline for those inputs, or different implementations may
silently fill the gap with different recognizers. Coverage fixtures cannot distinguish a deliberate policy exclusion
from an accidental parser gap.


#### Suggestion

Specify an authoritative recognizer and exact precedence for every required GFM autolink-literal form, or change the
options and fixtures so the pinned parser accepts them. If these forms are intentionally rejected, list that rejection
as an explicit style policy and remove them from the complete-coverage claim.


#### Outcome


#### S02: Math delimiter preservation contradicts canonical bytes


#### Where

Inline and fence profile matrix and AC13 — approximately lines 233–262


#### Issue

The math row canonicalizes `\(...\)` to `$...$` and `\[...\]` to `$$...$$`, while AC13 says the math delimiter is
preserved in both the AST and canonical source. The matrix therefore discards a field that AC13 requires the canonical
source to preserve.


#### Impact

Implementations cannot satisfy both requirements, and round-trip fixtures cannot assert whether delimiter kind is
semantic source meaning or an intentionally normalized spelling.


#### Suggestion

Choose one contract: preserve each delimiter kind in canonical bytes, or state that delimiter kind is AST-only and that
all accepted variants are canonically equivalent. Align AC13, the matrix, and the second-pass invariants with that
choice.


#### Outcome


#### S03: Reference definitions lack a canonical source contract


#### Where

AC07, AC13, and the extension source matrix — approximately lines 116–121 and 253–260


#### Issue

The AST must represent CommonMark reference definitions and preserve reference relationships, but no section specifies
their canonical bytes, destination and title escaping, definition ordering, or placement relative to body and extension
definitions. The statement that definitions use placements “stated in the matrices” does not cover this core construct.


#### Impact

Equivalent reference-link inputs can produce different canonical documents, and a second parse cannot be required to
preserve the promised definition relationships and placement.


#### Suggestion

Add an explicit reference-definition contract covering its accepted grammar, canonical destination and title forms,
case-sensitive identity, ordering, placement, and interaction with footnote and abbreviation definitions.


#### Outcome


#### S04: Inline wrapping and lexical claims remain underspecified


#### Where

AC08 and its input-category table — approximately lines 124–145


#### Issue

The renderer is told to append “inline atoms” and a separator when the next atom fits, but the plan does not define the
atomization, whether a source whitespace boundary exists between adjacent atoms, which line prefixes count toward the
limit, or how leading and trailing whitespace is handled. Ordinary-text escaping still depends on the undefined
condition that a character “could begin a recognized block or inline claim.” The entity rule also names only named
entities and omits canonical handling for numeric entities.


#### Impact

Conforming implementations can insert spaces around adjacent markup, choose different wrap points, or emit different
escaping for the same source. Those differences can alter Markdown meaning and violate deterministic idempotence.


#### Suggestion

Define the inline token stream with explicit breakable-boundary metadata, the exact separator and line-prefix algorithm,
the claim predicates used by ordinary-text escaping, and canonical handling for both named and numeric entities.


#### Outcome


#### S05: Backtick-only fences cannot represent every accepted info string


#### Where

AC04 and AC11 — approximately lines 48–63 and 169–181


#### Issue

The plan accepts all CommonMark-legal fenced code and preserves unknown info text, but canonicalizes every fence to
backticks. A legal tilde fence can have a backtick in its info string; the same info string is illegal after a backtick
opening fence. AC11 also renders an empty info string as `text`, while AC13 claims SuperFences language/info is
preserved.


#### Impact

Some accepted source cannot be rendered as valid canonical Markdown without changing its info semantics. The canonical
output may fail the next parse or silently change the AST's preserved info field.


#### Suggestion

Either choose the canonical fence delimiter based on payload and info-string legality, or explicitly reject the affected
tilde-fence cases as a policy exclusion in AC04. Define whether empty info and `text` are semantically equivalent and
align that decision with AC13.


#### Outcome


----

## Notes

The raw-HTML boundary remains explicit and has no regression: valid autolinks and destinations are classified before
HTML, while HTML productions outside code are rejected and ordinary tag-like text remains ordinary text when it does not
enter those productions.

Code payload whitespace and trailing newlines remain explicitly preserved; the S05 finding concerns fence and info
canonicalization, not payload preservation. The positional `----` hierarchy separator remains idempotent, and AC15–AC16
still define optimistic per-file comparison, atomic replacement, preflight, and partial-commit behavior without claiming
an impossible absolute concurrency guarantee.
