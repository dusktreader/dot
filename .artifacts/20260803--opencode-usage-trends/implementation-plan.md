# Implementation Plan: OpenCode usage trends

Add the `dt opencode trends` command, daily model-cost aggregation, and a colored stacked-bar terminal chart while
preserving the existing `costs` command and read-only database behavior.


## Goal

Build the trends feature in a small presentation module that consumes `SessionRecord` values from the existing
`OpenCodeSessionStore`. Filter sessions by the existing `_parse_date` semantics, aggregate recorded costs by UTC
date and model, select a configurable number of top models across the selected range, and group all remaining or
unmodelled sessions as `other`.

Render one chronologically ordered stacked bar per usage date with stable colors and a legend through `plotille`. Keep
`costs` unchanged and declare `plotille` as a runtime dependency.


## Project Commands

### Run focused trend tests

Command:

```shell
uv run pytest tests/test_opencode_trends.py tests/test_cli_opencode_trends.py tests/test_cli_opencode_costs.py
```

Expected Output:

All trend tests and existing cost CLI tests pass.


### Run the full test suite

Command:

```shell
uv run pytest
```

Expected Output:

All tests pass and the configured coverage threshold remains satisfied.


### Run lint and type checks

Command:

```shell
uv run ruff check src tests && uv run ty check
```

Expected Output:

Ruff and ty complete without errors.


### Synchronize dependencies

Command:

```shell
uv lock
```

Expected Output:

`uv.lock` is updated successfully and contains the declared `plotille` runtime dependency.


### Validate Markdown artifacts

Command:

```shell
~/.agents/tools/markdown-format.py check .artifacts/20260803--opencode-usage-trends/*.md
```

Expected Output:

The Markdown validator passes every project artifact.


## Project Standards

- [Repository guide](../../.dot_agents/dot.md) defines the `dt` CLI, uv workflow, and project quality commands.
- [Python instructions](../../.agents/instructions/python.md) govern Python implementation and tests.
- [Markdown style guide](../../.agents/instructions/markdown.md) governs project artifacts.
- [`pyproject.toml`](../../pyproject.toml) defines runtime dependencies and the 120-character Ruff limit.
- [`src/dot_tools/opencode_costs.py`](../../src/dot_tools/opencode_costs.py) defines `SessionRecord`, UTC date handling,
  and the read-only `OpenCodeSessionStore`.
- [`src/dot_tools/cli/opencode.py`](../../src/dot_tools/cli/opencode.py) defines `costs` and `_parse_date`.
- [`tests/test_opencode_costs.py`](../../tests/test_opencode_costs.py) and
  [`tests/test_cli_opencode_costs.py`](../../tests/test_cli_opencode_costs.py) define existing test conventions.


## Relevant Skills

- `execute-implementation-plan`
- `review-implementation-execution`
- `review-code`


## Execution

### 01: Add trend aggregation and rendering tests

Define the observable aggregation and rendering contract before implementation.


#### Acceptance Criteria

- AC01: Tests verify that costs on the same UTC date are summed by model and dates are returned in ascending order.
- AC02: Tests verify inclusive `since`, zero-dollar costs, omitted `None` costs, gap dates, and unmodelled sessions
  grouped as `other`.
- AC03: Tests verify configurable top-model selection by range spend, alphabetical tie-breaking, and stable series
  order.
- AC04: Tests verify empty data returns the no-data message and one-day data avoids an equal-axis-range error.
- AC05: Tests verify date labels, dollar labeling, the model legend, and colored stacked-bar series.


#### Steps

1. Create `tests/test_opencode_trends.py` with reusable `SessionRecord` fixtures matching existing cost tests.
2. Write failing tests for daily model aggregation, UTC conversion, inclusive filtering, gap omission, and `other`.
3. Write failing tests for top-three ranking, alphabetical ties, unmodelled sessions, and stable series order.
4. Write failing renderer tests for empty, single-day, multi-day, and colored stacked bars.
5. Run the focused trend test command and confirm the new tests fail because the trend module is absent.


### 02: Implement trend data and plot rendering

Create the reusable trend module consumed by the CLI.


#### Acceptance Criteria

- AC01: `src/dot_tools/opencode_trends.py` exposes aggregation and rendering helpers used by CLI tests.
- AC02: Aggregation uses numeric costs, UTC dates, inclusive `since`, gap omission, and model groups.
- AC03: Ranking uses selected-range spend, keeps at most `max_models` named models, resolves ties alphabetically, and
  assigns remaining or unmodelled costs to `other`; an empty `other` series is omitted.
- AC04: Rendering produces one ordered stacked bar per date, with stable colors, a legend, and dollar-denominated
  output.
- AC05: Empty data returns a clear no-data message; one represented day is padded for plotting without adding synthetic
  data.


#### Steps

1. Add typed data structures for daily model costs and the selected model/color legend.
2. Implement `aggregate_daily_model_costs(sessions, since=None)` using `Report.build` UTC conversion and date
   comparison.
3. Select top models from range totals, sort ties by model name, and fold other model keys plus `None` into `other`.
4. Implement `render_trends(series)` with `plotille` figure or canvas primitives for colored cumulative bar
   segments.
5. Use fixed colors for the three model slots and `other`; keep legend and stack order aligned.
6. Handle one-date input by padding x-axis limits without creating a data point. Return the explicit no-data
   message before invoking plotille when the series is empty.
7. Run the focused trend tests and confirm they pass.


### 03: Add the CLI command and dependency

Wire the trend module into the existing OpenCode command group without changing `costs`.


#### Acceptance Criteria

- AC01: `dt opencode trends` is listed in help and accepts `--since` and non-negative `--max-models`; `--since` uses
  the existing `_parse_date` parser.
- AC02: The command loads sessions through one `OpenCodeSessionStore` context, aggregates them, and prints the chart or
  no-data message.
- AC03: Invalid dates use the existing error handling and no database writes or alternate data source are introduced.
- AC04: `dt opencode costs` remains unchanged and its focused tests continue to pass.
- AC05: `plotille` is a runtime dependency and `uv.lock` is synchronized.


#### Steps

1. Add `plotille>=5.0.0` to the runtime dependencies in `pyproject.toml`.
2. Run `uv lock` and inspect the diff to confirm only the intended dependency metadata changes.
3. Add `trends` to `src/dot_tools/cli/opencode.py`, reusing `_parse_date`, `handle_errors`, `log_error`, and the
   existing session-store context-manager pattern.
4. Add `tests/test_cli_opencode_trends.py` with a patched `OpenCodeSessionStore`. Cover help, ISO and natural-language
   `--since`, empty data, one day, multiple days, top-model output, and errors.
5. Run the focused trend and cost CLI tests.


### 04: Verify compatibility and quality

Run the repository checks and confirm the existing cost workflow remains intact.


#### Acceptance Criteria

- AC01: Full pytest, Ruff, and ty checks pass.
- AC02: Existing cost tests pass without modifying their expected behavior or output contracts.
- AC03: The Markdown validator passes all project artifacts.
- AC04: The final diff contains only the planned trend implementation, tests, dependency metadata, lockfile, and
  artifacts.


#### Steps

1. Run the focused tests and inspect chart output for multi-model stacked bars and the legend.
2. Run the full test suite, Ruff, and ty checks.
3. Run the Markdown validator over the project artifacts.
4. Inspect `git diff`, `git diff --check`, and `git status` for unintended changes.


## Technical Notes

- Use recorded costs, not local estimates, so trends matches the meaning of actual usage in `costs`.
- Keep the session database read-only. Do not add schema changes, migrations, writes, or cleanup behavior.
- `plotille` does not need a high-level stacked-bar helper. Compose colored cumulative vertical segments with its figure
  or canvas primitives while retaining plotille-generated axes and terminal output.
- Do not fill missing calendar dates with zero values. Plot only dates represented by recorded usage.
