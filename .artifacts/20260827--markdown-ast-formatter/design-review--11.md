# Design Plan Review: Canonical AST-based Markdown formatter

Iteration 11 re-reviews the design plan against iterations 10 and 09, with emphasis on canonical structure, finite
profile ownership, source coverage, canonical bytes, round trips, and write safety.


## Source Artifact

/Users/tucker.beck/src/dusktreader/dot/.artifacts/20260827--markdown-ast-formatter/design-plan.md


## Overview

The review surfaced findings:

- **Critical**:    1
- **Significant**: 8
- **Trivial**:     0


## Prior Review Resolution

- **C01** ✗: The profile headings remain `####` siblings of AC12, and `Table serialization details` remains an `####`
  heading outside AC07. The canonical structural defect is unchanged.
- **S01** ⚠: Per-extension predicates and the ordinary-text fallback are more explicit, but the plan still rejects
  some valid baseline forms through malformed or unknown extension claims without listing those rejections in AC04.
- **S02** ⚠: The plan now specifies block-math delimiter identity and annotation restoration order, but the fence
  grammar still leaves `INFO_TEXT` and annotation-definition boundaries underdefined.
- **S03** ⚠: Core reference resolution and discard behavior are stated in several places, but AC07 still describes a
  reference definition as both emitted and discarded.
- **S04** ⚠: The dispatch lists now include block math and a post-block attribute phase, but the inline list omits the
  smartsymbols owner and the exact block-target attachment and math line predicates remain incomplete.
- **S05** ✓: Empty and absent fence info normalize to AST `text`, and AC13 preserves that equality.
- **S06** ⚠: Definition-list syntax is substantially more concrete, but recursive content, blank-line/EOF behavior, and
  the complete continuation production remain unspecified.


## Findings

### Summary

| Finding | Title                                                                 | Outcome |
| ------- | --------------------------------------------------------------------- | ------- |
| C01     | Acceptance-criteria support remains structurally detached             |         |
| S01     | Profile claims still conflict with complete baseline coverage         |         |
| S02     | Dispatch still omits an owner and exact attachment predicates         |         |
| S03     | Core canonical bytes can diverge on reparse                           |         |
| S04     | Extension rows do not define all canonical bytes                      |         |
| S05     | Fence info and annotation boundaries remain incomplete                |         |
| S06     | Core reference lifecycle still contains contradictory output language |         |
| S07     | Definition-list grammar is not a complete recursive production        |         |
| S08     | Policy exclusions are not finite executable predicates                |         |


### Critical

#### C01: Acceptance-criteria support remains structurally detached


#### Where

Acceptance Criteria — AC07, AC12, `Table serialization details`, `Block profile`, and `Inline and fence profile`,
approximately lines 15–362


#### Issue

AC01 through AC17 are `####` headings, but `Table serialization details`, `Block profile`, and `Inline and fence
profile` are also `####` headings. The extension matrices are therefore siblings of the acceptance criteria rather than
supporting content owned by AC12. The table rules are also placed after AC11 and are not owned by AC07.


#### Impact

A canonical section extractor can omit the matrices or associate them with the wrong criterion. AC07 and AC12 then lack
the detailed contracts required to make serialization and extension ownership implementable.


#### Suggestion

Move `Table serialization details` into AC07 before AC08 and make it a `#####` heading. Make `Block profile` and `Inline
and fence profile` `#####` headings directly under AC12. Keep AC01–AC17 as the only `#### AC##` headings in the
acceptance-criteria section.


#### Outcome


### Significant

#### S01: Profile claims still conflict with complete baseline coverage


#### Where

AC04, AC08, AC11, AC12 profile invalid-behavior cells, and the dispatch paragraphs, approximately lines 44–64,
176–224, 248–273, and 285–369


#### Issue

The plan now names claim predicates, but it still uses incompatible rules for deciding when a profile owns text:

- AC04 and AC08 say an incomplete predicate remains ordinary CommonMark/GFM text.
- AC11 rejects a valid baseline fence info string when its final brace group begins with a known metadata key but is
  malformed.
- AC12 says unknown kinds, bad conditions, malformed extensions, and unclosed math fail, even when their prefixes do
  not satisfy the complete profile production and are valid baseline text.
- Block rows say ownership requires a matching child sequence, while the dispatch says a recognized malformed opener
  fails. Child presence is therefore both part of claiming the span and a post-claim failure.

Examples include an unknown admonition kind, an invalid `@if` condition, a known-prefix but malformed fence metadata
group, and an unclosed inline math delimiter. The plan does not say which are ordinary text and which are recognized
failures.


#### Impact

Two implementations can assign different owners to the same bytes. The formatter cannot simultaneously guarantee
complete CommonMark/GFM coverage, fail-closed profile parsing, and non-circular ownership.


#### Suggestion

Define a finite header/opener predicate separately from the full production for every owner. State the exact source span
claimed after that predicate succeeds, then state which child or terminator errors fail. Any prefix that does not
satisfy
the opener predicate must remain baseline text, unless it is added explicitly to AC04's policy exclusions and fixtures.
Apply the same rule to malformed metadata, unknown extension kinds, conditions, and unclosed inline delimiters.


#### Outcome


#### S02: Dispatch still omits an owner and exact attachment predicates


#### Where

AC08, AC12 inline and block dispatch, the Math and Attributes rows, approximately lines 210–224, 326–329, and 349–362


#### Issue

Adding block math and a post-block attribute phase resolves the largest omission from iteration 10, but the
authoritative
dispatch is still not complete. The matrix owner `Betterem and smartsymbols` is represented only as `betterem` in the
inline list. The block-math entry names delimiters and a body but does not define the exact physical line predicate,
active structural prefix, blank-body/blank-line behavior, or EOF rule. The attribute phase says “same physical source
line” without defining the target's source endpoint for multiline paragraphs, nested blocks, block math, or recursively
rendered containers.


#### Impact

An implementation can dispatch smartsymbols through ordinary text, claim block math with different whitespace or body
boundaries, or attach the same attribute list to different nodes. This changes source spans and can break reparsing even
when the broad dispatch order is followed.


#### Suggestion

List every matrix owner exactly once, including smartsymbols. Give block math an exact line-level opener, terminator,
body, prefix, nesting, and EOF grammar. Define one attribute attachment production that identifies the target's source
span and final physical line for every block target, and state its precedence relative to block and inline claims.


#### Outcome


#### S03: Core canonical bytes can diverge on reparse


#### Where

AC07–AC10, approximately lines 133–224


#### Issue

Several core byte productions remain implicit:

- “Literal label” does not specify canonical label bytes for links and images containing escapes, brackets, entities, or
  inline children.
- Recursive `*`, `**`, and `~~` rendering has no collision rule for adjacent or nested children that would form a
  longer delimiter run or change the parsed node kind.
- Ordinary-text escaping refers to the claim predicate rather than enumerating the complete context-sensitive escape
  set.
- “Every other entity-triggering character” is undefined.
- “Paragraph-like blocks” is undefined, and one LF between two ordinary paragraph siblings would reparse as one
  paragraph rather than two.


#### Impact

Independent serializers can produce different bytes for the same normalized AST. More seriously, the stated one-LF
spacing rule can violate AC13's identical-AST second pass for adjacent paragraph siblings.


#### Suggestion

Specify exact link/image-label and ordinary-text productions, the complete entity encoding table, and
delimiter-collision
handling for every recursive inline node. Define paragraph-like block membership and require separators that preserve
block boundaries on reparsing; add representative nested and adjacent inline cases.


#### Outcome


#### S04: Extension rows do not define all canonical bytes


#### Where

AC07, AC12 Block profile and Inline and fence profile, approximately lines 140–161 and 294–345


#### Issue

The matrix header promises accepted source, fields, nesting, and canonical bytes, but several rows specify only source
recognition or partial normalization. For example, the Admonition and Details rows do not give complete canonical opener
bytes and child/blank-line emission; the Snippet row specifies path quoting but not the full emitted source span; and
the
Zensical row specifies condition whitespace removal without a complete canonical production for each directive and
branch.
The generic rule that extension blocks use four-space child indentation does not fill in missing marker, title, state,
or
field ordering rules. Recursive rendering is also not a canonical byte rule by itself.


#### Impact

Two implementations can preserve the same extension meaning while emitting different headers, quoting, blank lines, or
branch bytes. AC13's exact source and byte identity claim is therefore not reproducible for every profile node.


#### Suggestion

Give every profile owner one explicit canonical production, including opener marker, kind/state, title or path quoting,
field order, child indentation, blank-line placement, and source-span endpoint. Do not rely on “same,” “emit headers,”
or
the generic container rule where exact bytes are required.


#### Outcome


#### S05: Fence info and annotation boundaries remain incomplete


#### Where

AC05, AC11, and the SuperFences metadata row, approximately lines 97–119 and 248–273, 333


#### Issue

The registered metadata group and marker restoration order are now explicit, but `INFO_TEXT` is not part of the
immutable lexical contract and is defined only as “ordinary info.” Its allowed characters, line-ending/EOF boundary,
and interaction with a final brace group are consequently not executable. The annotation rule also says a marker has an
“immediately following” definition after the fence without defining a contiguous definition suffix, intervening-line
behavior, or whether annotation text preserves or normalizes trailing and internal spaces.


#### Impact

Valid language-plus-metadata fences and annotated payloads can receive different AST fields or source spans. A canonical
fence may reparse its info consistently but still change annotation text or association on the second pass.


#### Suggestion

Add `INFO_TEXT` to the finite grammar with exact character and whitespace rules, and define the final metadata split
unambiguously. Define the annotation suffix as a complete production with its allowed line order, adjacency, EOF rule,
text-byte normalization, and canonical output order. Retain the already-correct rule that marker extraction precedes
delimiter selection and payload newline normalization.


#### Outcome


#### S06: Core reference lifecycle still contains contradictory output language


#### Where

AC07, the Core references row, the collection rules, and AC13, approximately lines 148–153, 323–340, and 377


#### Issue

AC07 says a reference definition “is emitted only when” it is validated, resolved, and discarded. The Core references
row,
the collection rules, and AC13 instead say every core definition, including unused definitions, is validated and
discarded
without retention or output. The first sentence still describes a canonical reference-definition production while
denying
that any such node is emitted.


#### Impact

An implementation plan can retain a transient definition node and serialize it, or resolve it and remove it, while both
appear to satisfy different parts of the design. Canonical output and the second-pass relationship lifecycle remain
ambiguous.


#### Suggestion

State one lifecycle: collect every legal core definition into a transient label registry; normalize and validate all
definitions, including unused ones; resolve all reference links and images in the second pass; store no core-definition
nodes in the normalized AST; and never emit core definitions. Remove the phrase that presents a core definition as an
emitted canonical production.


#### Outcome


#### S07: Definition-list grammar is not a complete recursive production


#### Where

The Definition list row, definition-list canonical-output paragraph, and block dispatch, approximately lines 301,
342–345, and 349–353


#### Issue

The plan now fixes the term opener, `: ` entry marker, exact four-space continuation intent, no-blank-gap rule,
grouping,
and broad precedence. It still does not define what a continuation line contains beyond indentation, whether the first
definition line is inline-only or recursively parsed, how nested block/profile constructs are represented, whether blank
lines with four spaces are valid, whether EOF terminates a definition, or where the source span ends under an active
container prefix. “Nonempty inline first line” conflicts with canonical output that recursively renders a definition.


#### Impact

Common definition-list edge cases can produce different grouping, nesting, or canonical indentation. A serializer can
also emit a recursively rendered block that the stated input grammar cannot read back as the same definition.


#### Suggestion

Specify a finite line production for a term, one or more definitions, continuation content, blank lines, EOF, and active
structural prefixes. State whether continuation content is inline-only or recursively parsed, the exact termination
point,
and precedence against every earlier block owner. Make the canonical production the inverse of that grammar.


#### Outcome


#### S08: Policy exclusions are not finite executable predicates


#### Where

AC04, AC09, and AC10, approximately lines 55–60 and 227–245


#### Issue

AC04 claims its policy-rejection list is complete, but “heading terminal punctuation” and a list item's “complete first
sentence” are not defined grammars. The plan does not identify the punctuation code points that trigger the heading
rejection or the sentence boundary and Unicode behavior used to decide whether a bold subject is the complete first
sentence. These are policy exclusions, not parser behavior, so the CommonMark/GFM coverage claim cannot make them
implicit.


#### Impact

Fixtures and implementations can disagree on valid baseline headings and list items without violating the words of the
plan. The resulting rejection set is not auditable as the promised complete list.


#### Suggestion

Enumerate the exact heading-terminal code points and define the finite sentence/subject predicate, including newline,
Unicode punctuation, escapes, and nested inline markup. Keep those predicates in AC04's explicit exclusion list and
cover their boundaries separately from parser-coverage fixtures.


#### Outcome


## Notes

Raw-HTML handling is materially improved and does not add a new finding: AC06 defines a body-only rejection boundary,
keeps code and frontmatter outside it, and gives valid autolinks and angle destinations precedence. AC15 and AC16 also
provide a credible optimistic per-file compare, atomic replacement, preflight, and partial-commit contract; the
remaining
round-trip findings are the main threat to that write path's correctness rather than a missing write-safety policy.

The three listed Unknowns remain legitimate questions. The corpus-migration inventory is the one that must be resolved
before the AC17 rollout gate can be evaluated. No tests, builds, or linters were run.
