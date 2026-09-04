# Hack journal: Add macOS Caps Lock to Escape support

This record documents the focused manifest change that applies the existing Caps Lock to Escape setting durably on
macOS.


## Intent

Keep the existing Linux keyboard configuration and add a macOS `hidutil` mapping for Caps Lock to Escape. macOS now
uses the repository's LaunchAgent machinery so the mapping is reapplied at login instead of being a one-shot setting.


## Changes

- Marked the existing `capslock-to-escape` setting as Linux-only and retained its original Linux check.
- Removed the Darwin setting script and made the setting explicitly Linux-only so the check does not run on macOS.
- Added a Darwin-only `com.dusktreader.capslock-to-escape` LaunchAgent service using `/usr/bin/hidutil property --set`
  with the standard keyboard HID usages.
- Added a service-level `keep_alive` option so this one-shot mapping command runs at login without being respawned
  indefinitely.
- Kept the service out of Linux configuration and avoided marking it `gui_only`, because the installer cannot reliably
  infer a native macOS GUI session from `DISPLAY` or `WAYLAND_DISPLAY`.
- Updated the manifest and installer tests to cover the separate platform-specific paths.


## Verification

Ran the focused manifest tests and lint:

```shell
uv run pytest tests/test_install.py -k capslock --no-cov
uv run ruff check tests/test_install.py
```

Both commands passed. The `hidutil` setter and `launchctl` were not run against the host. The mapping check is runtime
state and is evaluated only when `dt configure` runs on macOS; service registration is handled by `_install_services()`.

Ran the focused service tests and lint:

```shell
uv run pytest tests/test_configure.py -k install_services --no-cov
uv run ruff check tests/test_configure.py
```

Both commands passed. The service test invoked mocked `launchctl` calls only; no real `hidutil` or `launchctl` command
was run.

Ran the platform-specific settings test and lint:

```shell
uv run pytest tests/test_configure.py -k 'service_specs or install_services or apply_settings' --no-cov
uv run ruff check tests/test_configure.py
```

Both commands passed. The Linux-only setting was verified to be skipped on macOS without invoking its check command.
