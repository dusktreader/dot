# SSH tunnel command

This journal records the implementation and focused verification for the `dt tunnel` command.


## Change

- Added the top-level `dt tunnel` command in `src/dot_tools/cli/main.py`.
- Added bare port forwarding and `LOCAL_PORT:REMOTE_PORT` parsing, with port-range validation.
- Added tests in `tests/test_cli_main.py` for SSH command construction, subprocess failure propagation, and malformed
  forwarding specifications.
- Updated `.dot_agents/dot.md` to list the new top-level command.


## Verification

Focused checks passed:

```shell
uv run pytest tests/test_cli_main.py --no-cov
uv run ruff check src/dot_tools/cli/main.py tests/test_cli_main.py
uv run dt tunnel --help
git diff --check
```

The full test suite also passed with 391 tests and 85.97% total coverage. A focused pytest run without the repository's
global coverage threshold was used because that threshold applies to the entire package, not only this test module.

`uv run ty check` remains blocked by 78 pre-existing diagnostics in unrelated files and dependencies.

The configured personal Luna executor and reviewer agents could not be dispatched because the configured endpoint
reported that `opencode/gpt-5.6-luna` was unavailable. The implementation and diff were reviewed directly instead.
