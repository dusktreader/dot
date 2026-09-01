# Design Plan Review: Canonical AST-based Markdown formatter

**Iteration 10**

Iteration 10 re-reviews the plan against iteration 09, with emphasis on acceptance-criteria structure, finite profile
grammars, parser coverage, dispatch ownership, canonical bytes, fence annotations, idempotence, and write safety.


## Source Artifact

/Users/tucker.beck/src/dusktreader/dot/.artifacts/20260827--markdown-ast-formatter/design-plan.md


## Overview

The review surfaced findings:

- **Critical**:    1
- **Significant**: 6
- **Trivial**:     0


## Prior Review Resolution

- **C01** ✗: The extension profiles remain `####` siblings of AC12; the table serialization subsection is also detached
  from AC07.
- **C02** ⚠: Details closure and most block termination rules are clearer, and fence ownership is stated, but definition
  list productions, attribute attachment across block and inline domains, and exact metadata grammar remain ambiguous.
- **S01** ⚠: The plan adds a general claim predicate, but it still does not define per-extension opener predicates or
  reconcile unknown and malformed extension spellings with complete baseline coverage.
- **S02** ✓: Math delimiter identity and body preservation remain explicit.
- **S03** ⚠: Reference source forms and discard intent remain, but later criteria contradict the discard rule and do not
  provide one unambiguous lifecycle for definitions.
- **S04** ⚠: The plan now provides one named dispatch order, but block math, block-target attributes, and extension
  claim
  predicates are not fully represented by that order.
- **S05** ✓: Empty and absent fence info still normalize to AST `text`.


## Findings

### Summary

| Finding | Title                                                    | Outcome |
| ------- | -------------------------------------------------------- | ------- |
| C01     | Acceptance-criteria support is structurally detached     |         |
| S01     | Extension claims still conflict with baseline coverage   |         |
| S02     | Fence metadata and annotations lack a round-trip grammar |         |
| S03     | Core canonical bytes are not fully specified             |         |
| S04     | Dispatch omits block-level profile ownership             |         |
| S05     | Core reference-definition lifecycle is contradictory     |         |
| S06     | Definition-list grammar is still schematic               |         |


### Critical

#### C01: Acceptance-criteria support is structurally detached


#### Where

Acceptance Criteria — AC07, AC12, `Table serialization details`, `Block profile`, and `Inline and fence profile`,
approximately lines 258–301


#### Issue

`Table serialization details`, `Block profile`, and `Inline and fence profile` are all `####` headings at the same level
as the AC headings. The extension matrix is therefore not nested under AC12, and the table rules are not nested under
AC07. AC01 through AC17 are contiguous, but the supporting material is not structurally owned by the criteria it
defines.


#### Impact

The plan still violates the canonical design-plan structure. A consumer that extracts an AC section can omit the matrix
or associate its rules with the wrong criterion, leaving AC12 without its claimed executable contract.


#### Suggestion

Make `Block profile` and `Inline and fence profile` `#####` headings under AC12. Move `Table serialization details`
under AC07 and make it a `#####` heading. Keep AC01–AC17 as the only `#### AC##` headings.


#### Outcome


----

### Significant

#### S01: Extension claims still conflict with baseline coverage


#### Where

AC04 and AC08, plus the Emoji, Math, Mark/caret/tilde, and Zensical rows, approximately lines 44–64, 208–215, and
307–315


#### Issue

The plan says that no valid CommonMark or GFM form is rejected beyond the listed policy restrictions and raw HTML, and
that incomplete profile-looking punctuation remains ordinary text. It also says that malformed extensions, unknown
shortcodes, bad conditions, and unbalanced math fail. No per-extension complete opener predicate decides which rule
applies. Examples such as `costs $5`, `ratio: 3:1`, `:Name:`, `@if bad`, and `~text` can consequently be classified as
ordinary baseline text or failed extension input. “Any other shortcode spelling fails” is especially inconsistent with
the exhaustive baseline-rejection claim.


#### Impact

Two conforming implementations can reject different valid baseline documents, or accept malformed profile syntax. The
claimed CommonMark/GFM coverage and fail-closed behavior cannot both be implemented from this contract.


#### Suggestion

Define an explicit opener predicate, source span, and precedence for every extension delimiter. An unmatched delimiter
must remain ordinary text unless its complete opener predicate succeeds. If unknown or malformed spellings are intended
to fail, enumerate them as additional policy exclusions in AC04 and fixtures; otherwise remove those failure claims.


#### Outcome


#### S02: Fence metadata and annotations lack a round-trip grammar


#### Where

AC11 and the SuperFences metadata row, approximately lines 241–256 and 315


#### Issue

The notation `[INFO_TEXT] [METADATA]` does not define the registered brace group's exact source grammar: field
separators, assignment syntax, value quoting, optional-field rules, metadata-only input, or the precise treatment of
unknown fields. The plan also removes `^{N}` from a payload line and says only that its definition is emitted after the
fence. It never says that the marker is rendered back into the payload or gives another canonical representation for
the relationship.


#### Impact

Valid language-plus-metadata fences can receive different AST ownership and info bytes. A canonical fence with only the
definition has no marker to associate with it on the second parse, so annotation relationships and the idempotence claim
can fail. Payload trailing-space preservation is also ambiguous at the removal and reinsertion boundary.


#### Suggestion

Specify the complete registered metadata production and canonical byte order, including metadata-only input and every
field value. State the annotation AST fields and emit a canonical marker at the owning payload line, followed by its
definition in the specified order, or define a different self-contained representation. State whether extraction and
delimiter selection operate before or after marker restoration, with examples for combined metadata and annotated code.


#### Outcome


#### S03: Core canonical bytes are not fully specified


#### Where

AC07–AC08, approximately lines 148–215


#### Issue

Several core serializers still rely on prose rather than a complete byte production. “Literal label,” “escaped heading
text,” and the claim-predicate rule do not define the ordinary-text escape set, delimiter collision handling, or
adjacent
emphasis and strong-node rendering. “Every other entity-triggering character” is undefined. In addition, `\\` inside
inline code denotes two backslash bytes if it is literal; if it is notation for one byte, the plan does not say so. That
would make the stated hard-break and table-pipe outputs either incorrect or unverifiable.


#### Impact

Independent serializers can emit different Markdown for the same AST. Two backslashes before a line feed do not encode
the stated canonical hard break, and two backslashes before a table pipe do not provide the stated literal-cell escape.
The parser can therefore produce a different AST on the second pass.


#### Suggestion

Define exact productions for ordinary text, headings, labels, entities, and every core delimiter, including collision
and
adjacency rules. State byte counts explicitly: a hard break uses one ASCII backslash followed by LF, and a literal table
pipe uses one ASCII backslash followed by `|`. Add representative nested and adjacent inline examples.


#### Outcome


#### S04: Dispatch omits block-level profile ownership


#### Where

AC12 dispatch paragraphs and the Math and Attributes rows, approximately lines 301–342


#### Issue

The authoritative block dispatch does not include the block forms of Math (`$$` and `\[` through `\]`). Attributes
can target headings, paragraphs, list items, block quotes, tables, and extension blocks, but “attached attributes”
appears
only in the inline dispatch. The claim that every matrix owner appears once is therefore not true for the complete set
of block-level claims, and precedence for block math and block-target attribute attachment is absent.


#### Impact

An implementation can classify block math as ordinary CommonMark content and can attach a block attribute list at a
different phase or source boundary. This produces divergent ownership, source spans, and reparsing behavior despite the
single-dispatch requirement.


#### Suggestion

Add block math to the block dispatch with its exact opener, terminator, nesting, and precedence. Define one explicit
attribute-attachment phase that owns both block and inline targets, or place block-target attachment in the block
dispatch;
do not leave the same source class implied by another dispatch domain.


#### Outcome


#### S05: Core reference-definition lifecycle is contradictory


#### Where

AC07, the Core references row, AC12 collection rules, and AC13, approximately lines 150–152, 305, 317–320, and 351


#### Issue

AC07 permits a normalized AST to retain and emit reference definitions. The Core references row and AC12 instead say
that definitions are resolved to inline links or images and discarded. AC13 then says reference definitions remain in
the


#### Impact

The same unused or resolved definition can be discarded, emitted, or ordered differently by conforming implementations.
That changes canonical bytes and leaves the second-pass contract under-specified.


#### Suggestion

Choose one lifecycle and use it consistently. If all core definitions resolve and are discarded, remove the retention
and
post-body claims. If unused definitions are retained, define the retention predicate, AST ownership, canonical spelling,
and exact ordering separately from abbreviations and footnotes.


#### Outcome


#### S06: Definition-list grammar is still schematic


#### Where

The Definition list row and the definition-list canonical-output paragraph, approximately lines 283 and 323–325


#### Issue

The accepted production uses “a nonempty definition block,” “a continuation line,” and “all consecutive definition
lines” without defining the finite line grammar. The `or` clause does not establish whether the first definition is
same-line or next-line syntax, how multiple definitions are grouped, whether blank lines terminate a span, or whether
indentation means exactly four spaces or at least four. Precedence against an ordinary paragraph and indented code is
also
not stated.


#### Impact

The source span and owner of common definition-list edge cases are implementation choices. Canonical grouping and
reparsing can consequently differ while each implementation appears to follow the matrix.


#### Suggestion

Give the owner a finite production with exact line forms, opener predicate, recursion, termination, and dispatch
precedence. Define same-line, next-line, multiple-definition, blank-line, tab, and malformed cases explicitly, and use
one consistent rule for exact versus minimum indentation.


#### Outcome


----

## Notes

AC01–AC17 are contiguous, and the frontmatter envelope, raw-HTML boundary, write safety, preflight/commit behavior, and
optimistic concurrency limitation are explicit. AC13 and AC17 state the intended idempotence contract, but S02, S03, and
S05 leave concrete round-trip paths unresolved. No tests, builds, or linters were run.
