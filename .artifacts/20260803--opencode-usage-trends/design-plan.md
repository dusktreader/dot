# Design Plan: OpenCode usage trends

Add a terminal chart for recorded OpenCode session costs while retaining the existing tabular cost report.
The command filters sessions by an inclusive starting date, aggregates recorded dollars by calendar day and
model, and renders colored stacked bars with `plotille`.


## Goal

Provide a quick visual view of how recorded OpenCode usage changes over time through `dt opencode trends`.
The command reads the same local session data as `costs`, applies the same date-expression semantics for
`--since`, and presents daily recorded cost in a terminal-friendly chart with dates on the x-axis and dollars
on the y-axis. The chart highlights the three highest-spend models with distinct colors and combines all
remaining models into an `other` segment.

The feature adds `plotille` as a runtime dependency without changing the behavior or output contracts of
`dt opencode costs`.


## Acceptance Criteria

### Command behavior

#### AC01: Trends command is available

`dt opencode trends` is exposed by the existing `dt` CLI and produces terminal output without requiring an
alternate reporting mode.


#### AC02: Since filtering matches costs

The optional `--since` value accepts the same ISO and natural-language date expressions as `costs`, treats the
date as inclusive, and reports an actionable CLI error for an unparseable value.


### Aggregation

#### AC03: Usage is aggregated by day

Each plotted day represents the sum of all numeric recorded session costs whose session timestamps fall on
that calendar date. Calendar dates use the same UTC interpretation as the existing cost report. Zero-dollar
records contribute zero; sessions without a recorded cost do not contribute to a day. Calendar dates with no
recorded usage between plotted dates are omitted rather than represented as `$0` points.


#### AC04: Daily points are chronologically ordered

The chart plots one stacked bar per day represented by recorded usage, in ascending date order. Every bar has
a date on the x-axis and its total aggregated dollar amount on the y-axis.


#### AC05: Top models use colored stacked segments

Across the selected date range, the three models with the highest recorded spend appear as separate, consistently
colored segments in each daily stacked bar. All other models appear in a single `other` segment. The legend
identifies every displayed model and its color. Ties at the third-place boundary are resolved by model name in
ascending order. Sessions without a model are included in `other`, and fewer than three available models produce
only the available model segments plus `other` when needed.


### Output and edge cases

#### AC06: Chart communicates dollars and dates

The terminal chart uses `plotille`, labels or formats the horizontal scale with the represented dates, and
labels or formats the vertical scale as dollar-denominated cost values.


#### AC07: Empty data is handled clearly

When no selected session has a numeric recorded cost, including when the database contains no sessions or the
`--since` date excludes all usage, the command exits successfully and prints a clear no-data message instead
of rendering a misleading chart.


#### AC08: A single day remains a valid chart

When the selected data produces one day and one aggregated point, the command exits successfully and renders
a valid terminal chart that still identifies the date and dollar value rather than failing because a line or
range cannot be formed.


#### AC09: Costs remains unchanged

Existing `dt opencode costs` behavior continues to work, including its current filters, date parsing, output
formats, read-only database access, and error handling.


#### AC10: Runtime installation includes the charting library

Installing the application makes `plotille` available at runtime, and invoking the trends command does not
fail because the charting dependency is absent from the declared application dependencies.


## Architecture

The existing OpenCode CLI remains the command boundary. A new sibling command under the `opencode` command
group owns trends-specific presentation while sharing the established date parsing policy, session loading
boundary, and error handling conventions.

The read-only session data source supplies normalized session records to a trends aggregation stage. That stage
applies the inclusive starting-date filter, converts session timestamps to the established UTC calendar date,
discards records with no recorded cost, and sums costs into daily values grouped by model. It ranks models by
total selected-range spend, preserves the top three as separate series, folds all remaining models into `other`,
and returns chronologically ordered daily segment values. It distinguishes no numeric usage from a populated
series.

The presentation stage maps the daily segment series to a `plotille` terminal chart using colored stacked bars.
Dates remain the x-axis values and daily dollar totals remain the y-axis values. The legend maps colors to the
top models and `other`. A populated series is rendered directly to standard terminal output. A single point
uses the same chart path as any other populated series, while no numeric usage follows an explicit no-data path.

The existing costs reporting path remains separate at the presentation level. Both commands may use the same
read-only source, but trends does not alter cost report rows, totals, sorting, formats, or database state.


## Technical Notes

- The session database is a read-only source of recorded usage; trends does not write, migrate, or update it.
- The chart represents recorded cost, not locally estimated cost, so it remains consistent with the meaning of
  actual usage in `costs`.
- The runtime dependency must be declared with the application dependencies rather than only development tools.
