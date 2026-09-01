# Design Plan Review: Canonical AST-based Markdown formatter

**Iteration 01**


## Source Artifact

.artifacts/20260827--markdown-ast-formatter/design-plan.md


## Overview

The review surfaced findings:

- **Critical**:    3
- **Significant**: 7
- **Trivial**:     0


## Findings

### Summary

| Finding | Title                                                           | Outcome |
| ------- | --------------------------------------------------------------- | ------- |
| C01     | Unknowns section violates the canonical design-plan structure   |         |
| C02     | Parser choice does not provide strict validation semantics      |         |
| C03     | Current H1-exempt document corpus has no migration contract     |         |
| S01     | Frontmatter format and semantic preservation are underspecified |         |
| S02     | Canonical rendering is incomplete for declared node kinds       |         |
| S03     | Heading normalization conflicts with repository style           |         |
| S04     | The wrapper error contract is not defined                       |         |
| S05     | Code-fence normalization can violate byte preservation          |         |
| S06     | Table syntax and malformed-table boundaries are undefined       |         |
| S07     | Atomic in-place write semantics are incomplete                  |         |


### Critical

#### C01: Unknowns section violates the canonical design-plan structure


#### Where

Unknowns — lines 164–175


#### Issue

The section contains six flat bullet items. The canonical design-plan artifact permits a flat
list only for five or fewer short items; larger sections must use `###` subsections. The items
also mix independent policy decisions with corpus discovery, so they cannot be tracked as
distinct resolutions in their current shape.


#### Impact

This is a structural violation of the design-plan artifact contract. More importantly, the
output-affecting decisions can be answered or deferred inconsistently because the review has no
separate resolution target for each question.


#### Suggestion

Convert the six questions into named `###` subsections, or group them into no more than five
clearly scoped questions. Keep each question answerable and record the resulting decision in the
review process before implementation planning begins.


#### Outcome

Resolved. The Unknowns section now contains three short, explicit questions in a flat list, which conforms to the design-plan artifact structure.


----

#### C02: Parser choice does not provide the strict validation semantics


#### Where

Acceptance Criteria — AC03 and AC04, lines 38–49; Architecture — lines 119–134


#### Issue

`markdown-it-py` is a permissive CommonMark parser, not a general Markdown validator. Many
constructs that the plan calls malformed are represented as literal text or a valid fallback,
not parser errors. Footnotes and unknown extensions that are not enabled are likewise unlikely
to appear as unsupported AST nodes. Rejecting parser errors, forbidden node kinds, and
unclassified tokens therefore does not establish the fail-closed behavior promised by AC03 and
AC04.


#### Impact

Malformed links, unclosed constructs, malformed tables, and extension syntax can be accepted,
canonicalized, and written instead of producing a diagnostic. This directly violates the
source-preservation and unsupported-input requirements, and leaves the implementation plan
without a testable definition of invalid Markdown.


#### Suggestion

Define the supported grammar and the rejection boundary explicitly. Add a validation contract
for constructs that the parser accepts permissively, including unmatched fences and delimiters,
invalid nesting, malformed links, tables, footnotes, and extension syntax. Either specify an
explicit validation layer that rejects those cases or narrow the acceptance criteria to the
parser's actual semantics. Also state how extension-like text is distinguished from ordinary
literal text.


#### Outcome

Resolved. The plan makes the formatter-owned supported grammar and rejection boundary authoritative, and lists observable malformed, forbidden, and unsupported cases instead of relying on parser errors alone.


----

#### C03: Current H1-exempt document corpus has no migration contract


#### Where

Acceptance Criteria — AC02 and AC10, lines 31–36 and 94–99; Technical Notes — lines 190–192


#### Issue

AC02 requires every formatted body to begin with an H1. The current formatter deliberately
exempts frontmatter documents whose first body line is the agent instruction
`Read and follow the agent description in ~/.agents/agents/<name>.md.` The repository contains
multiple `.config/opencode/agents/*.md` files in exactly that shape. The Technical Notes say
such files must be corrected or excluded, but define neither a migration outcome nor an
exclusion mechanism for recursive directory formatting.


#### Impact

Adopting the new default against an existing recursive Markdown directory will reject current
OpenCode configuration documents that the existing invocation accepts. Either the repository's
configuration corpus must change, or directory formatting must gain a documented exclusion
policy. Without that decision, AC10 is not a deployable compatibility requirement.


#### Suggestion

Choose and state one policy: retain a narrowly defined, testable exception for the agent-wrapper
document class; migrate every current exception to an H1-bearing form and define the rollout
gate; or specify how excluded files are selected and reported. Add an AC that exercises the
current repository corpus through recursive formatting and states the expected result.


#### Outcome

Resolved. The old agent-description exception is removed, and the plan requires migrating every affected current agent document before recursive formatting, with a zero-rejection corpus gate.


----

### Significant

#### S01: Frontmatter format and semantic preservation are underspecified


#### Where

AC01 — lines 23–29; Architecture — lines 113–117 and 143–146; Unknowns — lines 166–167


#### Issue

The plan requires supported YAML, permitted roots and scalar values, and a canonical
representation that preserves meaning, but does not define any of those terms. It does not
specify the delimiter grammar, BOM and leading-blank handling, missing closing delimiter,
`---` versus `...`, empty documents, duplicate keys, aliases, tags, multi-document YAML, dates,
or the accepted root type. A line-based preamble boundary could also confuse a top-level
thematic break with an incomplete frontmatter block.


#### Impact

Implementations can accept different metadata, serialize the same data differently, or silently
change YAML values while claiming to preserve meaning. Existing agent frontmatter can therefore
be altered or rejected, and round-trip tests have no authoritative expected output.


#### Suggestion

Specify the frontmatter envelope and supported YAML model before implementation planning. Define
the accepted root and value types, duplicate-key and tag policy, multi-document behavior,
delimiter and BOM rules, deterministic serialization, and the semantic round-trip invariant.
Add acceptance examples for valid metadata, incomplete and ambiguous delimiters, and every
rejected YAML feature.


#### Outcome

Resolved. The plan defines the byte-0 `---` envelope, closing delimiter, safe YAML data model, rejected YAML features, deterministic serialization, and data-meaning preservation; only exact scalar-rendering details remain as a compatibility unknown.


----

#### S02: Canonical rendering is incomplete for declared node kinds


#### Where

AC05 — lines 53–58; Architecture — lines 120–123 and 148–152


#### Issue

The architecture declares links, images, emphasis, strong text, block quotes, thematic breaks,
and other nodes supported, but the ACs define canonical output only for headings, prose, lists,
code, and tables. There is no policy for inline escaping, link and image titles, reference
definitions, blockquote wrapping and nesting, nested blocks, indented code, or the canonical
form of thematic breaks. The phrase "where the parser can validate them" delegates scope to an
implementation detail.


#### Impact

Two implementations can both satisfy the written plan while emitting different bytes or
changing inline meaning. AC05's equivalent-input and idempotence claims are not testable for a
substantial part of the stated language.


#### Suggestion

Enumerate the supported node kinds and specify one canonical serialization policy for each,
including nested blocks and inline escaping. Mark every omitted construct explicitly unsupported
and reject it. Replace parser-dependent wording with observable input and output rules.


#### Outcome

Resolved. The plan enumerates supported block and inline kinds and defines canonical handling for escaping, links, images, block quotes, thematic breaks, nested structure, and rejected reference definitions.


----

#### S03: Heading normalization conflicts with repository style


#### Where

AC06 — lines 60–64; Architecture — lines 136–139 and 154–161; Unknowns — lines 166 and 170


#### Issue

AC02 checks only the first H1, while AC06 says the renderer emits one document H1 without
defining the behavior for a second H1. Skipped heading levels are left unresolved, and "no
unsupported heading depth" has no boundary. The repository style guide permits H5 and deeper
headings when the structure requires them, while the current Python formatter still rejects
them. The treatment of source thematic breaks is also left open even though it changes output.


#### Impact

An implementation may reject, demote, or shift valid headings and may produce a different
document hierarchy from the one the style guide permits. Duplicate titles, deep headings, and
source separators cannot be tested consistently, and canonical output remains dependent on
unresolved policy.


#### Suggestion

State whether the document has exactly one H1, what happens to later H1s, whether skipped levels
fail or shift, the maximum supported depth, and whether H5+ is valid under the current style
guide. Separately define when a source thematic break becomes the four-dash separator and add
ACs for each boundary.


#### Outcome

Resolved. The plan now requires exactly one H1 as the first AST entry, permits H1 through H6, rejects skipped heading levels, and distinguishes source thematic breaks from inserted four-dash hierarchy separators.


----

#### S04: The wrapper error contract is not defined


#### Where

AC09 — lines 84–89; AC10 — lines 94–99; Architecture — lines 143–146


#### Issue

AC09 requires a non-zero exit status, but the existing OpenCode wrapper catches a failed shell
command and returns a normal text result beginning with `Markdown {mode} failed:`. The plan calls
the wrapper a reporting boundary without specifying whether a failed tool invocation must be
raised, returned with an explicit status, or treated as successful output. It also does not define
how read, decode, permission, path-collection, or write errors are categorized and aggregated.


#### Impact

The underlying formatter can exit non-zero while OpenCode callers observe a successful tool
execution. Automation cannot reliably branch on failure, and frontmatter-versus-Markdown
diagnostic distinctions may disappear at the integration boundary.


#### Suggestion

Define separate process and OpenCode contracts. Require the wrapper to propagate failure through
the tool's failure mechanism, or return a structured result with an explicit failure status and
preserved diagnostics. Specify deterministic ordering and aggregation for collection, read,
validation, render, and write failures, then add integration ACs for those paths.


#### Outcome

Resolved. The plan defines the formatter's non-zero failure behavior, diagnostic preservation through the wrapper, deterministic aggregation, and the retained check operation's canonical-output comparison semantics.


----

#### S05: Code-fence normalization can violate byte preservation


#### Where

AC08 — lines 76–81; Architecture — lines 132–134 and 140–145


#### Issue

The plan normalizes fence delimiters and indentation while promising that code payloads remain
byte-preserving apart from newline policy. It does not select backticks or tildes as the
canonical delimiter, define collision-safe fence length, specify allowed info strings, or state
how indentation and final code newlines are handled. A payload containing the canonical fence
sequence is a direct collision case.


#### Impact

Valid code can be truncated, reinterpreted as Markdown, or changed during canonicalization.
Equivalent inputs can also fail idempotence when the renderer's chosen fence is not safe for the
payload.


#### Suggestion

Define the canonical delimiter and a rule that selects a delimiter longer than any conflicting
payload sequence. Specify indentation, language and info-string acceptance, and the exact newline
normalization allowed inside code. Add cases containing backticks, tildes, HTML-looking text,
trailing spaces, and unlabeled fences.


#### Outcome

Resolved. The plan selects collision-safe backtick fences, defines accepted info strings and language normalization, and limits code changes to the declared newline policy.


----

#### S06: Table syntax and malformed-table boundaries are undefined


#### Where

AC03 and AC08 — lines 38–41 and 76–81; Architecture — lines 119–127; Unknowns — lines 172–173


#### Issue

The plan does not lock which `markdown-it-py` rule set enables tables. "Malformed table
structure" may become a paragraph or a permissively parsed table depending on that configuration.
The rectangular normalization rule does not say whether missing or extra cells are errors or are
padded or discarded, and the plan leaves escaped pipes, code-span pipes, multiline cells, header
requirements, and alignment markers unresolved.


#### Impact

The formatter may repair input that AC03 requires it to reject, or may reject ordinary pipe
prose. Cell content and alignment intent can change without a testable semantic contract.


#### Suggestion

Define the supported table grammar independently of parser defaults. Specify header and separator
requirements, row-width behavior, empty cells, alignment markers, escaped and code-span pipes,
multiline or block content, and whether any repair is allowed. Add paired acceptance examples for
normalization and rejection.


#### Outcome

Resolved. The plan defines a strict header/separator table grammar, supported escaped and code-span pipes, alignment preservation, exact row widths, and rejection of malformed or multiline cells.


----

#### S07: Atomic in-place write semantics are incomplete


#### Where

AC09 — lines 84–89; Architecture — lines 143–146


#### Issue

The plan promises that a failed file remains intact and describes atomic writes, but does not
define behavior for an output write failure, file permissions, symlink destinations, concurrent
source changes, preserving metadata, or a later failure in a multi-file invocation. It is also
unclear whether successful files may be rewritten before another file in the same invocation
fails.


#### Impact

Implementers may choose a direct write, a replacement that changes a symlink, or a batch policy
that leaves surprising partial results. The promised fail-safe behavior cannot be verified at the
filesystem boundary.


#### Suggestion

State the per-file atomicity guarantee and the multi-file transaction policy. Define handling for
read-only files, symlinks, permissions, concurrent modifications, replacement failures, and
whether successful siblings are committed when another file fails. Add acceptance cases that
verify the original bytes and relevant metadata after each failure.


#### Outcome

Resolved. The plan defines per-file atomic replacement, preflight-before-commit behavior, symlink and permission policy, concurrent-change detection, and the multi-file partial-commit boundary.


## Notes

C02, S02, and S06 are coupled. The parser's permissive behavior and table rule configuration
must be resolved before the supported-language and rejection contracts can be made testable.

S01 requires a product-level decision about whether this repository's agent frontmatter is a
schema or merely arbitrary safe YAML. S03 requires the same kind of decision for heading repair
versus rejection; neither choice should be left to implementation planning.

C03 should be resolved against the actual recursive directory invocation, not only against a
newly migrated sample. The current agent-wrapper exception is an existing compatibility behavior,
not an incidental formatting defect.
