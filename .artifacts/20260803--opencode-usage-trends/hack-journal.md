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

- Changed plotted x positions from UTC calendar timestamps to sequential positions for populated dates only.
- Switched date labels to full ISO dates with hyphens, such as `2026-08-01`.
- Added regression coverage proving that missing calendar days produce no labels or bars and that sparse dates remain
  adjacent and aligned with their bars.
- Replaced the plotille axis-label slice replacement with a separately constructed label line, using eleven columns per
  populated date so full labels remain readable and separated.


## Verification

The corrective follow-up now derives the label origin from the chart baseline, with a temporary geometry-only baseline
for all-zero-cost series. It also covers unequal-height bars, zero-cost dates, a single-day label, and width growth.

`uv run pytest --no-cov tests/test_opencode_trends.py tests/test_cli_opencode_trends.py` passed with 18 tests after the
corrective follow-up.

`uv run ruff check src tests` passed.

`node ~/.agents/tools/check-markdown-format.mjs .artifacts/20260803--opencode-usage-trends/hack-journal.md` passed.

`git diff --check` passed.
