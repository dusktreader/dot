# Manual-testing issue: unreadable OpenCode cost table

This issue records the reported terminal-output problem and the follow-up fixes for `dt opencode costs`.


## Description

The default table output used space-delimited interpolated values. Long directories, model names, statuses, and
provenance values made column boundaries ambiguous in a terminal. Expected behavior is an aligned table that remains
readable in terminal output. JSON, CSV, and `--file` behavior must remain unchanged; file output must not contain
ANSI terminal control codes.


## Reproduction steps

1. Run `dt opencode costs` against a database containing a normal session row.
2. Observe the former space-delimited output with inconsistent column boundaries.
3. Run `dt opencode costs --file /tmp/opencode-costs.txt` and inspect the saved output.


## Root cause

- **Confirmed** (`src/dot_tools/opencode_costs.py:278-302` before this fix): table rows were assembled with f-strings
  and single spaces, so values were not padded or bounded as columns.
- **Confirmed** (`src/dot_tools/cli/opencode.py:34-38`): the same renderer string was used for terminal and file output,
  with no explicit terminal/file rendering policy.


## Blast radius

- Default `dt opencode costs` table output was difficult to scan.
- Long values could visually merge adjacent dimensions.
- JSON, CSV, and report calculations were not affected.


## Proposed approach

Use Rich `Table` and `Console` for the table renderer. Force a non-terminal, colorless console for captured output so
terminal output remains readable and `--file` receives plain text without ANSI control codes. Keep JSON and CSV branches
unchanged and retain the existing file-parent validation.


## Resolution

The report now parses JSON model values into `providerID/id`, preserves normalized model filters, and uses the parsed
model identifier for pricing. Home-descendant directories display with a `~/` prefix. The table uses unwrapped Rich
columns with ignored overflow and a dynamically sized console, so long fields remain complete without ellipses or
wrapping. It labels compact estimate statuses and discloses the recorded-cost outlier metric, threshold, eligible
population, and flagged count. JSON and CSV retain detailed estimate reasons and report metadata. Focused verification
passes with 19 tests and Ruff passes. The `Recorded` and `Estimate` cells now display USD values with a dollar sign and
two decimal places. The `Recorded`, `Estimate`, and `Cache Ratio` values use explicit right-aligned Rich cells while
headers retain their natural alignment. JSON, CSV, and internal calculations retain full precision.


## Sort follow-up

`dt opencode costs` accepts `--sort [asc:|desc:]<column>` with comma-separated keys. Headers are matched
case-insensitively, omitted directions default to descending, and all output formats use the same row order.
Invalid directions and columns return an actionable error.
