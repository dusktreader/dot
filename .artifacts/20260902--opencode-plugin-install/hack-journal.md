# OpenCode plugin installation hack journal

This journal records the focused fix that restores installation of the OpenCode plugin dependency during `dt configure`.


## Intent

Restore the manifest tool that installs `@opencode-ai/plugin` into the configured home directory. Ensure checks and
installation honor `--override-home` instead of using the repository root, including override homes with spaces.


## Files changed

- `etc/install.yaml`: restored the `opencode-npm-deps` tool, dependent on `node`, using a quoted
  `$HOME/.config/opencode` path.
- `tests/test_configure.py`: replaced stale manifest assertions and added override-home regression coverage.
- `.artifacts/20260902--opencode-plugin-install/hack-journal.md`: recorded this change and its verification.

The package version in `.config/opencode/package.json` remains `1.18.14`. No generated dependencies or lockfiles were
added.


## Verification

`uv run pytest tests/test_configure.py` collected 57 tests and all passed, but the command returned nonzero because the
repository-wide coverage gate measured 21.16% for this focused file-only run, below the configured 70% threshold.

The focused test suite therefore verifies successfully with `uv run pytest tests/test_configure.py --no-cov`. The
review also confirmed that generated dependency artifacts remain ignored and that the package version is unchanged.
