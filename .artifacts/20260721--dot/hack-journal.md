# Sortable total cost

Record the scoped fix to make the OpenCode cost report's displayed total-cost column sortable.


## Change

`opencode costs --sort` now accepts unique, case-insensitive partial column labels. Exact label matches take precedence.
`Total Cost` is an available sort column and orders table root session groups by their recorded subtree totals.


## Files changed

- `src/dot_tools/cli/opencode.py`
- `src/dot_tools/opencode_costs.py`
- `tests/test_cli_opencode_costs.py`
- `tests/test_opencode_costs.py`


## Verification

Run the focused OpenCode cost-report tests and the Markdown format validator for this journal.
