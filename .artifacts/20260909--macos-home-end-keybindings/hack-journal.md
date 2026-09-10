# Hack journal: Add macOS Home and End keybindings

This record documents the focused installer change that makes macOS Home and End keys behave like their Windows
counterparts in standard Cocoa text fields.


## Intent

Install a native `DefaultKeyBinding.dict` during `dt configure` on macOS only. Keep Linux and other platforms
untouched, and make repeated configuration runs skip the copy when the installed file already matches the repository
version.


## Changes

- Added `etc/macos/DefaultKeyBinding.dict` with line, document, and selection mappings for Home and End.
- Added a Darwin-only `settings` entry to `etc/install.yaml` that creates `~/Library/KeyBindings` and copies the tracked
  file into place.
- Added a manifest and keybinding-content contract test in `tests/test_install.py`.


## Verification

The focused manifest test and lint passed:

```shell
uv run pytest tests/test_install.py -k home_end --no-cov
uv run ruff check tests/test_install.py
```
