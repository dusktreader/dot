# Design Plan: Canonical AST-based Markdown formatter

Replace line-oriented Markdown formatting with a fail-closed parser, a formatter-owned semantic AST, and deterministic
serialization for two explicitly selected source profiles. Frontmatter remains independent of Markdown. The default
profile is GFM; Zensical requires `--zensical` so existing recursive formatting can migrate explicitly.


## Goal

The formatter accepts either `--gfm` or `--zensical`. Both profiles use CommonMark 0.31.2 as their base, apply the
shared repository style policy, reject raw HTML in the Markdown body, and emit the same shared canonical layout rules.
Each profile then adds only its own finite, pinned source dialect. Profile-specific syntax has one owner and one
canonical source spelling; it is never accepted because it happens to be understood by the other profile.

The formatter selects GFM when no profile is supplied. Zensical requires `--zensical`. The command-line interface and
the
OpenCode wrapper expose the same profile choice. Invalid profile values fail before any file is changed. Generated HTML,
CSS, JavaScript,
theme behavior, directive evaluation, shortcode lookup, and build behavior are outside the contract.


## Acceptance criteria

### Input validation

#### AC01: Frontmatter has an unambiguous envelope

Frontmatter is recognized only when byte 0 begins an exact `---` line. No BOM, leading blank, whitespace, or other byte
is accepted before it. The closing delimiter is a separate exact `---` line; `...` does not close the envelope. A
missing closing delimiter is an error. The body begins after the closing line ending.


#### AC02: Frontmatter preserves safe data meaning

The YAML document has a mapping root with string keys. Values are nested mappings, sequences, or null, Boolean, finite
integer, finite real, or string scalars. Duplicate keys, aliases, tags, binary, timestamps, sets, multi-document YAML,
invalid YAML, and all other values outside this model fail. Serialization sorts mapping keys lexically, uses
deterministic
indentation and LF line endings, and emits strings with deterministic double-quoted escaping. Frontmatter strings are
not Markdown and are not subject to the raw-HTML rule.


#### AC03: The first body AST entry is H1

The body contains exactly one H1, and it is the first AST entry. A later H1, missing H1, leading non-H1 block, or H1
nested in another construct fails. There is no agent-description exception. Existing affected agent documents are
migrated before recursive formatting is enabled, and the migrated supported corpus formats successfully.


#### AC04: Profile selection is explicit and deterministic

`--gfm` selects the GFM profile and `--zensical` selects the Zensical profile. The flags are mutually exclusive. An
omitted profile selects GFM. A repeated flag or any invalid profile value fails with a diagnostic naming the requested
value and the valid choices, before parsing or writing files. The selected profile is part of the formatting context.
Omission selects GFM for both `format` and `check`; a Zensical output requires `--zensical` when it is checked.


#### AC05: Each profile accepts only its governed source dialect

Both profiles use complete CommonMark 0.31.2 parser coverage as their syntax baseline. The explicit formatter policy
exclusions are raw HTML, thematic-break source constructs, and the shared repository policy rejections. No other valid
baseline form is excluded. Shared task-list syntax means `[ ]`, `[x]`, and `[X]` immediately after a list marker and one
space in either profile; `[ ]` and `[x]` are canonical. Shared tables and references also have one meaning in both
profiles.
GFM additionally accepts the complete formal GFM source dialect. Zensical accepts only the selected, pinned
Zensical/PyMdown source forms in the Zensical matrix below. Neither profile is a broad superset.

Every selected-profile construct has one explicit claim predicate and one successful production. It claims source only
when the full predicate matches, including required delimiters or first tokens and any required body or terminator. If
the predicate does not match, ordinary CommonMark parsing wins. Under `--gfm`, the unsupported Zensical claim predicate
is exactly a complete Zensical block or inline production listed in the Zensical matrix: a full valid admonition/details
block with required children, full tabs with required children, a full valid Zensical directive/branch group, or a full
valid `==...==`, `^^...^^`, `^...^`, `~...~`, keys, attributes, shortcodes, math, snippet, or SuperFences profile
construct. Under `--zensical`, the unsupported GFM claim predicate is exactly: (a) a valid GFM strikethrough span with
`~~` opener, body, and closer; (b) a bare GFM extended autolink recognized by the pinned linkify tokenizer as a
complete scheme, `www`, email, or fuzzy-IP literal; or (c) a complete production owned by a GFM grammar listed in this
plan and explicitly absent from the accepted rows of the Zensical matrix. Shared tables, references, and task lists are
not in this set. A complete construct matching the unselected profile's listed predicate fails with a profile-specific
unsupported-syntax diagnostic. Malformed or incomplete candidates fall back to baseline CommonMark text; unknown
extension-like text remains baseline text. Raw HTML always fails.

For GFM tables, the claim predicate is a header line immediately followed by a valid delimiter row. If no valid
delimiter follows, the source remains a paragraph. A malformed row after a claimed table uses the existing GFM row and
error rules. Shared tables use this exact rule in both profiles.


#### AC06: Raw HTML is forbidden in both profiles

CommonMark HTML block and inline-tag productions, comments, declarations, processing instructions, and CDATA in the
body fail in either profile. Valid angle-bracket autolinks and angle-bracket link destinations are classified first and
accepted. Escaped `<`, entities, ordinary comparisons, fenced code, indented code, and frontmatter strings are accepted.
Malformed tag-like text fails only when it enters a CommonMark HTML production. The decision examines source outside
code only.


### Canonical output

#### AC07: Canonical document structure is deterministic

The AST represents documents, H1-H6 headings, paragraphs, lists and items, block quotes, fenced code, tables,
references,
links, images, a formatter-generated `HeadingSeparator` layout node, and the selected profile's nodes with recursive
block and inline content. Output uses
LF, canonical blank lines, deterministic indentation, exactly one final newline, and no trailing whitespace on
structural or prose lines. Code payload lines retain trailing spaces. Nested blocks retain structure.

Sibling blocks use one blank line, with no blank line immediately inside a container. Lists use `- ` for unordered items
and decimal `N. ` markers for ordered items, preserving the first start number. Continuation blocks are indented four
spaces relative to the marker. Block quotes prefix every rendered line with `> `. Extension blocks retain their exact
four-space child indentation. Canonical output reparses to the same normalized AST.

Every table output uses aligned columns for human readability so a human can visually scan each column: every row
separator and cell content lines up. Tables always render a leading and trailing pipe with exactly one ASCII space
inside each pipe. For each cell, the renderer emits its canonical inline content, strips only surrounding ordinary
spaces, and measures Unicode code-point width. It pads every non-separator cell in each column to that column's maximum
rendered content width. Separator cells preserve their alignment markers and contain enough dashes to fill the same
column width, with a minimum of three dashes plus the marker characters. The same algorithm applies to shared tables
under both `--gfm` and `--zensical`, including GFM ragged-row normalization. Code-span pipes remain untouched, and
literal pipes use the settled backslash-parity codec. Short body rows gain empty cells, excess cells are discarded
according to the owning profile's rectangular-table contract, and malformed or block-content cells fail.

Headings, links, images, destinations, titles, labels, code spans, entities, hard breaks, inline delimiters, and layout
nodes follow the settled canonical rules: headings use one space and escaped text; `HeadingSeparator` emits exactly
`---` followed by LF, with one blank line before it after the preceding block's normal ending and one blank line after
it
before the lower-level heading; empty destinations use `<>`; labels escape literal backslash, `[` and `]`; and hard
breaks use backslash plus LF. Core emphasis owns `*`, `_`, `**`, `__`,
and GFM `~~`; profile nodes own
only their profile-specific delimiters. The finite delimiter codec protects literal delimiter bytes at opening,
closing, and sibling boundaries, preserves semantic backslashes, and rejects an unrepresentable AST rather than
changing its meaning.


#### AC08: Inline rendering uses an executable lexical algorithm

Inline AST nodes are maximal atoms. Source whitespace and soft breaks become one boundary space; leading and trailing
boundaries are discarded. Lines wrap at 120 Unicode code points excluding structural indentation, while an atom longer
than 120 remains whole. Tabs count one in prose and become four spaces in structural indentation. No rendered non-code
line has trailing whitespace.

Code spans, entities, destinations, titles, attributes, emphasis, strong, strike, profile spans, and math use the
settled finite codecs and claim predicates. Source spelling metadata such as alternate math or emphasis delimiters is
excluded from normalized-AST equality. Canonical output is reparsed and must produce identical semantic nodes,
relationships, and bytes.


#### AC09: Headings and hierarchy follow fixed policy

ATX headings render as `#` through `######`, one space, and escaped heading text. A level may increase only one from
the preceding heading; skipped levels fail. Heading terminal punctuation is evaluated over the final semantic character
of the last content-bearing inline node and rejects unescaped `.`, `:`, `;`, `!`, or `?`. Strong markup in a heading is
always a policy error. The AST contains headings and formatter-generated `HeadingSeparator` layout nodes, not
thematic-break nodes. For each heading after the first, the formatter compares its level with the immediately preceding
heading level in document heading order. If the current level is lower, it inserts exactly one `HeadingSeparator` after
the preceding block's normal ending, with one blank line before the separator and one blank line after it before the
lower-level heading; if the level is equal or higher, it inserts none. No separator is inserted before the first H1. A
source line consisting of `---`, `***`, or `___` is not accepted as a semantic Markdown block. Outside a required
downward heading transition, it is rejected as unsupported source syntax; in that position, it is consumed as the
separator layout node regardless of spelling and canonicalized to exactly `---` plus LF. The
parser recognizes a separator lexically only in that required position, so canonical output reparses the line as a
positional layout node and is idempotent. The formatter does not infer author intent.


#### AC10: Prose, breaks, and lists follow fixed policies

All legal CommonMark list indentation and marker spacing, ordered starts, two-space hard breaks, and backslash hard
breaks are accepted and canonicalized. Item order, nesting, and task state are preserved. A list item's bold subject is
valid only when it is the complete first sentence, optionally followed by `: ` and remaining inline nodes, and the full
canonical item is at most 120 code points. Otherwise the input fails as a style-policy error rather than being
restructured.


#### AC11: Code is literal and collision-safe

Fenced and indented code render as unindented fenced blocks. Info text is LF-free, trimmed at the edges, and has
internal ASCII whitespace collapsed. The selected SuperFences metadata and annotation subset is normalized only when
its complete grammar matches. Fence selection, payload bytes, annotation placement, metadata, language normalization,
and structural newlines follow the settled canonical rules. Unknown info tokens remain ordinary info text. Code payload
is never parsed as Markdown and raw HTML inside code is accepted.


#### AC12: Each profile has executable syntax ownership

The matrices below are complete. Every accepted row has one owner, explicit semantic fields, and one canonical spelling.
Reference collection and resolution are a prepass; block attributes are a post-block attachment phase. Profile
recognizers run only for the selected profile. Core CommonMark owns baseline delimiter runs and HTML classification;
profile owners cannot compete with it. Each row below defines its claim predicate and successful production. A complete
selected-profile claim reserves its source before fallback; invalid children or relationships then fail. An incomplete
claim is baseline text. Unknown extension-like text is baseline text unless it matches the explicit unsupported claim
predicate of the other profile. Generic `///` is not part of the Zensical profile. Every shared source spelling is
claimed once in the shared phase before profile-specific dispatch; unselected profile recognizers are unavailable. Every
source span has exactly one owner.

The GFM owners are the core CommonMark adapter for the base row, the shared table and task-list adapters, the GFM
strike and autolink adapters, the reference prepass, and the raw-HTML rejection. The Zensical owner is the core shared
adapter for its CommonMark base row, shared task/table adapters for shared rows, and the formatter-owned Zensical
recognizer named by each remaining accepted row: admonitions/details, tabs, footnotes, definition lists, abbreviations,
attributes, shortcodes, math, keys, mark/caret/tilde, Betterem/smartsymbols, SuperFences, snippets, and directives.
The selected-profile gate owns unsupported claims; unselected recognizers are unavailable.


#### GFM profile

| Area                     | Owner                    | Accepted source and semantic contract                                                                                                                                                                                                                                                                                                            | Canonical rendering                                                                                                                                                   |
| ------------------------ | ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CommonMark base          | Core CommonMark adapter  | Complete CommonMark blocks and inlines, including headings, setext headings, paragraphs, quotes, lists, ordered starts, fenced and indented code, escapes, entities, emphasis, strong, links, images, and hard breaks. Thematic-break source constructs are excluded by formatter policy; required separator spellings are handled positionally. | Shared serializer rules in AC07-AC11, including `HeadingSeparator`.                                                                                                   |
| Shared task-list adapter | Shared task-list adapter | Markers immediately after a list marker and one space: `[ ]`, `[x]`, and `[X]`.                                                                                                                                                                                                                                                                  | `[ ]` or `[x]`, retaining state.                                                                                                                                      |
| Shared table adapter     | Shared table adapter     | A claim is a header line immediately followed by a valid GFM delimiter row. If no valid delimiter follows, the source is a paragraph. Ragged rows normalize; malformed rows after a claimed table use existing GFM row/error rules.                                                                                                              | The AC07 aligned-column algorithm: canonical inline cells, one ASCII space inside leading/trailing pipes, Unicode code-point widths, and preserved alignment markers. |
| Strikethrough            | GFM strike adapter       | Complete GFM `~~` spans, with core delimiter precedence and nesting rules.                                                                                                                                                                                                                                                                       | Canonical `~~` using the finite delimiter codec.                                                                                                                      |
| Autolinks                | GFM autolink adapter     | CommonMark angle autolinks plus formal GFM extended autolinks: bare scheme URLs, `www.` URLs, email addresses, and pinned fuzzy IP forms.                                                                                                                                                                                                        | Angle autolinks preserving the target.                                                                                                                                |
| Reference prepass        | Reference prepass        | All legal reference definitions and uses, including unused definitions.                                                                                                                                                                                                                                                                          | Resolve and validate definitions, then discard them.                                                                                                                  |
| Raw HTML                 | Raw-HTML rejection       | No HTML block or inline production.                                                                                                                                                                                                                                                                                                              | Rejected before serialization.                                                                                                                                        |


#### Zensical profile

| Area                                       | Owner                                     | Accepted source and semantic contract                                                                                                                                                                                                                                                                                                                                                                                                                                                          | Canonical rendering                                                                                                                                                 |
| ------------------------------------------ | ----------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CommonMark base                            | Core shared adapter                       | Complete CommonMark blocks and inlines, excluding raw HTML, thematic-break source constructs, and constructs owned by dedicated shared rows. Required separator spellings are handled positionally.                                                                                                                                                                                                                                                                                            | Shared serializer rules in AC07-AC11, including `HeadingSeparator`.                                                                                                 |
| Shared task-list adapter                   | Shared task-list adapter                  | Markers immediately after a list marker and one space: `[ ]`, `[x]`, and `[X]`.                                                                                                                                                                                                                                                                                                                                                                                                                | `[ ]` or `[x]`, retaining state.                                                                                                                                    |
| Shared table adapter                       | Shared table adapter                      | A claim is a header line immediately followed by a valid GFM delimiter row. If no valid delimiter follows, the source is a paragraph. Ragged rows normalize; malformed rows after a claimed table use existing GFM row/error rules.                                                                                                                                                                                                                                                            | The same AC07 aligned-column algorithm as GFM, including one ASCII space inside leading/trailing pipes, Unicode code-point widths, and preserved alignment markers. |
| Reference prepass                          | Reference prepass                         | All legal reference definitions and uses, including unused definitions.                                                                                                                                                                                                                                                                                                                                                                                                                        | Resolve and validate definitions, then discard them.                                                                                                                |
| Admonitions and details                    | Zensical admonition/details recognizer    | Selected `!!!` admonitions and `???`/`???+` details with the pinned kind set, optional quoted title, and nonempty four-space child blocks.                                                                                                                                                                                                                                                                                                                                                     | Exact canonical marker, kind, title, LF, and four-space children.                                                                                                   |
| Tabs                                       | Zensical tabs recognizer                  | Consecutive `=== "title"` headers with nonempty four-space child blocks, preserving order and labels.                                                                                                                                                                                                                                                                                                                                                                                          | Source-order headers with exact four-space children.                                                                                                                |
| Footnotes                                  | Zensical footnotes recognizer             | `[^ID]:` definitions, repeated uses, exact four-space continuations, and first-reference then unreferenced source ordering.                                                                                                                                                                                                                                                                                                                                                                    | Definitions after the body; no generated backlinks.                                                                                                                 |
| Definition lists                           | Zensical definition-list recognizer       | `TERM` followed immediately by one or more `: ` entries and optional four-space inline continuations.                                                                                                                                                                                                                                                                                                                                                                                          | No blank gaps; exact term, entry, and continuation structure.                                                                                                       |
| Abbreviations                              | Zensical abbreviation recognizer          | `*[TERM]: "value"` declarations and boundary-aware case-sensitive uses in ordinary text only.                                                                                                                                                                                                                                                                                                                                                                                                  | Body text plus declarations in source order; no HTML expansion.                                                                                                     |
| Constrained attributes                     | Zensical attribute recognizer             | Immediate inline or block attributes with `#ID`, `.class`, and quoted key values using the fixed key grammar.                                                                                                                                                                                                                                                                                                                                                                                  | ID first, classes in source order, keys lexically, one ASCII space between entries.                                                                                 |
| Emoji and icon shortcodes                  | Zensical shortcode recognizer             | Lowercase ASCII `:name:` forms with `[a-z0-9_+-]+`; names are preserved without catalog lookup.                                                                                                                                                                                                                                                                                                                                                                                                | The exact shortcode bytes.                                                                                                                                          |
| Math and Arithmatex                        | Zensical math recognizer                  | Inline `$...$` and `\(...\)`, and block `$$` or `\[`/`\]`, with nonempty LF-free inline bodies, at least one nonblank block line, no nesting, and the fixed backslash/dollar codec.                                                                                                                                                                                                                                                                                                            | Inline `$body$`; block `$$` delimiters; semantic body preserved.                                                                                                    |
| Keys                                       | Zensical keys recognizer                  | `++KEY(+KEY)++` with one or more fixed-grammar key names.                                                                                                                                                                                                                                                                                                                                                                                                                                      | Exact key order and canonical delimiters.                                                                                                                           |
| Mark, caret, and tilde                     | Zensical mark/caret/tilde recognizer      | `==body==`, `^^body^^`, `^body^`, and `~body~`; `~~` is not accepted as a Zensical form.                                                                                                                                                                                                                                                                                                                                                                                                       | The corresponding canonical delimiter with collision-safe encoding.                                                                                                 |
| Betterem and smartsymbols                  | Zensical Betterem/smartsymbols recognizer | Betterem affects core emphasis parsing only. Smartsymbols recognizes only `--`, `---`, `(c)`, `(r)`, `(tm)`, and `...`.                                                                                                                                                                                                                                                                                                                                                                        | Core emphasis is canonicalized normally; recognized symbols become `–`, `—`, `©`, `®`, `™`, and `…`.                                                                |
| SuperFences subset                         | Zensical SuperFences recognizer           | Fenced code info metadata and line-end `^{N}` annotations only, with the fixed metadata, ordering, and scope rules.                                                                                                                                                                                                                                                                                                                                                                            | Canonical fence metadata and annotations attached to the same fence.                                                                                                |
| Snippets                                   | Zensical snippets recognizer              | Complete `--8<-- "PATH"` directives are opaque and non-expanding; `PATH` uses the fixed safe grammar.                                                                                                                                                                                                                                                                                                                                                                                          | The same canonical quoted directive.                                                                                                                                |
| Zensical directives                        | Zensical directive recognizer             | Complete `@if`, `@elif`, `@else`, `@use`, and `@var{ID}` forms with fixed condition, quote, ID, order, and child rules. They are opaque and non-evaluated.                                                                                                                                                                                                                                                                                                                                     | Canonical directive spelling, condition spacing, and four-space children.                                                                                           |
| GFM-only extensions and unknown extensions | Selected-profile gate                     | Under `--zensical`, the unsupported claim is exactly a valid GFM `~~` span, a bare extended autolink that the pinned linkify tokenizer recognizes as a complete scheme/`www`/email/fuzzy-IP literal, or a complete production owned by a GFM grammar listed in this plan and explicitly absent from the accepted rows of the Zensical matrix. Shared task lists, tables, and references are excluded. Malformed or incomplete candidates and unknown extension-like text remain baseline text. | Matching complete forms fail with a profile-specific unsupported-syntax diagnostic; ordinary text remains baseline text.                                            |
| Raw HTML and HTML-required layouts         | Raw-HTML rejection                        | Raw HTML, grids, cards, buttons, and other HTML-dependent layout forms are rejected.                                                                                                                                                                                                                                                                                                                                                                                                           | No HTML output or fallback layout.                                                                                                                                  |

Shared syntax has one meaning in both profiles: CommonMark headings, lists, links, images, references, code, entities,
emphasis, strong, angle autolinks, hard breaks, task lists, and tables use the same AST and serializer. A profile-only
owner cannot claim a
shared source spelling differently. The same source therefore has one meaning within each profile, while a construct
that is profile-only is either accepted by its owner or rejected by the other profile according to the contract above.


#### AC13: Extension meaning survives canonical rendering

For the selected profile, nesting, relationships, attributes, shortcode text, math bodies, inline styling, task state,
tables, references, annotations, metadata, opaque directives, heading-transition `HeadingSeparator` nodes and their
canonical spacing, and all profile-specific semantic fields survive AST normalization and canonical rendering. Core
references are validated, resolved, and discarded. Generated backlinks,
HTML, theme expansion, glyph resolution, condition evaluation, and build validation are not rendered or promised.
Re-parsing canonical output produces identical normalized node kinds, fields, relationships, and bytes.


#### AC14: Failures are observable and safe

The formatter exits zero only when every requested file succeeds. Decode, collection, read, parse, profile validation,
raw-HTML rejection, render, and write failures produce deterministic diagnostics containing file, category, selected
profile, and best source location. Profile errors name the rejected profile and the offending source span. A file is not
replaced unless frontmatter, AST, validation, and rendering all succeed. Multi-file preflight failure writes no file.


#### AC15: In-place writes use optimistic per-file replacement

The formatter snapshots bytes, identity, metadata, and destination type, then compares them immediately before atomic
replacement. Changed content or identity, a type change, symlink, non-regular destination, or read-only destination is
rejected. Replacement preserves the existing permission mode. Earlier committed siblings may remain committed after a
later commit failure; the changed file is never corrupted.


#### AC16: Check and wrapper behavior are explicit

`check` compares each file with canonical output for the selected profile and uses no second policy. Omission selects
GFM;
a Zensical output requires `--zensical` to check. The OpenCode wrapper accepts an explicit profile argument, defaults it
to GFM when omitted for either mode, passes it unchanged to the formatter, and reports the formatter's
profile diagnostics and failure status. It accepts files and recursive directories, resolves relative paths from the
session directory, reports formatted and unchanged files, and preserves deterministic ordering.


#### AC17: Compatibility and corpus verification are source-only

Current recursive/default formatting uses GFM and succeeds for the migrated supported corpus. Before recursive
formatting
is enabled, migrate every document affected by H1 policy or the source grammar. Fixtures cover both profiles,
all matrix rows, equivalent shared source variants, cross-profile rejection, profile selection and defaults, raw HTML,
references, nesting, tables, task states including `[X]`, metadata, annotations, opaque non-expansion, non-evaluation,
policy rejection, semantic preservation, idempotence, wrapper propagation, concurrent changes, atomicity, and unchanged
files. Downward heading transitions produce the exact `---` separator with one blank line on each side, source separator
spellings are consumed only in those positions and rejected elsewhere, and thematic-break source constructs remain an
explicit policy exclusion. The rollout gate is zero rejected supported files and a second pass with identical bytes.


## Architecture

The pipeline reads bytes, recognizes the optional byte-0 YAML envelope, validates and serializes safe YAML, normalizes
body line endings to LF, selects one profile, classifies raw HTML, and parses the body into a formatter-owned AST with
source spans. Frontmatter never enters Markdown parsing.

Both profiles share a CommonMark-capable core parser configuration with HTML disabled. The exact runtime GFM
configuration is `markdown-it-py` preset `gfm-like2` with `html: false`, `linkify: true`, `breaks: false`, and
`typographer: false`; GFM table, task-list, strike, and extended-autolink adapters are enabled, with
`linkify-it-py` options `fuzzy_link=true`, `fuzzy_email=true`, and `fuzzy_ip=true`. The exact Zensical core options are
`html: false`, `linkify: false`, `breaks: false`, and `typographer: false`. Formatter-owned recognizers model the
selected Zensical forms; unselected recognizers are unavailable.

Authoritative dispatch is this sequence:

1. Validate the CLI profile and set the profile gate.
2. Parse and validate frontmatter.
3. Collect and validate shared reference definitions.
4. Classify and reject raw HTML outside code.
5. Recognize shared CommonMark blocks plus shared tables and task lists, while recognizing separator spellings only at
   required downward heading transitions and rejecting them elsewhere.
6. Attach block attributes.
7. Recognize profile-specific blocks.
8. Recognize inline nodes in order: code, links/images/autolinks, math, keys, inline attributes, selected profile spans,
   footnote/abbreviation uses, core emphasis/strong/strike, smartsymbols, ordinary text.
9. Normalize style, heading-transition `HeadingSeparator` layout nodes, and relationships.
10. Render canonical Markdown, placing each downward-transition separator after the preceding block's normal ending
    with one blank line on each side, and reparse-check the normalized AST.

Complete selected-profile claims reserve source before fallback, and every source span has exactly one owner. Every
shared source spelling is claimed once in the shared phase before profile-specific dispatch; unselected profile
recognizers are unavailable. GFM adapters expose only CommonMark plus formal GFM semantics. Zensical adapters expose
only CommonMark plus the Zensical matrix. The shared AST and serializer are the only interoperability layer.

Python-Markdown and PyMdown are source-compatibility fixtures only, not user-selectable profiles or acceptance
authorities. The fixture uses `Markdown==3.10.3` and `pymdown-extensions==11.0.2`, with exactly `tables`, `sane_lists`,
`abbr`, `admonition`, `attr_list`, `def_list`, `footnotes`, `toc`, `pymdownx.betterem`, `pymdownx.caret`,
`pymdownx.details`, `pymdownx.emoji`, `pymdownx.keys`, `pymdownx.mark`, `pymdownx.smartsymbols`,
`pymdownx.superfences`, `pymdownx.tabbed`, `pymdownx.tasklist`, and `pymdownx.tilde`; options disable `fenced_code`,
`smartstrong`, `markdown_extra`, and `pymdownx.extra`. Zensical is a fixture/reference dependency only at
`zensical==0.0.57`, configured exactly as `{"theme": null, "plugins": [], "markdown_extensions": [], "build": false}`.
No separate MkDocs Material oracle or dependency is retained.

Runtime dependencies are limited to the parser and tokenizer needed by the selected profiles: `markdown-it-py==4.2.0`,
`linkify-it-py==2.0.3`, and `uc-micro-py==1.0.3` for the shared core and GFM linkification. The formatter-owned
Zensical recognizers require no third user-facing parser. `Markdown==3.10.3`, `pymdown-extensions==11.0.2`, and
`zensical==0.0.57` are fixture-only reference dependencies, pinned for comparison and never used to expand acceptance
or serialization. Their reference options remain the settled fixture options; no Material dependency is added.

The AST contains validated children and only metadata needed to preserve source meaning. Reference, footnote,
abbreviation, table, task, attribute, and annotation relationships resolve before rendering. Normalization applies
hierarchy, profile ownership, relationships, delimiters, attributes, tables, lists, width, and style policy. Rendering
is the sole Markdown serializer and prepends independent frontmatter serialization. The wrapper is a transport layer,
not a second formatter policy: it forwards profile, paths, mode, and failures without reinterpretation.


## Unknowns

- Which current corpus files require migration after both finite profiles are implemented?
- Which safe-YAML scalar spellings need compatibility fixtures without changing the fixed scalar model?
- Which additional deeply nested fixtures are needed for confidence in the pinned matrix?


## Technical notes

- The project already declares `pyyaml`; formatter parser dependencies are direct and version-pinned, never transitive.
- Existing scanning, wrapping, table alignment, frontmatter handling, and post-write validation are replaced by the AST
  contract.
- The controlled corpus permits coordinated migration before recursive formatting uses GFM as the default.
- Source syntax is the contract. Generated HTML, CSS, JavaScript, theme behavior, and build validation are not.
