# OpenCode usage trends legend totals and date alignment

This journal records bounded follow-up changes to the OpenCode trends chart legend and date-axis rendering.


## Change

- Updated `render_trends` to calculate each legend total from the displayed `TrendSeries` values.
- Added focused coverage for multiple named models, grouped `other`, and the selected date range.
- Configured the plotille x-axis to allocate ten columns per daily bar, align each date tick with its bar, and suppress
  repeated or irrelevant date labels.
- Added regression coverage proving that each date in a multi-day chart is shown once and aligns with its bar.
- Corrected the axis sizing to use the full calendar span, including days without recorded usage, and kept plotted
  timestamps timezone-aware in UTC.
- Added sparse-date and longer-range regression coverage.


## Files modified

- `UPDATED` `src/dot_tools/opencode_trends.py`
- `UPDATED` `tests/test_opencode_trends.py`
- `UPDATED` `.artifacts/20260803--opencode-usage-trends/hack-journal.md`


## Follow-up

The previous follow-up still inferred the first bar column by scanning a rendered `$0.00` row. That row includes
plotille's faint baseline and can contain no markers for zero-cost dates, so it was not a reliable coordinate source.

The new implementation hides plotille's x-axis and uses a controlled sequential coordinate system. It constructs the
date axis from the same eleven-character bar geometry and the known thirteen-character y-axis prefix. This keeps full
hyphenated ISO labels aligned for unequal heights, zero-cost dates, sparse dates, and wide charts without scanning
rendered rows.


## Verification

The corrective follow-up now derives the label origin from the chart baseline, with a temporary geometry-only baseline
for all-zero-cost series. It also covers unequal-height bars, zero-cost dates, a single-day label, and width growth.

This follow-up widens each populated date slot to twelve terminal columns, renders a three-character bar, and centers
each full ISO date label on that slot. Adjacent labels therefore retain two separating spaces without scanning rendered
rows or relying on offsets disconnected from the shared plot geometry.

`uv run pytest --no-cov tests/test_opencode_trends.py tests/test_cli_opencode_trends.py` passed with 20 tests after the
date-slot follow-up. The inspected unequal-height output rendered three-character bars at each date slot, with centered
labels and two spaces between `2025-10-09`, `2025-10-10`, and `2025-10-11`.

`uv run ruff check src tests` passed.

`node ~/.agents/tools/check-markdown-format.mjs .artifacts/20260803--opencode-usage-trends/hack-journal.md` passed.

`git diff --check` passed.


## Follow-up: show six named models by default

Changed the application and `dt opencode trends` defaults from three to six named models. The default now keeps six
named model series visible and groups a seventh and later named models into `other`; explicit `--max-models` values
remain unchanged.

Added focused coverage for the six-model default, seventh-model grouping, and explicit lower limits.


## Verification

`uv run pytest --no-cov tests/test_opencode_trends.py tests/test_cli_opencode_trends.py` passed.

`uv run dt opencode trends --help` shows the default of 6 for `--max-models`.

`uv run ruff check src tests` passed.

`node ~/.agents/tools/check-markdown-format.mjs .artifacts/20260803--opencode-usage-trends/hack-journal.md` passed.

`git diff --check` passed.


## Follow-up: separate the total from legend entries

Added a `-------` divider immediately before the total recorded cost line so the aggregate remains visually distinct
from the per-model legend entries. Preserved the existing no-data behavior and chart rendering and filtering.

Updated focused trend coverage to assert that the divider directly precedes the total.


## Verification

`uv run pytest --no-cov tests/test_opencode_trends.py tests/test_cli_opencode_trends.py` passed.

`uv run ruff check src tests` passed.

`node ~/.agents/tools/check-markdown-format.mjs .artifacts/20260803--opencode-usage-trends/hack-journal.md` passed.

`git diff --check` passed.


## Follow-up: show selected chart total

Added a total recorded cost line immediately beneath the legend. The total sums the displayed `TrendSeries` values, so
provider filters, date filters, grouped `other`, and zero-cost values are represented without re-reading sessions. The
existing no-data message remains unchanged and does not include a total.

Added focused coverage for multi-model totals, provider-filtered totals, grouped `other`, and no-data output.


## Verification

`uv run pytest --no-cov tests/test_opencode_trends.py tests/test_cli_opencode_trends.py` passed.

`uv run ruff check src tests` passed.

`node ~/.agents/tools/check-markdown-format.mjs .artifacts/20260803--opencode-usage-trends/hack-journal.md` passed.

`git diff --check` passed.

Inspected rendered output: the legend entries are followed immediately by `Total recorded cost: $2.00`, with no
additional chart content between the legend and total.


## Follow-up: filter usage by provider

Directory-based work and personal classification was removed because a work model can be used in a personal
repository. Costs and trends now accept an exact `--provider` filter, matching the provider component before the first
slash in normalized model values. Unqualified models and substring matches do not qualify. The selected provider is
disclosed in cost JSON metadata and filters, and in the trends heading. The obsolete scope helper and scope tests were
removed.


## Verification

`uv run pytest --no-cov tests/test_opencode_costs.py tests/test_opencode_trends.py tests/test_cli_opencode_costs.py
tests/test_cli_opencode_trends.py` passed with 61 tests.

`uv run dt opencode costs --help` and `uv run dt opencode trends --help` show `--provider` and no `--scope`.

`uv run ruff check src tests` passed.

`node ~/.agents/tools/check-markdown-format.mjs .artifacts/20260803--opencode-usage-trends/hack-journal.md` passed.

`git diff --check` passed.


## Follow-up: filter usage by provider

Directory-based work and personal classification was removed because a work model can be used in a personal
repository. Costs and trends now accept an exact `--provider` filter, matching the provider component before the first
slash in normalized model values. Unqualified models and substring matches do not qualify. The selected provider is
disclosed in cost JSON metadata and filters, and in the trends heading. The obsolete scope helper and scope tests were
removed.


## Verification

`uv run pytest --no-cov tests/test_opencode_costs.py tests/test_opencode_trends.py tests/test_cli_opencode_costs.py
tests/test_cli_opencode_trends.py` passed with 61 tests.

`uv run dt opencode costs --help` and `uv run dt opencode trends --help` show `--provider` and no `--scope`.

`uv run ruff check src tests` passed.

`node ~/.agents/tools/check-markdown-format.mjs .artifacts/20260803--opencode-usage-trends/hack-journal.md` passed.

`git diff --check` passed.


## Follow-up: resolve scope paths before classification

Corrected `is_work_directory` to resolve both the candidate directory and `WORK_ROOT` before checking their relative
path. This keeps `~`, absolute, and relative inputs supported while classifying traversal paths and symlink targets
outside the work root as personal.

Added focused coverage for relative paths, `..` traversal, and a symlink from the work root to a directory outside it.

`uv run pytest --no-cov tests/test_opencode_costs.py tests/test_opencode_trends.py tests/test_cli_opencode_costs.py
tests/test_cli_opencode_trends.py` passed.

`uv run ruff check src tests` passed.

`node ~/.agents/tools/check-markdown-format.mjs .artifacts/20260803--opencode-usage-trends/hack-journal.md` passed.

`git diff --check` passed.


## Follow-up: explicit work and personal usage scopes

OpenCode costs and trends now accept `--scope all|work|personal`. Scope classification lives in the reusable
`opencode_scope` model helper and treats `~/src/mhe` plus descendants as work using path-component-safe matching.
Reports filter before calculating metrics, and trends aggregate only selected sessions. Cost JSON filters and metadata,
along with the trends heading, disclose the selected scope.

Focused verification:

`uv run pytest --no-cov tests/test_opencode_costs.py tests/test_opencode_trends.py tests/test_cli_opencode_costs.py
tests/test_cli_opencode_trends.py` passed.

`uv run ruff check src tests` passed.

`node ~/.agents/tools/check-markdown-format.mjs .artifacts/20260803--opencode-usage-trends/hack-journal.md` passed.

`git diff --check` passed.


## Follow-up: remove plotille origin lines

Plotille's `origin` setting defaults to `True`. Although the renderer already hides plotille's x-axis, that setting
still draws the dotted horizontal zero baseline and vertical origin line. Set `figure.origin = False` while preserving
the y-axis, custom date ruler, stacked bars, and legend.

Added focused regression coverage that rejects the plotille origin characters `⣀` and `⡇` while requiring the legitimate
three-character bar, custom date label, and date ruler.

`uv run pytest --no-cov tests/test_opencode_trends.py tests/test_cli_opencode_trends.py` passed with 21 tests.

Inspected rendered output: the `$0.00` row contains only whitespace outside the three-character `███` bar, and the
custom `-> (Date)` ruler and `2025-10-09` label remain present.


## Corrective follow-up: retain unmodeled sessions

Changed `other_needed` to retain the `other` series whenever sessions with `model=None` contribute recorded cost, even
when no named models require grouping. Added regression coverage for an only-unmodeled dataset, including its legend
entry, total, and single divider immediately before the total. Provider filtering, `max_models`, the divider before
`Total recorded cost`, and no-data behavior remain unchanged.


## Verification

`uv run pytest --no-cov tests/test_opencode_trends.py tests/test_cli_opencode_trends.py` passed.

`uv run ruff check src tests` passed.

`node ~/.agents/tools/check-markdown-format.mjs .artifacts/20260803--opencode-usage-trends/hack-journal.md` passed.

`git diff --check` passed.

`uv run ruff check src tests` passed.

`node ~/.agents/tools/check-markdown-format.mjs .artifacts/20260803--opencode-usage-trends/hack-journal.md` passed.

`git diff --check` passed.
