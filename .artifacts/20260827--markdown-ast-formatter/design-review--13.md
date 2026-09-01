# Design Plan Review: Canonical AST-based Markdown formatter

Iteration 13 re-reviews the design plan against iteration 12, limited to prior findings and the requested structural,
ownership, serialization, lifecycle, policy, idempotence, and write-safety checks.


## Source Artifact

/Users/tucker.beck/src/dusktreader/dot/.artifacts/20260827--markdown-ast-formatter/design-plan.md


## Overview

The review surfaced findings:

- **Critical**:    1
- **Significant**: 6
- **Trivial**:     0

The plan still is not ready for approval. The heading ownership defect remains, and the remaining significant gaps
affect
profile ownership, exact serialization, fence annotations, definition-list parsing, and policy predicates.


## Prior Review Resolution

- **C01** ✗: Supporting headings remain `####` siblings instead of `#####` content owned by AC07 or AC12.
- **S01** ⚠: Opener-versus-span ownership still conflicts with child validation, and Betterem overlaps core emphasis.
- **S02** ⚠: Math attributes have a separate-line rule, but the attributes row still says same-physical-line attachment.
- **S03** ⚠: Core escaping, delimiter collision, and entity-trigger rules remain non-executable.
- **S04** ✓: Betterem and smartsymbols now have selected canonical representations; the remaining extension-specific
  gaps
  are covered by the fence and definition-list findings below.
- **S05** ⚠: Fence metadata is more constrained, but payload-marker and final-group productions remain incomplete.
- **S06** ⚠: Definition-list continuation and termination rules still do not form a complete inverse grammar.
- **S07** ⚠: Policy predicates still do not fully define source provenance and inline-node terminal behavior.


## Findings

### Summary

| Finding | Title                                                     | Outcome |
| ------- | --------------------------------------------------------- | ------- |
| C01     | Acceptance-criteria support remains structurally detached |         |
| S01     | Profile ownership and dispatch are still ambiguous        |         |
| S02     | Block-math attribute placement is contradictory           |         |
| S03     | Core canonical bytes remain under-specified               |         |
| S04     | Fence metadata and annotation grammar remain incomplete   |         |
| S05     | Definition-list grammar is not a complete inverse         |         |
| S06     | Policy predicates still lose source and inline context    |         |


### Critical

#### C01: Acceptance-criteria support remains structurally detached


#### Where

Acceptance Criteria, `Table serialization details`, `Block profile`, and `Inline and fence profile`, approximately lines
185, 324, and 349.


#### Issue

The plan has exactly 17 `#### AC##` headings, but the supporting headings are also level four. `Table serialization
details` is not nested under AC07, and both profile headings are not nested under AC12.


#### Impact

A structural extractor can treat the supporting contracts as sibling criteria or omit them. AC07 and AC12 then do not
own the details required to interpret their acceptance claims.


#### Suggestion

Change only `Table serialization details`, `Block profile`, and `Inline and fence profile` to `#####` headings, keeping
them directly under AC07 or AC12. Ensure AC01 through AC17 are the only level-four headings matching `AC##`.


#### Outcome


----

### Significant

#### S01: Profile ownership and dispatch are still ambiguous


#### Where

AC04 and AC12 ownership rules, profile matrices, and final dispatch, approximately lines 60-64, 314-319, 328-334, 356,
and 395-407.


#### Issue

The general rule says a complete opener claims a span and later child or relationship failures are extension errors.
Several block rows instead say the owner claims only after the child sequence matches, otherwise falling back to
baseline
text. Betterem also claims `*` and `**`, which the dispatch separately assigns to core emphasis and strong. The dispatch
lists omit the core-reference prepass while naming attributes in both inline dispatch and a post-block attachment phase.


#### Impact

The same bytes can receive different owners or different failure outcomes. The formatter cannot guarantee complete
baseline coverage, one-owner dispatch, and fail-closed extension validation.


#### Suggestion

Define a finite header/opener predicate and claimed span for every owner, then apply child, terminator, and relationship
validation after ownership. Make Betterem and core emphasis ownership disjoint, and explicitly separate prepasses and
attachment phases from the block and inline claim lists.


#### Outcome


#### S02: Block-math attribute placement is contradictory


#### Where

AC12 Attributes and Math rows and the final block dispatch, approximately lines 356 and 395-403.


#### Issue

The Attributes row says an attribute follows every allowed target, including a math block, on the same physical source
line. The dispatch later says a block-target attribute is a separate immediately-following line, while the math closing
delimiter cannot carry attributes.


#### Impact

An implementation cannot determine whether a math attribute is legal on the closing line or on the following line, nor
which source span the attribute owns. Equivalent inputs can therefore parse differently and fail round-trip checks.


#### Suggestion

Separate inline same-line attachment from block attachment in the contract. For math, specify the exact closing line,
attribute line, active-prefix and LF rules, source-span endpoint, and canonical order as one unambiguous production.


#### Outcome


#### S03: Core canonical bytes remain under-specified


#### Where

AC07 and AC08 core serialization, approximately lines 154-182 and 194-244.


#### Issue

“Escaped as needed” has been improved but remains incomplete for link and image labels, nested or adjacent markup, and
delimiter runs. The delimiter rule still says to escape or choose atom boundaries deterministically without an
algorithm.
Entity output refers to an explicit claim character set that is not enumerated, and the source-versus-rendered decision
for every entity-triggering character remains implicit.


#### Impact

Independent serializers can emit different bytes or produce canonical output that reparses into different inline nodes.
The exact-byte and idempotence criteria remain untestable for these cases.


#### Suggestion

Specify context-specific label escaping, a deterministic delimiter-run collision algorithm, the complete entity-trigger
character table, and fixtures for nested and adjacent inline nodes whose canonical output must preserve the AST.


#### Outcome


#### S04: Fence metadata and annotation grammar remain incomplete


#### Where

AC11 and the SuperFences metadata row, approximately lines 278-308 and 363.


#### Issue

The final metadata group is identified by prose rather than a complete split production when ordinary brace groups and
metadata-looking groups coexist. More importantly, `payload marker` is never given an exact marker grammar, payload
position, end-of-line rule, or marker-number domain. Preservation of annotation text bytes and the exact suffix/payload
source spans is also not fully stated.


#### Impact

Valid language-plus-metadata fences and annotated payloads can produce different AST fields, marker associations, or
canonical bytes. Re-parsing canonical fences can then change annotations.


#### Suggestion

Define the complete info-string tokenization and final-group split, the exact payload marker production and number
domain, its placement and whitespace behavior, the contiguous suffix and EOF grammar, and byte normalization for both
annotation payloads and definitions.


#### Outcome


#### S05: Definition-list grammar is not a complete inverse


#### Where

AC12 Definition list row and canonical-output paragraph, approximately lines 331 and 385-391.


#### Issue

Continuation content is only “nonblank content” in the input grammar, while canonical output promises recursively
rendered
inline continuation lines. The plan does not define that inline production, escaped or active structural prefixes, the
precise termination rule against earlier block owners, or whether an unterminated final physical line is valid at EOF.


#### Impact

Implementations can disagree on grouping, continuation ASTs, source-span endpoints, and whether canonical definition
lists are accepted on the next parse.


#### Suggestion

Specify finite productions for the term, first-line and continuation inline content, blank lines, LF and EOF,
active-prefix
removal/restoration, and termination against every earlier block owner. Make canonical output the exact inverse of those
productions.


#### Outcome


#### S06: Policy predicates still lose source and inline context


#### Where

AC09 and AC10 policy predicates, approximately lines 247-273.


#### Issue

The heading rule refers to normalized rendered text while also requiring retained escape provenance, without defining
the
representation used by the predicate. The bold-subject sentence rule similarly delegates termination to an atom's
rendered terminal character without specifying the behavior of escaped punctuation, code, links, entities, math,
extensions, or soft and hard breaks.


#### Impact

Fixtures and implementations can disagree about policy rejection while both claim the complete exclusion list. Valid
baseline input can be rejected, or policy-forbidden content can be retained.


#### Suggestion

Define each predicate over source tokens or a specified normalized inline AST. Enumerate terminal-character behavior for
every inline node kind, entity decoding, source escapes, opaque spans, and newline boundaries, while preserving the
provenance required for heading decisions.


#### Outcome


## Notes

Core references now have a consistent lifecycle: collect, validate including unused definitions, resolve uses, discard,
and never emit. Footnote and abbreviation ordering is explicit. Raw HTML rejection, canonical idempotence intent, and
optimistic per-file and preflighted multi-file write safety are materially specified; their final guarantees remain
dependent on resolving the serialization and ownership findings.

No tests, builds, or linters were run.
