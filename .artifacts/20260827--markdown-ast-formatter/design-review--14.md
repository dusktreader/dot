# Design Plan Review: Canonical AST-based Markdown formatter

Iteration 14 re-reviews the design plan against iteration 13, limited to prior findings and the requested ownership,
serialization, grammar, policy, HTML, idempotence, and write-safety checks.


## Source Artifact

/Users/tucker.beck/src/dusktreader/dot/.artifacts/20260827--markdown-ast-formatter/design-plan.md


## Overview

The review surfaced findings:

- **Critical**:    1
- **Significant**: 5
- **Trivial**:     0

The plan is not ready for approval. The acceptance-criteria support headings remain structurally detached. Significant
gaps remain in exclusive profile ownership, exact core serialization, fence annotations, definition-list inversion, and
executable policy predicates.


## Prior Review Resolution

- **C01** ✗: Supporting headings remain level-four siblings instead of level-five content owned by AC07 or AC12.
- **S01** ⚠: The general opener rule is clearer, but Betterem still overlaps core emphasis and strong, and dispatch
  phases are not represented as one disjoint lifecycle.
- **S02** ✓: Block attributes now attach on a separate same-prefix line, and math closing delimiters cannot carry them.
- **S03** ⚠: The claim character set is more explicit, but delimiter collision, context-specific escaping, and entity
  provenance still do not determine exact core bytes.
- **S04** ✓: Betterem and smartsymbols have explicit canonical representations; the remaining extension serialization
  gaps are covered by the fence and definition-list findings below.
- **S05** ⚠: Fence metadata is more constrained, but final-group splitting and payload-marker productions remain
  incomplete.
- **S06** ⚠: Definition-list continuation and termination rules remain insufficiently defined to be an inverse grammar.
- **S07** ⚠: Heading and bold-subject predicates still do not define their source provenance and inline terminal
  behavior
  precisely enough to execute.


## Findings

### Summary

| Finding | Title                                             | Outcome |
| ------- | ------------------------------------------------- | ------- |
| C01     | Supporting material remains structurally detached |         |
| S01     | Profile ownership and dispatch still overlap      |         |
| S02     | Core canonical bytes remain under-specified       |         |
| S03     | Fence metadata grammar is not round-trip complete |         |
| S04     | Definition-list grammar is not a complete inverse |         |
| S05     | Policy predicates remain non-executable           |         |


### Critical

#### C01: Supporting material remains structurally detached


#### Where

Acceptance Criteria support headings, `Table serialization details`, `Block profile`, and `Inline and fence profile`,
approximately lines 187, 321, and 346.


#### Issue

The three supporting headings remain `####` headings. `Table serialization details` is not nested under AC07, and
`Block profile` and `Inline and fence profile` are not nested under AC12. AC01 through AC17 are the only level-four
headings matching the `AC##` pattern, but the supporting contracts are still level-four siblings rather than content
owned by their criteria.


#### Impact

A structural extractor can treat the supporting contracts as separate criteria or omit them. AC07 and AC12 then do not
structurally own the details required to interpret their acceptance claims.


#### Suggestion

Change only `Table serialization details`, `Block profile`, and `Inline and fence profile` to `#####` headings, keeping
them directly under AC07 or AC12. Keep AC01 through AC17 as the only `#### AC##` headings.


#### Outcome



----

### Significant

#### S01: Profile ownership and dispatch still overlap


#### Where

AC04 and AC12 ownership rules, the profile matrices, and final dispatch, approximately lines 60-64, 312-318, 321-360,
and 395-406.


#### Issue

The repeated opener rule now states the intended claim-then-validate lifecycle, but Betterem still accepts `*` and `**`,
which the same inline dispatch assigns to core emphasis and strong. The dispatch assertion that every owner appears once
is also false as written: core references are handled in a separate collection and resolution prepass, while attributes
appear both as inline dispatch and as post-block attachment. These phases are described, but they are not one explicit,
disjoint ownership lifecycle.


#### Impact

The same source can receive competing owners, or a required prepass or attachment can be omitted while still satisfying
the stated dispatch list. That defeats one-owner parsing and makes extension failure behavior dependent on ordering that
the plan does not define.


#### Suggestion

Define collection and resolution as explicit prepasses, make block and inline recognition disjoint from attachment, and
list those phases separately from owner dispatch. Make Betterem's predicate disjoint from core emphasis and strong, or
assign the overlapping spellings exclusively to one owner. Then enumerate each owner exactly once in its applicable
phase.


#### Outcome


#### S02: Core canonical bytes remain under-specified


#### Where

AC07 and AC08 core serialization, approximately lines 153-230.


#### Issue

The plan names deterministic escaping but does not specify the algorithm for adjacent and nested delimiter-run
collisions. Link and image label escaping is reduced to literal backslash and closing-bracket rules without defining all
context interactions, and entity output refers to claim predicates without an exhaustive context and provenance table.
The source-versus-decoded decision is therefore still implicit for several canonicalization cases.


#### Impact

Independent serializers can emit different bytes or produce output that reparses into different inline nodes. Exact-byte
and idempotence criteria remain untestable for nested, adjacent, escaped, and entity-containing inline content.


#### Suggestion

Specify context-specific label and ordinary-text escaping, a deterministic delimiter-run collision algorithm, and a
complete entity-trigger table that states source escape and decoded-character provenance. Include nested and adjacent
fixtures whose canonical bytes and reparsed AST are fixed.


#### Outcome


#### S03: Fence metadata grammar is not round-trip complete


#### Where

AC11 and the SuperFences metadata row, approximately lines 280-307 and 360.


#### Issue

The final metadata group is identified as a group that begins with selected keys, but the plan does not give a complete
split production for ordinary brace groups, metadata-looking groups, and the normalized info text. The payload marker
has
no exact token production, placement, whitespace, or number-domain rule. "Contiguous immediately after its payload line"
does not determine the marker's source span or the line-ending boundary.


#### Impact

Valid fences containing ordinary brace info, metadata, or inline payload markers can produce different info fields,
annotation associations, and payload bytes. Canonical output may therefore fail to reparse to the same fence AST.


#### Suggestion

Define the complete info-string tokenization and final-group split, the exact payload marker and positive-number
grammar,
its placement and whitespace rules, and the contiguous suffix and EOF productions. State the preserved and normalized
source spans for metadata, markers, annotation text, payload trailing spaces, and line endings.


#### Outcome


#### S04: Definition-list grammar is not a complete inverse


#### Where

AC12 definition-list row and canonical-output paragraph, approximately lines 328 and 385-391.


#### Issue

The grammar still refers to "inline content" without defining a finite first-line or continuation production. It does
not
fully distinguish a valid four-space inline continuation from a nested block or profile opener, define blank-line
behavior,
or settle whether an unterminated final physical line at EOF is valid. The termination rule also does not specify the
boundary against every earlier block owner or how canonical inline wrapping maps to continuation lines.


#### Impact

Implementations can disagree about grouping, continuation ASTs, source-span endpoints, and acceptance of canonical
output.
The claim that canonical output is exactly the inverse is not testable from the stated grammar.


#### Suggestion

Specify productions for the term, first-line and continuation inline content, active-prefix removal and restoration,
blank
lines, LF and EOF, continuation-vs-block classification, and termination against every earlier owner. Define canonical
wrapping as the exact inverse of those productions.


#### Outcome


#### S05: Policy predicates remain non-executable


#### Where

AC09 and AC10 policy predicates, approximately lines 251-275.


#### Issue

Heading policy combines normalized rendered text with retained escape provenance without specifying the predicate's
input
representation. The bold-subject rule delegates to an atom's rendered terminal character without defining terminal
behavior for escaped punctuation, code, links, images, entities, math, extension atoms, or soft and hard breaks. Newline
and opaque-span boundaries are also not enumerated.


#### Impact

Fixtures and implementations can disagree about policy rejection while both claim the same exclusion list. Valid
baseline
input can be rejected, or policy-forbidden content can be retained.


#### Suggestion

Define each predicate over a specified source-token or normalized-inline-AST representation. Give every inline node kind
an
explicit terminal-character and boundary rule, including entity decoding, source escapes, opaque spans, and soft and
hard
breaks, while retaining the provenance needed for heading decisions.


#### Outcome


## Notes

The block-math attribute rule is now unambiguous: the closing delimiter carries no attribute, and a block attribute is a
separate immediately following same-prefix line. Raw HTML rejection, canonical idempotence intent, and optimistic
per-file and preflighted multi-file write safety remain sound as stated. Their final guarantees still depend on
resolving
the ownership and serialization findings.

No tests, builds, or linters were run.
