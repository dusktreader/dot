# OpenCode plugin installation hack journal

This journal records the bounded fix for installing the OpenCode plugin in the repository-resolved configuration path.


## Intent

Use `$DOT_ROOT/.config/opencode` for the plugin existence check and npm installation prefix so OpenCode can resolve the
dependency from the tool's real repository path. Preserve the `node` dependency ordering and safe override-home test
coverage.


## Files changed

- `etc/install.yaml`: point the OpenCode plugin check and npm prefix at `$DOT_ROOT`.
- `tests/test_configure.py`: assert the manifest commands, subprocess environment, and override-home behavior.
- `.artifacts/20260903--opencode-plugin-install/hack-journal.md`: record this hack and its verification status.


## Verification status

`uv run pytest tests/test_configure.py --no-cov` passed with 57 tests.
