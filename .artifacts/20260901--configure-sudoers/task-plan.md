# Task plan: Configure passwordless sudo safely

This plan replaces the installer’s unsafe username-based sudo setup with a standalone, validated sudoers configurator
and
isolated coverage for its platform, privilege, parsing, and rollback behavior.


## Goal

Implement `tools/configure-sudoers.py` as the single passwordless-sudo implementation, expose it through the `settings`
section of `etc/install.yaml`, and remove the legacy block from `install.sh`. Preserve unrelated sudoers content and
drop-ins while safely managing `/etc/sudoers.d/90-dotfiles` on Darwin and Linux. Add temporary-fixture tests that never
touch live `/etc/sudoers`; do not run live-system configuration or change unrelated installer behavior.


## Project commands

### Run sudoers tests

Command:

```shell
uv run pytest tests/test_install.py --no-cov
```

Expected output:

All sudoers fixture tests pass, including the command-execution, validation, restoration, platform, identity, parsing,
and idempotence cases.


### Check the shell installer

Command:

```shell
bash -n install.sh
```

Expected output:

The command exits zero and reports no shell syntax errors.


### Run Ruff

Command:

```shell
uv run ruff check src tests
```

Expected output:

Ruff exits zero with no diagnostics for the existing Python package and the new tests.


### Run focused sudoers tests during development

Command:

```shell
uv run pytest tests/test_install.py --no-cov -k sudo
```

Expected output:

The selected sudoers tests pass without invoking a live sudoers command or writing outside the temporary fixture tree.


## Project standards

- [Task requirements](../../../sudoers-prompt.md)
- [Repository guide](../../../.dot_agents/dot.md)
- [Repository agent instructions](../../../AGENTS.md)
- [Python project configuration](../../../pyproject.toml)
- [Test conventions](../../../tests/test_configure.py)


## Steps

1. Add `tests/test_install.py` with temporary fixture trees representing `/etc/sudoers`, `/etc/sudoers.d`, and
   `90-dotfiles`; load or execute a copied standalone script so fixture paths and identities remain test-only seams.
2. Build an argument-aware mocked command runner in the test harness that records exact `sudo`, `visudo`, and related
   invocations, returns configured failures for candidate and final validation, and never executes against the host.
3. Write failing tests for the script contract: the uv shebang, inline PEP 723 metadata, `--check` non-modification,
   Darwin/Linux support, clear rejection of other systems, invoking identity from `SUDO_UID`/`SUDO_USER` or current UID,
   automatic noninteractive sudo re-exec, and clear failure when sudo or visudo is unavailable or authentication fails.
4. Write failing fixture tests for include parsing and preservation: create Linux `#includedir` and Darwin `@includedir`
   entries, accept active `/etc` and macOS `/private/etc` spellings, allow trailing comments, ignore ordinary comments
   and
   unrelated paths, collapse duplicate active target includes, add one canonical include when absent, and preserve every
   unrelated line and drop-in byte-for-byte.
5. Write failing fixture tests for managed-file safety and content: create a missing include directory safely, reject
   directory and drop-in symlinks plus unsafe ownership, modes, types, or main-file symlinks, write the fixed safe
   filename
   `90-dotfiles`, and assert the exact rule for usernames containing `.`.
6. Write failing fixture tests for validation and transaction behavior: reject invalid existing sudoers, validate the
   generated drop-in and complete candidate with noninteractive `visudo`, install through same-directory temporary files
   and atomic replacement, preserve safe main-file metadata and directory mode, restore managed files after write or
   final
   validation failure, leave unrelated drop-ins untouched, and keep a correct rerun’s inode and mtime unchanged.
7. Implement `tools/configure-sudoers.py` with standard-library-only code, the uv shebang and PEP 723 metadata, explicit
   Darwin/Linux checks, OS-backed identity resolution, bounded/noninteractive sudo re-exec, active-include parsing, safe
   root-owned path checks, candidate validation, atomic installation, final validation, and restoration.
8. Add the `passwordless sudo` setting to `etc/install.yaml` with the quoted `$DOT_ROOT` `--check` command and generic
   execution command, relying on `DotInstaller._apply_settings` and retaining ordinary package-install `sudo` usage in
   `install.sh`.
9. Remove only the legacy passwordless-sudo block from `install.sh`, then run the focused tests and fix implementation
   or
   harness defects until all cases pass without live-system access.
10. Run the required verification commands, record changed files, sudoers design, test coverage, exact results, and any
    unrelated pre-existing failures in the task journal, and leave the worktree uncommitted.


## Acceptance criteria

1. **AC01**: `tools/configure-sudoers.py` starts with `#!/usr/bin/env -S uv run --script` and contains valid inline PEP
   723 metadata while using no unnecessary non-stdlib dependency.
2. **AC02**: The manifest has one `passwordless sudo` entry under `settings` whose commands quote `$DOT_ROOT`, and
   `install.sh` contains no legacy passwordless-sudo block or username-derived sudoers write.
3. **AC03**: Normal execution supports only Darwin and Linux, resolves the invoking account without trusting `USER`,
   re-execs through noninteractive `sudo` when needed, and returns a clear nonzero error on unsupported platforms,
   unavailable tools, or failed authentication.
4. **AC04**: `--check` exits zero only for the active desired configuration and performs no file modification; normal
   execution recognizes, deduplicates, or creates exactly one active target include while preserving unrelated content.
5. **AC05**: The managed rule is exactly `<username> ALL=(ALL) NOPASSWD: ALL` in fixed root-owned mode `0440` file
   `/etc/sudoers.d/90-dotfiles`; unsafe symlinks, types, ownership, or permissions are rejected rather than overwritten.
6. **AC06**: The implementation validates existing and candidate sudoers configurations with noninteractive `visudo`,
   uses same-directory temporary files and atomic replacement, preserves safe metadata, restores managed files after
   failure, and never uses `sudo tee` against a live sudoers file.
7. **AC07**: Temporary-fixture tests cover all required Linux, Darwin, include, identity, safety, validation, failure,
   restoration, unsupported-platform, idempotence, and preservation cases, with mocked argument-aware commands and no
   writes to live `/etc/sudoers`.
8. **AC08**: `bash -n install.sh`, `uv run pytest tests/test_install.py --no-cov`, and `uv run ruff check src tests` all
   exit zero, and the task journal contains the required implementation and verification record.
