# Markdown heading depth

Removed the Markdown validator's H5+ heading-depth error so necessary deep headings are allowed, matching the Markdown
style guidance.


## Changes

- Updated `.agents/tools/check-markdown-format.mjs` to stop rejecting H5 and deeper headings.
- Kept the existing heading syntax and formatting checks.


## Verification

- `node ~/.agents/tools/check-markdown-format.mjs ".agents/instructions/markdown.md"`: passed.
