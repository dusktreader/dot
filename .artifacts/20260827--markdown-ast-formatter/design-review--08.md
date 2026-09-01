# Design Plan Review: Canonical AST-based Markdown formatter

**Iteration 08**

Iteration 08 re-reviews the revised design against iteration 07, with emphasis on executable profile grammars, complete
CommonMark and GFM coverage, extension ownership, canonical bytes, raw HTML rejection, fence normalization, and artifact
structure.


## Source Artifact

/Users/tucker.beck/src/dusktreader/dot/.artifacts/20260827--markdown-ast-formatter/design-plan.md


## Overview

The review surfaced findings:

- **Critical**:    2
- **Significant**: 3
- **Trivial**:     0


## Prior Review Resolution

- **C01** ⚠: Primitive lexical rules are substantially more explicit, but several block and inline matrix rows still
  lack executable source grammars and rejection predicates.
- **C02** ✓: The five canonical top-level design-plan sections remain present. A new acceptance-criteria numbering
  regression is recorded below.
- **S01** ✓: Fuzzy links, email addresses, IP addresses, and their pinned linkify configuration remain explicit.
- **S02** ✓: Math delimiter identity remains preserved in the AST and canonical source.
- **S03** ✓: Core reference definitions have explicit resolution, canonicalization, and discard behavior.
- **S04** ⚠: Width, wrapping, and claim ordering are clearer, but claim completion still depends on the underdefined
  extension grammars carried in C01.
- **S05** ✓: Empty and absent fence info normalize to AST `text`, and AC13 now declares that equality.


## Findings

### Summary

| Finding | Title                                               | Outcome |
| ------- | --------------------------------------------------- | ------- |
| C01     | Extension rows are not executable grammars          |         |
| C02     | Acceptance-criteria numbering breaks structure      |         |
| S01     | Complete CommonMark/GFM coverage remains overstated |         |
| S02     | Extension targets and dispatch remain ambiguous     |         |
| S03     | Canonical bytes are underdefined for core nodes     |         |


### Critical

#### C01: Extension rows are not executable grammars


#### Where

AC05 and the Extension source matrix, approximately lines 92–267


#### Issue

AC05 defines useful lexical primitives, but many accepted constructs still use descriptive shorthand rather than a
complete grammar. Admonitions, details, tabs, definition lists, footnotes, and directives do not specify every allowed
whitespace position, continuation rule, terminator, or source-span boundary. Inline attributes do not define their
attachment target. Betterem delegates delimiter validity to “CommonMark intraword rules,” while SuperFences metadata
does not fully define the relationship between the ordinary info prefix, the metadata suffix, and payload annotations.
The ordinary-text predicate therefore remains circular: a construct is claimed when its “complete grammar” matches, but
several complete grammars are not stated.


#### Impact

Independent implementations can accept different source spans, assign different owners, or construct different AST
fields while claiming the same immutable profile. Malformed openers can also fall through to prose inconsistently,
which defeats the fail-closed and deterministic-claim contracts.


#### Suggestion

Give every matrix row an executable grammar with exact token spelling, permitted whitespace, escape processing,
recursion, continuation and termination rules, ownership, cardinality, and explicit malformed-opener predicates. Define
the complete recursive delimiter rules instead of referring to external prose such as “intraword rules.” State the
annotation-to-payload relationship and the exact target set for attributes.


#### Outcome


### Critical

#### C02: Acceptance-criteria numbering breaks structure


#### Where

Acceptance Criteria, approximately lines 15–318


#### Issue

The numbered criteria jump from AC11 to an unnumbered Extension source matrix and then to AC13. No AC12 exists. The
matrix may be supporting material, but it cannot satisfy the required contiguous `AC01`, `AC02`, ... sequence by being
an unnumbered heading.


#### Impact

The artifact does not conform to the canonical design-plan structure, and review or implementation work cannot refer to
the extension-profile behavior through a stable acceptance criterion. The numbering gap also makes coverage tracking
ambiguous.


#### Suggestion

Add a testable `AC12` criterion for the extension profile and place the matrix beneath it, or renumber the criteria so
that every acceptance criterion is contiguous from AC01 through the final criterion. Keep the matrix as supporting
content only if its governing behavior is stated in the numbered criterion.


#### Outcome


### Significant

#### S01: Complete CommonMark/GFM coverage remains overstated


#### Where

AC04, the lexical contract, and the Core references row, approximately lines 44–114 and 234–235


#### Issue

AC04 still promises complete CommonMark 0.31.2 and GFM source coverage, but the stated core grammar excludes legal
variants without identifying them as policy exclusions. The contract makes titles and labels LF-free, and the reference
row requires single-line definitions with exactly one ASCII space between fields. CommonMark permits line-ending and
multi-line forms in link titles and reference definitions, plus legal indentation and separating-whitespace variants.
Inline code is accepted as well, but its source variants are not enumerated in the profile. The plan now covers empty
destinations, both hard-break forms, legal list spacing, and ragged tables, but those fixes do not establish complete
coverage for the remaining variants.


#### Impact

An implementation cannot tell whether these inputs must parse and canonicalize or must be rejected as an intentional
repository policy. It may silently reject claimed CommonMark input, producing a compatibility gap and an incomplete
fixture contract.


#### Suggestion

Either enumerate and accept the remaining legal CommonMark/GFM variants, including multi-line titles and reference
definitions, or narrow AC04 to the actual finite subset and list every excluded grammar as an explicit policy rejection
with fixtures. Keep source acceptance separate from canonical spelling.


#### Outcome


#### S02: Extension targets and dispatch remain ambiguous


#### Where

The inline and fence profile matrix plus dispatch paragraphs, approximately lines 230–267


#### Issue

The footnote and abbreviation rows resolve the specific relationship gap from iteration 07, but other relationships are
still not executable. “Immediately attached” attributes do not identify which block or inline node kinds consume them,
how attachment wins when multiple nodes are adjacent, or whether the same syntax has both block and inline owners. The
annotation row does not state whether a payload-line marker remains payload text or becomes an annotation child after
normalization. The abbreviation boundary says a use is bounded by a Unicode letter, number, or underscore, which is
ambiguous about whether those characters are allowed or prohibited at the boundary.


#### Impact

Dispatch can produce different AST ownership and relationships for the same bytes. That changes rendered output and
makes nested attributes, annotations, and abbreviation uses impossible to verify consistently.


#### Suggestion

Define the target node kinds and attachment precedence for attributes, the exact AST ownership and source span for
annotation markers and definitions, and the behavior of repeated footnote uses. Rewrite abbreviation boundaries as an
explicit allowed-neighbor predicate, with code, link, image, math, and other opaque-span exclusions stated in the same
grammar.


#### Outcome


#### S03: Canonical bytes are underdefined for core nodes


#### Where

AC07–AC12, approximately lines 128–200


#### Issue

The plan promises deterministic bytes but leaves several serializer choices as assertions. Table output is “aligned”
with one space inside each pipe, without defining leading and trailing pipes, the width and padding metric, separator
cell widths, or the exact escaping and alignment algorithm. Inline code has no canonical delimiter, padding, or
line-ending rule. “Canonical blank lines” and “deterministic indentation” likewise do not state exact counts for block
boundaries and nested list or quote structures.


#### Impact

Two conforming implementations can emit different Markdown for the same normalized AST. Byte-level idempotence,
`check`, and the promised unique canonical representation then remain untestable even when parsing and semantic
preservation are correct.


#### Suggestion

Specify serializer productions for every core node, including table pipe placement, width calculation, padding,
alignment markers, inline-code delimiter selection and normalization, blank-line counts, and nesting indentation. Add
fixtures for equivalent source variants and assert exact canonical bytes.


#### Outcome


## Notes

AC06 is materially clearer and has no finding: it separates body raw-HTML rejection from frontmatter, code, entities,
and valid angle-bracket destinations, and it covers tags, comments, declarations, processing instructions, and CDATA.
AC11 and AC13 now align the empty-fence normalization invariant. The pinned parser and oracle roles, core reference
ordering, write safety, multi-file behavior, and wrapper contract show no regression in this review. No tests, builds,
or
linters were run.
