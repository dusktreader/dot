# Design Plan Review: Canonical AST-based Markdown formatter

**Iteration 09**

Iteration 09 re-reviews the revised design against iteration 08, with emphasis on executable profile grammars,
acceptance-
criteria structure, complete CommonMark and GFM coverage, ownership and relationships, canonical bytes, fence semantics,
raw HTML, wrapping, and idempotence.


## Source Artifact

/Users/tucker.beck/src/dusktreader/dot/.artifacts/20260827--markdown-ast-formatter/design-plan.md


## Overview

The review surfaced findings:

- **Critical**:    2
- **Significant**: 3
- **Trivial**:     0


## Prior Review Resolution

- **C01** ⚠: The matrix now gives exact spellings and several rejection predicates, but details closure, block
  termination, attribute logical-line scope, and metadata composition remain underdefined.
- **C02** ⚠: AC12 exists and AC01 through AC17 are contiguous, but the two matrix headings are `####` siblings of AC12
  rather than content nested beneath that criterion.
- **S01** ⚠: The previously missing CommonMark variants are named, but the plan still does not distinguish malformed
  extension openers from ordinary baseline punctuation, so the complete-coverage claim remains contradictory.
- **S02** ✓: Math delimiter identity remains explicit in the AST and canonical output.
- **S03** ✓: Core reference definitions now specify legal source forms, resolution, canonical spelling, and discard
  behavior.
- **S04** ⚠: Dispatch order and target sets are substantially clearer, but unresolved opener predicates and fence
  metadata
  ownership still prevent an independent implementation from reproducing every claim.
- **S05** ✓: Empty and absent fence info normalize to AST `text`, and AC13 preserves that equality.


## Findings

### Summary

| Finding | Title                                               | Outcome |
| ------- | --------------------------------------------------- | ------- |
| C01     | Extension matrix is not nested under AC12           |         |
| C02     | Extension grammars still leave ownership undefined  |         |
| S01     | Baseline coverage conflicts with malformed openers  |         |
| S02     | Canonical bytes remain incomplete for several nodes |         |
| S03     | Fence metadata has no unique canonical composition  |         |


### Critical

#### C01: Extension matrix is not nested under AC12


#### Where

Acceptance Criteria — AC12 and the `Block profile` and `Inline and fence profile` headings, approximately lines 245–315


#### Issue

The plan adds AC12, but both profile headings use `####`, the same level as the individual AC headings. They are
therefore
siblings of AC12 in the document structure, not sections contained by it. The extension matrix is supporting material
for
AC12, but the Markdown hierarchy does not express that relationship.


#### Impact

The design plan still violates the canonical acceptance-criteria structure and leaves the extension contract without a
stable structural parent. Review and implementation tooling that extracts AC sections can omit or misassociate the
matrix.


#### Suggestion

Make `Block profile` and `Inline and fence profile` headings children of AC12, such as `#####` headings, or place the
matrix directly inside the AC12 criterion. Keep the complete AC01–AC17 sequence unchanged.


#### Outcome


#### C02: Extension grammars still leave ownership undefined


#### Where

AC05, AC12 profile rows, and dispatch rules, approximately lines 93–115 and 254–315


#### Issue

The rows are much more concrete, but several source boundaries and ownership decisions remain non-executable:

- Details rejects a “malformed closure” even though no closure production exists in its accepted grammar.
- Definition-list and footnote termination refers to an unindented `TERM`, but does not define the claim boundary or
  precedence against an ordinary paragraph and the other block owners.
- “Same logical line” for attached attributes is undefined for soft breaks and nested block rendering.
- SuperFences calls metadata a “final fence suffix” but does not define whether ordinary info may precede it, or which
  owner claims the combined form.

The repeated inline-dispatch paragraphs also present the ownership contract twice without a single authoritative
statement.


#### Impact

Two conforming implementations can choose different source spans for the same bytes, especially at block termination,
attribute attachment, and fence metadata boundaries. That changes AST relationships and defeats the fail-closed and
idempotence promises.


#### Suggestion

For every profile owner, state one complete source production, opener predicate, source-span endpoint, recursion rule,
termination rule, and precedence rule. Define attribute logical lines in terms of normalized source spans, define the
actual details closure or remove the closure reference, and split SuperFences into explicit ordinary-info and metadata
productions. Retain one dispatch list as the authority.


#### Outcome


### Significant

#### S01: Baseline coverage conflicts with malformed openers


#### Where

AC04, AC08, and the math, emoji, mark, caret, and tilde rows, approximately lines 44–59, 160–199, and 283–287


#### Issue

AC04 says no valid CommonMark or GFM form is rejected except the enumerated policy restrictions and raw HTML. AC08 and
multiple profile rows also say a recognized opener with no valid completion fails. The plan does not define when `$`,
`:`,
`^`, `~`, or another punctuation character is a recognized extension opener rather than ordinary text. Consequently,
ordinary baseline prose such as `costs $5` or `ratio: 3:1` can either remain valid text or fail, depending on the
implementation's claim heuristic. “Any other shortcode spelling fails” makes the emoji case especially direct.


#### Impact

The implementation cannot satisfy both complete baseline coverage and fail-closed extension parsing. It may reject valid
CommonMark/GFM prose that is not an extension use, creating an unlisted policy restriction and a corpus compatibility
gap.


#### Suggestion

Define an explicit opener predicate for each extension that leaves unmatched punctuation unclaimed unless the predicate
is
met, while still failing a syntactically recognized but incomplete construct. If the intended policy rejects ordinary
uses,
list each rejected form in AC04 and fixtures instead of claiming complete baseline coverage.


#### Outcome


#### S02: Canonical bytes remain incomplete for several nodes


#### Where

AC07–AC10 and the core/extension matrix, approximately lines 129–243 and 279–289


#### Issue

The plan now fixes wrapping, block spacing, inline-code delimiters, list indentation, and much of table sizing, but it
still does not choose unique bytes for every promised core and extension node. In particular:

- Core emphasis, strong, and strike-through do not have a canonical delimiter-selection and recursive-rendering
  production.
- Bare GFM autolinks do not state whether canonical output preserves the bare form, uses angle form, or renders as a
  normal link with a normalized destination.
- Table serialization does not define escaping for a literal pipe in a normal cell, or whether separator width means
  dash count or complete separator-cell width when alignment markers are present.
- Multiline reference titles are accepted, but their line-ending, indentation, and internal-whitespace normalization to
  `QUOTED` is not specified.
- Definition-list and footnote rows describe retention and indentation but do not give complete canonical productions.


#### Impact

Independent serializers can emit different bytes for the same normalized AST. Exact `check` behavior and the claimed
second-pass byte identity therefore remain untestable even when parsing and semantic preservation succeed.


#### Suggestion

Add a canonical production for every core and profile node, including delimiter choice, recursive child rendering, GFM
autolink spelling, table escaping and width equations, multiline-title normalization, and definition-list/footnote
emission. Add exact-byte examples for each equivalent source family.


#### Outcome


#### S03: Fence metadata has no unique canonical composition


#### Where

AC11 and the SuperFences metadata row, approximately lines 223–233 and 289–295


#### Issue

The fence contract defines delimiter safety and the annotation marker relationship, but it does not define the complete
composition of info text and metadata. “A final fence suffix is ordinary info or exactly” the metadata object leaves
unclear whether a source such as ````python {title="Demo"}` is accepted, which AST field owns `python`, and how the
canonical info string combines both parts. Annotation markers are removed from payload into metadata, but delimiter
selection and payload-newline decisions do not say whether they operate before or after that removal. The output order
of combined language, title, line-number, highlight, and annotation metadata is also not fully stated.


#### Impact

Fence inputs with valid language text plus SuperFences metadata can receive different ownership, delimiter, and info
bytes. A second parse may then produce a different fence AST or interpret metadata as ordinary info.


#### Suggestion

Specify the complete fence-info grammar and AST fields for ordinary language info, metadata, and their combined form.
Define metadata ordering, annotation-definition ordering, and whether fence delimiter selection and payload newline
normalization run on the post-annotation normalized payload. Provide canonical byte examples for empty info, language
plus
metadata, backtick-bearing info, and annotated payloads.


#### Outcome


## Notes

AC06 remains materially sound: it separates body raw-HTML rejection from frontmatter, code, entities, and valid
angle-bracket destinations, and covers HTML block and inline production families. AC08's wrapping algorithm is now
executable enough to establish boundary-only breaks, overlong-atom behavior, indentation exclusion, and hard-break
canonicalization. AC13 and AC17 state reparsing and second-pass byte identity explicitly. No tests, builds, or linters
were
run.
