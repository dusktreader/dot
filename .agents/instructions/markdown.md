# Markdown Style Guide

Rules for all markdown files in `.agents/` directories.


## File structure

Every file must have:

1. An H1 title (first line, no blank line before it)
2. A paragraph providing an overview of the document
3. Content sections using H2 headings

```markdown
# Title

A brief paragraph describing what this document covers.


## First section
```


## Headings

- H1 (`#`): document title only — one per file, first line
- H2 (`##`): major sections
- H3–H4 (`###`, `####`): subsections
- H5+: avoid unless there is very good reason

No trailing punctuation on headings. No bold in headings.

Always include 2 blank lines before a heading UNLESS the parent heading has no content:

```markdown
# Parent

## Child

Child content here


### Grandchild
```

Add a separator bar before going back to a higher-level heading. Do not use a separator bar between siblings at
the same level or between a parent and its first child.

```markdown
## Section 1

## Section 2

---

# Next Top-Level
```


## Lists

Use a blank line before and after a list block. Do not put blank lines between list items. If a list item wraps
before 120 characters, indent the continuation line to align with the start of the text on the line above.


### Unordered lists

Use `-` (not `*` or `+`).

When useful, use a **bold** summary followed by a colon:

```markdown
- **First item**: description of the first item
- **Second item**: description of the second item
  - Nested item (two-space indent)
```

Do not overuse unordered lists. If items become verbose (longer than 120 characters), consider subsections instead.


### Ordered lists

Use `N.` for all items where N is the 1-based index. Use `N.M` style for sublists.

```markdown
1. First step
2. Second step
   2.1 First substep
   2.2 Second substep
3. Third step
```


## Code

Inline code: backticks for commands, file paths, env vars, function names, and literal values.

```text
Set `GITHUB_TOKEN` before running `gh auth login`.
```

Fenced code blocks: always specify the language, even if it is just `text`.
Use `shell` for shell commands (not `bash` or `sh`).

````markdown
```shell
gh auth switch --user dusktreader
```

```python
import subprocess
```

```text
Plain text output.
```
````


## Tables

Use tables for reference data (account mappings, option comparisons, file inventories).

```markdown
| Column 1  | Column 2  | Column 3  |
|-----------|-----------|-----------|
| value     | value     | value     |
```

**Always** align columns for human readability. Keep cell content short — link out to docs for detail.


## Tone and style

- Direct and concise — no filler phrases ("In order to...", "Please note that...")
- Present tense for descriptions ("The service acquires a lock")
- Imperative mood for instructions ("Run `gh auth status`")
- No marketing language, superlatives, or emoji (unless the content is a status table)
- Sentence case for headings: "Account mapping" (not "Account Mapping")


## Line length

Wrap all prose lines at 120 characters. Code blocks and tables are exempt.


## What to avoid

- Redundant introductions ("This document explains...")
- Restating the H1 in the first paragraph
- Deep heading nesting (H5+)
- Walls of prose — break up into paragraphs or subsections
- Overuse of bullet lists
- Inconsistent bullet markers (`-` vs `*` in the same file)
- Trailing whitespace
- Lines exceeding 120 characters (outside code blocks and tables)
- Raw HTML — never embed `<tags>` in Markdown files for any reason
