# Design Plan: Generic AST-based Markdown formatter

This plan defines a deterministic, flavor-agnostic formatter for the repository. It applies repository style to a
bounded CommonMark subset and preserves source only where the parser provides a safe boundary.


## Goal

Produce readable, stable Markdown with optional deterministic YAML frontmatter. The formatter owns a small structural
subset, preserves parser-delimited opaque source spans outside that subset, and fails rather than guessing when required
structure or repository policy cannot be established. It is not a validator or an emulator for arbitrary extensions.


## Acceptance criteria

#### AC01: Frontmatter has an exact safe envelope

At byte 0, a line exactly equal to `---` opens frontmatter. A later line exactly equal to `---` closes it; a missing
close fails and never becomes body Markdown. The accepted YAML root is a mapping with string keys, nested mappings and
sequences, and null, boolean, finite integer, finite real, or string scalars. Duplicate keys, aliases, anchors, tags,
timestamps, binary values, sets, multiple documents, and invalid values fail. The root is a mapping. An empty root emits
an empty YAML document between the delimiters. Mapping serialization is a block mapping with keys in Unicode code-point
order, with each `KEY: VALUE` on its own LF-terminated line. Nested mappings and sequences are indented exactly two
spaces per level. An empty mapping value emits `{}` and an empty sequence value emits `[]`. A nonempty sequence emits
`- VALUE` entries on separate lines; nested values are indented two spaces below the dash. Null emits `null`; booleans
emit `true` or `false`; integers emit base-10 with no leading zeroes except `0`, and negative zero emits `0`. Finite
reals use lowercase decimal scientific notation only when absolute value is at least `1e21` or below `1e-6` and
nonzero; otherwise they use fixed decimal notation. The exponent has no plus sign, has `-` only when negative, and has
no leading zeroes. Trailing fractional zeroes and the decimal point are removed, while at least one digit remains
before and after the decimal point as needed. If a finite value cannot be represented without loss under this rule, it
is rejected. Strings are double quoted; backslash, double quote, LF, CR, tab, and other C0/control characters are
escaped as `\\`, `\"`, `\\n`, `\\r`, `\\t`, and `\\u00NN` respectively. Invalid Unicode is rejected. Output is `---`
LF, the serialized mapping, `---` LF, one additional LF, the body, and exactly one final LF. Existing exact byte-0 and
closing-delimiter rules remain in force. Without frontmatter, the body starts directly at H1.


#### AC02: Body H1 policy is AST-scoped

The first recognized top-level body AST entry must be H1, and there must be exactly one recognized top-level H1. A
top-level opaque or parser-delimited block before it fails. H1 syntax inside recognized containers or opaque regions is
outside the top-level count; recognized headings inside containers still receive local spacing. This is repository
style,
not dialect validation.


#### AC03: Parsing and preservation stay within a bounded contract

Use `markdown-it-py` with CommonMark plus the table rule. The owned subset is headings, paragraphs, lists and list
items,
block quotes, fenced and indented code, parser-identified pipe tables, and inline text, code, emphasis, strong, links,
images, and hard breaks when source maps permit. Content outside it is preserved only as parser-delimited opaque source
spans. Opaque spans are preserved byte-for-byte, including CRLF and trailing whitespace. They are exempt from global LF
and trailing-whitespace normalization, wrapping, reflow, renumbering, and every other formatting operation. Recognized
nodes use canonical LF. If a recognized node contains an opaque child and rewriting its surrounding structure would
alter
or require reflowing that child, preserve the entire containing block unchanged. Raw HTML detection scans body source
outside code, including inside opaque spans, and fails. If an unknown or mixed region has no safe parser boundary, leave
its entire containing block unchanged. Unknown extension semantics are outside the contract; the formatter does not
claim to detect extensions parsed as ordinary text, and does not execute or expand extensions.


#### AC04: Prose and lists render deterministically

Prose wraps at 120 Unicode code points, excluding structural indentation, code payloads, and tables; unbreakable tokens
are not split. Each ordered list uses its first marker as its start and renders later markers as sequential decimal
`N.`. Unordered markers render as `-`. Continuation indentation equals the active container prefix plus the rendered
marker width (`len("N. ")` or `len("- ")`) and, when present, the task prefix `[ ] ` or `[x] `; continuation starts at
the content column. Nested markers begin at the parent content column and apply recursively, including multi-digit
markers
and block quotes. Item order and task-marker text/state are preserved. Parser-identified lazy continuation is normalized
to this indentation; if structure cannot be determined, preserve the containing block unchanged. Opaque spans are never
split.


#### AC05: Headings use repository spacing

H1 has no preceding blank line in the body. Every non-H1 heading normally has exactly two blank lines before it. A child
heading's structural parent is the nearest preceding lower-level heading in the same container. If that parent has no
non-heading body block before the child, use one blank line; otherwise use two. Sibling headings use two. Do not invent
blank lines at container edges. Apply these rules inside recognized containers.


#### AC06: Downward heading transitions use one idempotent separator

The AST has a formatter-generated `HeadingSeparator`, not a thematic-break AST. At every transition to a heading lower
than the immediately previous heading in the same container, reuse or consume a source thematic-break spelling (`---`,
`***`, or `___`) immediately before that heading if present; otherwise insert one. The separator emits exactly `---`
plus
LF, with one blank line before and after, overriding ordinary heading spacing. Equal, upward, and first-H1 transitions
have no generated separator. Source thematic-break blocks outside a transition are preserved verbatim and do not affect
transitions. This positional reuse rule makes a second pass idempotent, including the active container prefix.


#### AC07: Recognized pipe tables are readable and lossless

A recognized pipe table has a header row immediately followed by a separator row. Each physical row may have at most one
leading framing `|` and at most one trailing framing `|`; framing pipes never count as cells. A row consisting only of
`|` has zero cells and is invalid as a header or separator. Escaped pipes and code-span pipes are cell content. The
header and separator define the column count. Short data rows pad with empty cells. Any non-framing extra cell,
including an empty cell, is an error and is never dropped. The separator row must have exactly the header count; it is
never padded or treated as ragged. Each separator cell is unaligned or preserves its input left, right, or center
marker.
Padded and normalized separator width uses that cell's own marker. Data cells are always left-aligned by padding on the
right; alignment markers are visual intent only and do not alter data padding. Unrecognized pipe text remains unchanged.
Cell text is canonical inline output with ordinary surrounding spaces stripped. A literal semantic backslash run
immediately before a literal pipe is emitted as `2k+1` ASCII backslashes followed by `|`; a literal pipe alone is
emitted as one backslash followed by `|`. Pipes in code spans are untouched. Define each separator width as the maximum
Unicode code-point length of column content and `3 + marker count`; dashes fill the remaining width. Always emit leading
and trailing framing pipes with one ASCII space inside. Preserve row and cell order and require reparsing and formatting
again to produce identical output.


#### AC08: Code payloads remain untouched

Code normalization is unconditional. Missing language becomes `text`; opening-fence info token `bash` or `sh` becomes
`shell`; other info text remains unchanged. Code payload is never wrapped or reflowed, including trailing spaces, and
its payload bytes are preserved. For fenced and indented code, use a backtick fence of length `max(3, longest
consecutive backtick run in the payload + 1)`. If any info text contains a backtick and therefore cannot be emitted
with a backtick fence, use a tilde fence of `max(3, longest consecutive tilde run in the payload + 1)` while preserving
the info text. The final document uses LF line endings and exactly one final LF outside preserved opaque spans and code
payload bytes. HTML-looking code remains code. Code is never wrapped.


#### AC09: CLI operations are deterministic and fail safely

`format PATH...` and `check PATH...` accept files or recursively discovered `.md` files. CLI direct paths resolve
against
the process current working directory. Wrapper relative paths resolve against the caller process current working
directory, captured once at wrapper entry before expansion, sorting, or deduplication; absolute paths are unchanged.
Sort
and deduplicate the final path set.
Missing
explicit paths and explicit non-Markdown files are errors; zero discovered files is a successful no-op. Diagnostics go
to
stderr and summaries to stdout. `format` preflights every file before writing, writes none if any preflight fails, then
atomically commits sorted files and stops at the first write error, reporting previous committed and untouched files. A
single-file failure leaves the original unchanged. `check` never writes and succeeds only when every file equals
canonical output. The wrapper propagates failure status.


## Architecture

The formatter flows through five stages: exact frontmatter extraction and safe serialization; `markdown-it-py` parsing
with source-span association; normalization of owned nodes and parser-delimited opaque spans; deterministic rendering;
and atomic writes. Parsing identifies only the bounded structural subset, code boundaries, headings, lists, tables, and
source-mapped inline spans. Normalization handles wrapping, list columns, heading spacing, positional separator reuse,
table geometry, code fences, and raw-HTML rejection. Recognized nodes render with canonical LF; opaque spans and code
payloads retain their specified source bytes. A region without a safe parser boundary remains wholly unchanged. All
file outputs are complete before any replacement, and multi-file commit follows the preflight and stop-on-first-error
behavior in AC09.


## Technical Notes

Fixture inventory is implementation QA, not a design unknown; it should cover frontmatter, AST boundaries, headings,
lists, tables, code, raw HTML, opaque spans, idempotence, and multi-file failure behavior. Canonical output has no
trailing whitespace outside preserved opaque spans and code payloads and is idempotent. The formatter does not execute
or
expand flavor extensions.
