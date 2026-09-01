# Design Plan Review: Canonical AST-based Markdown formatter

Iteration 12 re-reviews the design plan against iteration 11, with emphasis on canonical structure, profile ownership,
complete dispatch, exact serialization, round trips, and write safety.


## Source Artifact

/Users/tucker.beck/src/dusktreader/dot/.artifacts/20260827--markdown-ast-formatter/design-plan.md


## Overview

The review surfaced findings:

- **Critical**:    1
- **Significant**: 7
- **Trivial**:     0

The plan is not ready for approval. The acceptance criteria are sequentially numbered, but the canonical nesting defect
and several exactness and ownership gaps remain.


## Prior Review Resolution

- **C01** ✗: AC07 table details and the AC12 profile matrices remain `####` siblings instead of `#####` content owned by
  their respective acceptance criteria.
- **S01** ⚠: The finite grammars and fallback language are more explicit, but `@if bad` is still baseline text in AC04
  and an invalid condition is an extension failure in AC12. Body validation is also still mixed into ownership.
- **S02** ⚠: The dispatch now names block math, attributes, and smartsymbols, but block-math body boundaries and the
  interaction between exact delimiter lines and block attributes remain incomplete.
- **S03** ⚠: Labels, paragraph adjacency, and delimiter collisions are acknowledged, but their exact canonical
  productions and the entity-triggering character set remain undefined.
- **S04** ⚠: Most extension openers and child indentation are stated, but Betterem and smartsymbols still lack complete
  canonical byte productions.
- **S05** ⚠: `INFO_TEXT` has character and whitespace rules, but metadata splitting and annotation marker/suffix
  boundaries remain incomplete.
- **S06** ✓: Core definitions now have one consistent lifecycle: collect, validate, resolve uses, discard, and never
  emit.
- **S07** ⚠: Definition-list terms, entries, grouping, and broad continuation intent are present, but continuation
  content, EOF and line-ending behavior, and active-prefix termination are not a complete inverse grammar.
- **S08** ⚠: Heading punctuation and sentence terminators are more concrete, but source escaping and nested or opaque
  inline content are not fully defined by the policy predicates.


## Findings

### Summary

| Finding | Title                                                               | Outcome |
| ------- | ------------------------------------------------------------------- | ------- |
| C01     | Acceptance-criteria support remains structurally detached           |         |
| S01     | Profile ownership still conflicts with complete baseline coverage   |         |
| S02     | Block-math attributes and dispatch boundaries remain incompatible   |         |
| S03     | Core canonical bytes remain under-specified                         |         |
| S04     | Extension rows still omit canonical byte productions                |         |
| S05     | Fence metadata and annotation boundaries remain incomplete          |         |
| S06     | Definition-list grammar is not a complete recursive inverse         |         |
| S07     | Policy predicates still lose source and inline-context distinctions |         |


### Critical

#### C01: Acceptance-criteria support remains structurally detached


#### Where

Acceptance Criteria, AC07 and AC12, approximately lines 180, 304, and 329.


#### Issue

`Table serialization details`, `Block profile`, and `Inline and fence profile` remain `####` headings. They are siblings
of the `#### AC##` headings rather than `#####` content owned by AC07 or AC12.


#### Impact

A canonical section extractor can omit the matrices or associate them with the wrong criterion. AC07 and AC12 then lack
the detailed contracts required for implementation planning and review.


#### Suggestion

Make `Table serialization details` a `#####` heading directly under AC07, before AC08. Make `Block profile` and `Inline
and fence profile` `#####` headings directly under AC12. Keep AC01 through AC17 as the only `#### AC##` headings in the
acceptance-criteria section.


#### Outcome


### Significant

#### S01: Profile ownership still conflicts with complete baseline coverage


#### Where

AC04, AC08, and AC12 profile predicates, approximately lines 60-65, 223-237, and 295-323.


#### Issue

The plan still does not separate a finite opener predicate from later body and relationship validation. AC04 explicitly
classifies `@if bad` as ordinary baseline text, but `bad` satisfies the AC05 `COND` production and AC12 therefore claims
the same line as a valid directive. Other malformed conditions are not given a consistent boundary between baseline text
and extension failure. The block rows likewise require a child sequence before ownership, while the general rule treats
an invalid child or empty branch as an extension error.


#### Impact

Two implementations can assign different owners and rejection outcomes to the same bytes. The formatter cannot
simultaneously guarantee complete CommonMark/GFM coverage, non-circular profile ownership, and fail-closed validation.


#### Suggestion

Define, for every owner, a finite header or opener predicate and the exact source span it claims. Only after ownership
is
established should child, terminator, or relationship validation produce an extension error. Apply the rule consistently
to malformed conditions, metadata, empty children, unknown kinds, and unclosed inline constructs, and remove conflicting
baseline examples from AC04 or list them as explicit policy exclusions.


#### Outcome


#### S02: Block-math attributes and dispatch boundaries remain incompatible


#### Where

AC12 Attributes and Math rows and the final block/inline dispatch, approximately lines 336-340 and 367-381.


#### Issue

The dispatch now includes the required owners, but it still has an incompatible attribute contract. Math blocks are
listed as attribute targets whose attributes must follow the target's final physical source line with no whitespace, yet
the math production requires the closing line to be exactly `$$` or `\]` followed by LF. An attribute on that line makes
it
cease to be a valid closing line. The block-math grammar also does not define whether blank body lines count as a
nonempty
body or whether an unterminated final physical line is legal.


#### Impact

An allowed target cannot receive the promised attributes, and implementations can disagree on valid block-math spans and
empty-body failures. That changes dispatch ownership and prevents reliable reparsing.


#### Suggestion

Either remove math blocks from the allowed block-attribute targets or define an explicit attribute placement production
and
include it in the math closing-line grammar. Also define body-line content, blank-body semantics, closing-at-EOF rules,
and the exact source endpoint used by the attachment phase.


#### Outcome


#### S03: Core canonical bytes remain under-specified


#### Where

AC07 and AC08 core serialization, approximately lines 141-177 and 199-237.


#### Issue

Several claims remain descriptions rather than executable productions. Link and image labels do not define
context-sensitive
escaping for brackets, backslashes, entities, or recursively rendered children. “Escaped as needed” does not define the
delimiter-collision algorithm for adjacent and nested emphasis, strong, and strike nodes. “Every other entity-triggering
character” has no defined character set or output decision. The paragraph rule also says one LF separates paragraph-like
siblings but then conditionally requires two LF bytes, without a complete separation predicate.


#### Impact

Independent serializers can emit different bytes for the same AST, and canonical output can reparse into a different
node
sequence. AC13 and AC17 cannot establish idempotence for the affected cases.


#### Suggestion

Specify context-specific productions for link and image labels, a deterministic delimiter-run collision algorithm, the
complete entity encoding table, and the exact paragraph-like sibling separator rule. Include nested and adjacent inline
fixtures and adjacent paragraph fixtures whose canonical output must remain separate on reparse.


#### Outcome


#### S04: Extension rows still omit canonical byte productions


#### Where

AC12 block and inline matrices and the extension serialization paragraphs, approximately lines 306-365.


#### Issue

The Betterem row lists accepted delimiters and boundary rules but does not choose one canonical delimiter spelling.
Smartsymbols maps source spellings to Unicode glyphs but does not say whether canonical output emits the glyph or one of
the
source spellings. Similar generic phrases such as “canonical recursive children” and “headers in source order” do not
define every emitted marker, spacing, and blank-line boundary.


#### Impact

Multiple serializers can preserve extension meaning while producing different source bytes. The exact-byte and
second-pass
claims therefore remain non-reproducible for supported extension nodes.


#### Suggestion

Give every extension owner an explicit canonical production. At minimum, state Betterem's selected delimiter,
smartsymbols'
canonical representation, and the exact opener, child, closing, blank-line, and source-span rules for every extension
row.


#### Outcome


#### S05: Fence metadata and annotation boundaries remain incomplete


#### Where

AC11 and the SuperFences metadata row, approximately lines 266-290 and 343.


#### Issue

`INFO_TEXT` now has character and whitespace constraints, but the final metadata split is still defined only by the
phrase
“final metadata group.” The plan does not give a finite rule distinguishing a malformed recognized group from ordinary
info text. Annotation definitions specify the suffix line shape, but not the payload marker production, marker
placement,
multiple markers on one line, or whether the suffix may terminate at EOF without LF. Annotation text normalization is
also
not fully stated beyond preserving remaining bytes.


#### Impact

Valid language-plus-metadata fences and annotated payloads can receive different AST fields, associations, or source
spans.
Canonical output can change annotation text or fail to reparse identically.


#### Suggestion

Define the complete info-string grammar and deterministic final-group split, including the malformed-group predicate.
Define
the annotation marker, its allowed payload position and multiplicity, the contiguous suffix and EOF production, exact
text
byte normalization, and canonical marker order.


#### Outcome


#### S06: Definition-list grammar is not a complete recursive inverse


#### Where

AC12 Definition list row and canonical-output paragraph, approximately lines 311 and 358-363.


#### Issue

The plan defines a term, `: ` entries, and four-space nonblank continuations, but “content” has no inline production or
termination rule. It is unclear whether inline hard breaks, escaped markers, or active structural prefixes are permitted
in
continuations. Term and entry lines require LF while “EOF ends it,” without stating whether an unterminated final line
is
valid. The canonical statement that definitions are recursively rendered is not demonstrably the inverse of the input
grammar.


#### Impact

Implementations can disagree on grouping, nesting, source-span endpoints, and whether their own canonical definition
lists are accepted on the next pass.


#### Suggestion

Specify a finite production for term, first-line inline content, continuation inline content, blank lines, EOF, active
prefix removal and restoration, and termination against every earlier block owner. Make the canonical production the
exact
inverse, including line endings and indentation.


#### Outcome


#### S07: Policy predicates still lose source and inline-context distinctions


#### Where

AC04, AC09, and AC10, approximately lines 55-60, 242-248, and 257-261.


#### Issue

The policy code points are more explicit, but “unescaped” heading punctuation is evaluated on rendered heading text
without saying whether source escape provenance is retained. The bold-subject sentence predicate does not define how
escaped punctuation, code spans, links, entities, nested markup, or soft and hard breaks contribute to sentence
termination. “Complete first sentence” remains dependent on an unstated source-versus-normalized representation.


#### Impact

Fixtures and implementations can disagree on policy rejection while both claim to implement the complete exclusion list.
This can reject valid baseline input or accept text that the repository policy forbids.


#### Suggestion

Define the predicates over either source tokens or a specified normalized inline AST. Enumerate which inline node kinds
contribute sentence terminators, how source escapes and entity decoding affect them, and how newlines and opaque spans
are
handled. Preserve enough source provenance to make heading escape decisions deterministic.


#### Outcome


## Notes

AC01 through AC17 are present and sequentially numbered. AC07's table details and AC12's profile matrices are the
remaining
canonical-structure defect. Core reference discard is now consistent. Raw-HTML rejection, canonical idempotence intent,
and
the optimistic per-file and multi-file write contracts are materially specified; no separate finding is raised for those
areas. The unresolved serialization and ownership findings still put the idempotence and rollout claims at risk.

No tests, builds, or linters were run.
