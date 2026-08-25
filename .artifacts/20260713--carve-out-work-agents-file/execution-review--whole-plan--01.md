# Execution Review: Carve work-specific configuration into private work-dot repository

## Source Artifacts

- **Implementation journal**: `.artifacts/20260713--carve-out-work-agents-file/implementation-journal.md`
- **Implementation plan**: `.artifacts/20260713--carve-out-work-agents-file/implementation-plan.md`


## Scope

**whole-plan** — Iteration 01


## Issue Summary

- **Critical**:    2
- **Significant**: 3
- **Trivial**:     2


## Verification Evidence

```text
dot tests:        uv run pytest  →  161 passed, 0 failed  (coverage 71.18%, floor 70% ✓)
work-dot tests:   uv run pytest  →   24 passed, 0 failed  (coverage 72.40%, floor 70% ✓)

dot ruff:         uv run ruff check src tests  →  All checks passed
work-dot ruff:    uv run ruff check src tests  →  All checks passed

dot ty:           uv run ty check src  →  5 diagnostics (2 errors: see findings C01 and S01 below)
work-dot ty:      uv run ty check      →  3 warnings only (unknown-rule entries in pyproject.toml; no errors)
```

**Known claimed state**: Executor asserted both `ty` checks fail from pre-existing / project-wide
diagnostics, with no new creds/settings typing errors. That claim is **partially confirmed**:
work-dot's `ty` output contains only three `unknown-rule` warnings introduced by the copied
`pyproject.toml`, not errors. Dot's `ty check src` surfaces two errors — one pre-existing
(`settings.py:18` `invalid-assignment` on `JiraInfo.base_url`) and one new (`cli/git.py:49`
`unresolved-attribute` referencing `settings.jira_info`, which no longer exists on `Settings`
after this implementation removed inline fields). The second error is new code introduced by this
plan (settings migration). See C01.


## Acceptance Criteria Verification

| Task/AC | Status | Evidence                                                                                                                                                                                                                                                                                                                                              |
| ------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 01/AC01 | ✓      | `/Users/tucker.beck/src/mhe/work-dot/.git` exists                                                                                                                                                                                                                                                                                                     |
| 01/AC02 | ✓      | `git log main --oneline` shows exactly one commit                                                                                                                                                                                                                                                                                                     |
| 01/AC03 | ✓      | Commit message `Initial Commit` confirmed                                                                                                                                                                                                                                                                                                             |
| 01/AC04 | ✓      | README.md with `# work-dot\n` confirmed                                                                                                                                                                                                                                                                                                               |
| 01/AC05 | ✓      | Branch `feat/NO-TICKET--bootstrap-work-dot` branched from Initial Commit                                                                                                                                                                                                                                                                              |
| 01/AC06 | ✓      | Full scaffolding on feature branch; `src/work_tools/`, `tests/`, `etc/install.yaml` present                                                                                                                                                                                                                                                           |
| 01/AC07 | ✓      | `pyproject.toml` defines `wdt = "work_tools.cli.main:cli"`                                                                                                                                                                                                                                                                                            |
| 01/AC08 | ✓      | Structure matches dot layout                                                                                                                                                                                                                                                                                                                          |
| 01/AC09 | ✓      | `.gitignore` excludes `__pycache__`, `.venv`, credential files                                                                                                                                                                                                                                                                                        |
| 01/AC10 | ✓      | Python ≥3.13, same dev deps, `typerdrive>=0.9.8` confirmed in pyproject.toml                                                                                                                                                                                                                                                                          |
| 01/AC11 | ✓      | `.git/config` remote.origin → `https://github.com/Tucker-Beck_mcgraw/work-dot`                                                                                                                                                                                                                                                                        |
| 01/AC12 | ✓      | Scaffolding committed; branch name recorded in journal                                                                                                                                                                                                                                                                                                |
| 01/AC13 | ✓      | main has only Initial Commit                                                                                                                                                                                                                                                                                                                          |
| 02/AC01 | ✓      | `work_tools/cli/main.py` exports `cli` Typer app                                                                                                                                                                                                                                                                                                      |
| 02/AC02 | ✓      | `wdt --help` lists `configure`, `creds`, `settings`, `logs`                                                                                                                                                                                                                                                                                           |
| 02/AC03 | ✓      | Help describes it as work-layer bootstrap CLI                                                                                                                                                                                                                                                                                                         |
| 02/AC04 | ✓      | `configure` accepts `--root`, `--override-home`, `--force`                                                                                                                                                                                                                                                                                            |
| 02/AC05 | ✓      | `creds` group registered; shows `fetch`, `set`                                                                                                                                                                                                                                                                                                        |
| 02/AC06 | ✓      | `fetch --help` shows `<key>` arg and stdout disclosure                                                                                                                                                                                                                                                                                                |
| 02/AC07 | ✓      | Import succeeds; Typer-based confirmed                                                                                                                                                                                                                                                                                                                |
| 02/AC08 | ✓      | `add_settings_subcommand`, `add_logs_subcommand` applied in `main.py:22-23`                                                                                                                                                                                                                                                                           |
| 03/AC01 | ✓      | `work_tools/configure.py` exports `WorkInstaller`                                                                                                                                                                                                                                                                                                     |
| 03/AC02 | ✓      | `__init__` accepts `root`, `override_home`, `force`; `configure.py:42`                                                                                                                                                                                                                                                                                |
| 03/AC03 | ✓      | `install_work()` at `configure.py:214` runs full sequence                                                                                                                                                                                                                                                                                             |
| 03/AC04 | ✓      | `etc/install.yaml` defines all required sections                                                                                                                                                                                                                                                                                                      |
| 03/AC05 | ✓      | `_make_dirs` creates `mkdir_paths` entries; `test_work_installer_make_dirs`                                                                                                                                                                                                                                                                           |
| 03/AC06 | ✓      | `_make_links` scoped to work paths; `configure.py:69-107`                                                                                                                                                                                                                                                                                             |
| 03/AC07 | ✓      | `_update_dotfiles` appends to `~/.extra_dotfiles`; `configure.py:149-171`                                                                                                                                                                                                                                                                             |
| 03/AC08 | ✓      | `WorkInstaller` never writes dot-owned paths by design                                                                                                                                                                                                                                                                                                |
| 03/AC09 | ✓      | `test_work_installer_install_work` passes                                                                                                                                                                                                                                                                                                             |
| 03/AC10 | ✓      | Idempotency confirmed in `_make_links` and `_copy_files` duplicate detection                                                                                                                                                                                                                                                                          |
| 04/AC01 | ✓      | `work_tools/settings.py` exports `WorkSettings`                                                                                                                                                                                                                                                                                                       |
| 04/AC02 | ⚠      | Nested `credentials: WorkCredentialsModel` present; but plan AC02 lists `jira_api_key`, `confluence_token`, `datadog_api_key` — implementation uses `atlassian_pat` and `datadog_api_key` instead. This is an intentional post-research schema change (consolidated Jira+Confluence into one PAT); not a defect, but diverges from plan literal text. |
| 04/AC03 | ✓      | `creds fetch` looks up key in `settings.credentials` only; `creds.py:52-57`                                                                                                                                                                                                                                                                           |
| 04/AC04 | ✓      | Missing key → exit 1; `creds.py:54-55`                                                                                                                                                                                                                                                                                                                |
| 04/AC05 | ✓      | Empty/placeholder → exit 1; `creds.py:60-62`                                                                                                                                                                                                                                                                                                          |
| 04/AC06 | ✓      | Unknown key → exit 1, settings unchanged; `creds.py:101-103`                                                                                                                                                                                                                                                                                          |
| 04/AC07 | ✓      | Non-revealing acknowledgement printed; value not echoed; `creds.py:116`                                                                                                                                                                                                                                                                               |
| 04/AC08 | ✓      | Bare `wdt creds` → help + exit 0; `invoke_without_command=True`, callback `creds.py:24-34`                                                                                                                                                                                                                                                            |
| 04/AC09 | ✓      | `test_creds_help_matches_bare_invocation` passes                                                                                                                                                                                                                                                                                                      |
| 04/AC10 | ✓      | `wdt settings view` provided by Typerdrive via `add_settings_subcommand`                                                                                                                                                                                                                                                                              |
| 04/AC11 | ✓      | Typerdrive research documented in journal §Key Findings                                                                                                                                                                                                                                                                                               |
| 04/AC12 | ✓      | Separate SettingsManager instances; separate config dirs by app name                                                                                                                                                                                                                                                                                  |
| 04/AC13 | ✓      | `work_tools/cli/creds.py` registered in `main.py:24`                                                                                                                                                                                                                                                                                                  |
| 04/AC14 | ✓      | Fetch help docstring includes WARNING disclosure; `creds.py:43-47`                                                                                                                                                                                                                                                                                    |
| 04/AC15 | ✓      | Set help docstring includes non-echo disclosure; `creds.py:83-88`                                                                                                                                                                                                                                                                                     |
| 04/AC16 | ✓      | `test_creds_fetch_*` tests cover all cases                                                                                                                                                                                                                                                                                                            |
| 04/AC17 | ✓      | `test_creds_set_*` tests cover write, unknown key, byte-identical implicitly via isolation                                                                                                                                                                                                                                                            |
| 04/AC18 | ✓      | `test_creds_bare_invocation_*` tests pass                                                                                                                                                                                                                                                                                                             |
| 04/AC19 | ✓      | Separate SettingsManager instances isolate stores                                                                                                                                                                                                                                                                                                     |
| 04/AC20 | ✓      | `temp_home` fixture via `monkeypatch.setenv("HOME", ...)`                                                                                                                                                                                                                                                                                             |
| 05/AC01 | ✓      | `dot_tools/cli/creds.py` exports `cli` Typer group                                                                                                                                                                                                                                                                                                    |
| 05/AC02 | ✓      | `dt creds fetch` scoped to `Settings.credentials`                                                                                                                                                                                                                                                                                                     |
| 05/AC03 | ✓      | Missing key → exit 1; `creds.py:54-55` (dot)                                                                                                                                                                                                                                                                                                          |
| 05/AC04 | ✓      | Empty/placeholder → exit 1; `creds.py:60-62` (dot)                                                                                                                                                                                                                                                                                                    |
| 05/AC05 | ✓      | Fetch help includes WARNING; `creds.py:43-47` (dot)                                                                                                                                                                                                                                                                                                   |
| 05/AC06 | ✓      | Unknown key → exit 1, settings unchanged; `creds.py:101-103` (dot)                                                                                                                                                                                                                                                                                    |
| 05/AC07 | ✓      | Non-revealing acknowledgement; `creds.py:116` (dot)                                                                                                                                                                                                                                                                                                   |
| 05/AC08 | ✓      | Set help includes non-echo disclosure; `creds.py:83-88` (dot)                                                                                                                                                                                                                                                                                         |
| 05/AC09 | ✓      | `creds_cli` registered in `main.py:35`                                                                                                                                                                                                                                                                                                                |
| 05/AC10 | ✓      | `SettingsManager(Settings)` never touches WorkSettings                                                                                                                                                                                                                                                                                                |
| 05/AC11 | ✓      | Bare `dt creds` → help + exit 0                                                                                                                                                                                                                                                                                                                       |
| 05/AC12 | ✓      | `test_creds_help_matches_bare_invocation` (dot) passes                                                                                                                                                                                                                                                                                                |
| 05/AC13 | ✓      | 9 passing test cases in `test_cli_creds.py` (dot)                                                                                                                                                                                                                                                                                                     |
| 05/AC14 | ✓      | `test_creds_set_invalid_key` covers unknown-key; value not echoed test present                                                                                                                                                                                                                                                                        |
| 05/AC15 | ✓      | Bare invocation tests pass                                                                                                                                                                                                                                                                                                                            |
| 05/AC16 | ⚠      | Store isolation test not explicitly present in `test_cli_creds.py` (dot) — no test verifies work store byte-identical after `dt creds set`. Gap against AC16.                                                                                                                                                                                         |
| 05/AC17 | ✓      | `temp_home` fixture via monkeypatch                                                                                                                                                                                                                                                                                                                   |
| 05/AC18 | ✓      | Manual verification consistent with test results                                                                                                                                                                                                                                                                                                      |
| 06/AC01 | ✓      | `_seed_credentials` called from `install_work`; `configure.py:173-212` (wdt)                                                                                                                                                                                                                                                                          |
| 06/AC02 | ✓      | Empty fields seeded with `PLACEHOLDER_<FIELD>`                                                                                                                                                                                                                                                                                                        |
| 06/AC03 | ✓      | Existing non-placeholder values preserved (value check before seeding)                                                                                                                                                                                                                                                                                |
| 06/AC04 | ✓      | Notices printed to stderr for each seeded key                                                                                                                                                                                                                                                                                                         |
| 06/AC05 | ⚠      | Notice format is `Credential '<key>' is not set. Configure via: wdt creds set <key> <value>` — does not include `[work]` prefix specified in plan AC05. Minor deviation.                                                                                                                                                                              |
| 06/AC06 | ✓      | `install_work()` exits zero despite notices                                                                                                                                                                                                                                                                                                           |
| 06/AC07 | ✓      | Non-interactive; no input() calls                                                                                                                                                                                                                                                                                                                     |
| 06/AC08 | ✓      | Seeding tested in `test_work_installer_install_work`                                                                                                                                                                                                                                                                                                  |
| 06/AC09 | ✓      | Live run confirmed by executor                                                                                                                                                                                                                                                                                                                        |
| 07/AC01 | ✓      | `shutil.which("wdt")` called after installer runs; `main.py:110` (dot)                                                                                                                                                                                                                                                                                |
| 07/AC02 | ✓      | `wdt` absent → no output, exit 0                                                                                                                                                                                                                                                                                                                      |
| 07/AC03 | ✓      | `--override-home` and `--force` forwarded; `main.py:113-117`                                                                                                                                                                                                                                                                                          |
| 07/AC04 | ✓      | `override_home` forwarded when present                                                                                                                                                                                                                                                                                                                |
| 07/AC05 | ✓      | `override_home` not added when None                                                                                                                                                                                                                                                                                                                   |
| 07/AC06 | ✓      | Confirmed by `result.returncode` check                                                                                                                                                                                                                                                                                                                |
| 07/AC07 | ✗      | Output prefixing **removed** in current working-tree diff — committed code used `capture_output=True` with line-by-line `[work]` prefix; working tree now calls `subprocess.run(wdt_cmd)` with no capture or prefix. Plan AC07 and AC08 are violated in working tree. See C02.                                                                        |
| 07/AC08 | ✗      | Same as AC07 — per-line `[work]` prefix removed.                                                                                                                                                                                                                                                                                                      |
| 07/AC09 | ⚠      | `test_configure.py` (dot) has no new tests mocking `shutil.which` for wdt detection. Plan-specified test names (`test_configure_wdt_absent_silent`, etc.) absent.                                                                                                                                                                                     |
| 07/AC10 | ⚠      | Argument passing not unit-tested; relies only on code review                                                                                                                                                                                                                                                                                          |
| 07/AC11 | ⚠      | No integration tests for wdt detection in dot's test suite                                                                                                                                                                                                                                                                                            |
| 08/AC01 | ✓      | `Tucker-Beck_mcgraw` not present in dot source/config (removed GHES `insteadOf`)                                                                                                                                                                                                                                                                      |
| 08/AC02 | ✓      | `github.mheducation.com` `insteadOf` rule removed from `.gitconfig`                                                                                                                                                                                                                                                                                   |
| 08/AC03 | ✓      | `cdwork` alias and `~/src/mhe/` hardcoded paths removed/absent from dot shell files                                                                                                                                                                                                                                                                   |
| 08/AC04 | ✓      | `jira_tools.py` no longer has hardcoded work tenant; JiraInfo retained as generic                                                                                                                                                                                                                                                                     |
| 08/AC05 | ✓      | Work-specific agent guidance removed from `dot/.agents/instructions/`                                                                                                                                                                                                                                                                                 |
| 08/AC06 | ✓      | No `credentials.json` references remain in dot source, tests, or agent instructions                                                                                                                                                                                                                                                                   |
| 08/AC07 | ✓      | `.gitconfig` no longer references GHES; conditional include for `.gitconfig.work` present                                                                                                                                                                                                                                                             |
| 08/AC08 | ✓      | Committed on refactor branch                                                                                                                                                                                                                                                                                                                          |
| 08/AC09 | ✓      | No MHE-specific embedded content in dot source                                                                                                                                                                                                                                                                                                        |
| 08/AC10 | ✓      | Not pushed; committed locally on feature branch                                                                                                                                                                                                                                                                                                       |
| 09/AC01 | ✓      | `[includeIf "gitdir:~/src/mhe/"]` present in `.gitconfig:37`                                                                                                                                                                                                                                                                                          |
| 09/AC02 | ✓      | Path `~/.gitconfig.work` confirmed                                                                                                                                                                                                                                                                                                                    |
| 09/AC03 | ✓      | File is installed by `wdt configure`; not in dot                                                                                                                                                                                                                                                                                                      |
| 09/AC04 | ✓      | Git silently ignores missing `includeIf` targets                                                                                                                                                                                                                                                                                                      |
| 09/AC05 | ✓      | Comment added above block in `.gitconfig`                                                                                                                                                                                                                                                                                                             |
| 10/AC01 | ✓      | `work-dot/.workrc` exports `MHE_ROOT`                                                                                                                                                                                                                                                                                                                 |
| 10/AC02 | ✓      | `cdwork` alias defined                                                                                                                                                                                                                                                                                                                                |
| 10/AC03 | ✓      | File sources without errors                                                                                                                                                                                                                                                                                                                           |
| 10/AC04 | ✓      | `work-dot/.gitconfig.work` exists with `[user]` section                                                                                                                                                                                                                                                                                               |
| 10/AC05 | ✓      | Work email `tucker.beck@mheducation.com` present                                                                                                                                                                                                                                                                                                      |
| 10/AC06 | ✓      | Git identity applies inside `~/src/mhe/` via conditional include                                                                                                                                                                                                                                                                                      |
| 10/AC07 | ✓      | Both files listed in `etc/install.yaml` under `link_paths`                                                                                                                                                                                                                                                                                            |
| 10/AC08 | ✓      | `wdt configure` creates symlinks for both files                                                                                                                                                                                                                                                                                                       |
| 10/AC09 | ✓      | Sourcing `.workrc` sets `MHE_ROOT` and `cdwork`                                                                                                                                                                                                                                                                                                       |
| 11/AC01 | ✓      | `work-dot/.agents/instructions/work.md` exists, 125 lines                                                                                                                                                                                                                                                                                             |
| 11/AC02 | ✓      | Atlassian URL, Datadog account, service endpoints documented                                                                                                                                                                                                                                                                                          |
| 11/AC03 | ✓      | `wdt creds fetch <key>` documented with examples                                                                                                                                                                                                                                                                                                      |
| 11/AC04 | ✓      | `etc/install.yaml` has `link_paths: [".agents/instructions/work.md"]`; `_make_dirs` creates `~/.agents/instructions/`                                                                                                                                                                                                                                 |
| 11/AC05 | ✓      | Filename `work.md` clearly work-specific                                                                                                                                                                                                                                                                                                              |
| 11/AC06 | ✓      | File is symlinked; agent sessions will read it                                                                                                                                                                                                                                                                                                        |
| 12/AC01 | ✓      | dot coverage 71.18% ≥ 70%                                                                                                                                                                                                                                                                                                                             |
| 12/AC02 | ✓      | work-dot coverage 72.40% ≥ 70%                                                                                                                                                                                                                                                                                                                        |
| 12/AC03 | ✓      | All tests pass in both repos                                                                                                                                                                                                                                                                                                                          |
| 12/AC04 | ⚠      | Integration tests for `dt configure` with wdt present/absent not written (see AC09-11 in Task 07)                                                                                                                                                                                                                                                     |
| 12/AC05 | ✓      | All tests use temp directories / monkeypatched HOME                                                                                                                                                                                                                                                                                                   |
| 12/AC06 | ✓      | New tests clearly identifiable by name                                                                                                                                                                                                                                                                                                                |
| 13/AC01 | ✓      | `dot/.dot_agents/CREDENTIAL_MIGRATION.md` created (174 lines)                                                                                                                                                                                                                                                                                         |
| 13/AC02 | ✓      | Step-by-step migration sequence documented                                                                                                                                                                                                                                                                                                            |
| 13/AC03 | ✓      | Exact commands provided                                                                                                                                                                                                                                                                                                                               |
| 13/AC04 | ✓      | Rollback procedure documented                                                                                                                                                                                                                                                                                                                         |
| 13/AC05 | ✓      | Fully manual with success criteria at each step                                                                                                                                                                                                                                                                                                       |
| 14/AC01 | ✓      | No `credentials.json` references in agent instructions                                                                                                                                                                                                                                                                                                |
| 14/AC02 | ✓      | `about-me.md` updated to reference `dt creds fetch`                                                                                                                                                                                                                                                                                                   |
| 14/AC03 | ✓      | `work.md` documents `wdt creds fetch`                                                                                                                                                                                                                                                                                                                 |
| 14/AC04 | ✓      | No agent guidance directs reading a plaintext file                                                                                                                                                                                                                                                                                                    |
| 14/AC05 | ✓      | `.gitignore` entries reviewed; credential entries clarified                                                                                                                                                                                                                                                                                           |
| 14/AC06 | ✓      | No jq-against-credentials-file scripts remain in dot                                                                                                                                                                                                                                                                                                  |
| 15/AC01 | ✓      | `dot/.dot_agents/VALIDATION.md` created (307 lines)                                                                                                                                                                                                                                                                                                   |
| 15/AC02 | ✓      | Validation designed for scratch/test home                                                                                                                                                                                                                                                                                                             |
| 15/AC03 | ✓      | 10-point checklist covers all required validations                                                                                                                                                                                                                                                                                                    |
| 15/AC04 | ✓      | Both test suites pass                                                                                                                                                                                                                                                                                                                                 |
| 15/AC05 | ⚠      | Multiple uncommitted changes in both repos (see S02 below)                                                                                                                                                                                                                                                                                            |


## Scope Verification

| File                                      | Justified By               | Status                                                                                             |
| ----------------------------------------- | -------------------------- | -------------------------------------------------------------------------------------------------- |
| `work-dot/src/work_tools/settings.py`     | Tasks 01-04                | ✓                                                                                                  |
| `work-dot/src/work_tools/configure.py`    | Tasks 03, 06               | ✓                                                                                                  |
| `work-dot/src/work_tools/cli/creds.py`    | Task 04                    | ✓                                                                                                  |
| `work-dot/src/work_tools/cli/main.py`     | Tasks 02, 04               | ✓                                                                                                  |
| `work-dot/src/work_tools/exceptions.py`   | Task 03                    | ✓                                                                                                  |
| `work-dot/src/work_tools/spinner.py`      | Task 03                    | ✓                                                                                                  |
| `work-dot/src/work_tools/version.py`      | Task 02                    | ✓                                                                                                  |
| `work-dot/.agents/instructions/work.md`   | Task 11                    | ✓                                                                                                  |
| `work-dot/.gitconfig.work`                | Task 10                    | ✓                                                                                                  |
| `work-dot/.workrc`                        | Task 10                    | ✓                                                                                                  |
| `work-dot/etc/install.yaml`               | Tasks 03, 10, 11           | ✓                                                                                                  |
| `work-dot/tests/test_cli_creds.py`        | Task 04                    | ✓                                                                                                  |
| `work-dot/tests/test_configure.py`        | Tasks 03, 11               | ✓                                                                                                  |
| `dot/src/dot_tools/cli/creds.py`          | Task 05                    | ✓                                                                                                  |
| `dot/src/dot_tools/cli/main.py`           | Tasks 05, 07               | ✓                                                                                                  |
| `dot/src/dot_tools/settings.py`           | Task 05                    | ✓                                                                                                  |
| `dot/.gitconfig`                          | Tasks 08, 09               | ✓                                                                                                  |
| `dot/.agents/instructions/about-me.md`    | Task 14                    | ✓                                                                                                  |
| `dot/.dot_agents/CREDENTIAL_MIGRATION.md` | Task 13                    | ✓                                                                                                  |
| `dot/.dot_agents/VALIDATION.md`           | Task 15                    | ✓                                                                                                  |
| `dot/tests/test_cli_creds.py`             | Task 05                    | ✓                                                                                                  |
| `dot/src/dot_tools/jira_tools.py`         | Task 08                    | ✓ — minor cleanup                                                                                  |
| `dot/src/dot_tools/cli/git.py`            | **Unmodified per journal** | ⚠ — pre-existing `settings.jira_info` reference now a type error after Settings migration; see C01 |


## Prior Review Resolution

First iteration — no prior findings to resolve.


## Findings

### Summary

| Finding | Title                                                                 | Outcome |
| ------- | --------------------------------------------------------------------- | ------- |
| C01     | `git.py:49` references removed `Settings.jira_info` — new type error  |         |
| C02     | wdt output prefixing stripped in uncommitted working-tree changes     |         |
| S01     | Large volume of uncommitted implementation changes in both repos      |         |
| S02     | Task 07 `dt configure` wdt-detection tests not written                |         |
| S03     | `creds set` stores raw string into `SecretStr` field without wrapping |         |
| T01     | `configure.py:143` inline `import shutil` inside method body          |         |
| T02     | `work-dot/pyproject.toml` unknown-rule `ty` warnings need cleanup     |         |


---


### Critical

#### C01: `cli/git.py:49` references `Settings.jira_info`, which no longer exists


#### Where

`dot/src/dot_tools/cli/git.py:49`


#### Issue

`settings.jira_info` is referenced at `git.py:49`, but `jira_info` is not a field on
`Settings` after Task 05 restructured the settings model to use only a nested
`CredentialsModel`. `JiraInfo` is still defined in `settings.py` but is no longer
attached to `Settings`. This creates a real runtime crash if `dt git` is ever invoked
with a settings context, and `uv run ty check src` confirms it:

```text
error[unresolved-attribute]: Object of type `Settings` has no attribute `jira_info`
  --> src/dot_tools/cli/git.py:49:28
```

The executor's claim that "both ty checks still fail from pre-existing/project-wide
diagnostics, with no known new creds/settings typing errors" is **incorrect** for this error.
This error was introduced by the settings migration in Task 05.


#### Impact

`dt git` will raise `AttributeError: 'Settings' object has no attribute 'jira_info'` at
runtime the first time `JiraManager` is initialized through the CLI. Functionality broken.


#### Fix

Either re-attach `JiraInfo` to `Settings` as `jira_info: JiraInfo = Field(default_factory=JiraInfo)`,
or update `git.py:49` to derive the jira connection info from `Settings.credentials` fields
instead (whichever reflects the intended architecture post-migration).


#### Outcome


---


#### C02: Output prefixing for wdt subprocess removed in working tree — AC07/AC08 violated


#### Where

`dot/src/dot_tools/cli/main.py:119` (working tree version)


#### Issue

The committed implementation (`configure` in `main.py`) captured `subprocess.run()` output
and prefixed every line with `[work]` on both success and failure, satisfying plan AC07 and
AC08. The current working tree has removed `capture_output=True` and the entire prefixing
logic, leaving a bare `subprocess.run(wdt_cmd)` call that passes stdout/stderr directly
to the terminal with no prefix and no success-path log message.

Specifically:
- AC07 requires prefixing wdt stdout/stderr with `[work]` on failure.
- AC08 requires the prefix on every line of work-layer output.
- The working-tree diff removes both behaviors entirely.

These changes are **not committed**. Whether the commit or the working tree represents
intent is unclear, but the working-tree state would violate two plan ACs if committed as-is.


#### Impact

Failure output from `wdt configure` will not be distinguishable from `dt configure` output.
The plan's observability requirement for multi-layer configuration is lost.


#### Fix

Either restore `capture_output=True` with the line-prefix logic, or confirm the design has
been deliberately relaxed and update the plan ACs with a documented rationale before committing.


#### Outcome


---


### Significant

#### S01: Large volume of uncommitted changes in both repositories


#### Where

`work-dot` working tree: 9 modified tracked files + 3 untracked files
`dot` working tree: 18 modified tracked files + 4 untracked files


#### Issue

AC15/AC05 of Task 15 requires "No uncommitted changes remain; all implementation work is
committed to the appropriate feature branches." Neither repository satisfies this. Notable
uncommitted changes include:

- `work-dot/src/work_tools/settings.py` — schema change from `{jira_api_key, confluence_token, datadog_api_key}` to
  `{atlassian_pat, datadog_api_key}` with `SecretStr` types and a `field_serializer`. This is a substantive design
  change.
- `work-dot/.agents/instructions/work.md` — extensive content revision with accurate Jira/Atlassian documentation.
- `work-dot/tests/test_cli_creds.py` — updated to reflect the schema change (now tests `atlassian_pat`/`datadog_api_key`
  instead of the plan's listed fields).
- `dot/src/dot_tools/cli/main.py` — the prefixing removal discussed in C02.
- Several dot agent instruction files and git config files.

These are not trivial formatting changes; they include schema, behavior, and documentation
substantive additions or revisions.


#### Impact

The repository is not in a reviewable committed state for roughly half the implementation.
Test coverage numbers and AC compliance verified above apply to the **working tree**, not
the committed baseline. If commits revert any of this, findings may shift.


#### Fix

Commit all intended changes to their respective feature branches before final review sign-off.
Separate commits for schema changes, documentation revisions, and the prefixing decision (C02).


#### Outcome


---


#### S02: Task 07 wdt-detection tests absent from dot test suite


#### Where

`dot/tests/test_configure.py`


#### Issue

Plan Task 07 AC09-AC11 and Task 12 AC04 require unit and integration tests for `dt configure`
wdt detection. The named tests (`test_configure_wdt_absent_silent`,
`test_configure_wdt_present_success`, `test_configure_wdt_present_failure`,
`test_configure_passes_override_home_to_wdt`) are not present in `tests/test_configure.py`.
The journal notes Task 07 as "already done in Task 05" but does not address the missing tests.
The `dt configure` wdt invocation path is entirely untested.


#### Impact

Wdt detection, argument forwarding, and error propagation are unverified by automated tests.
Any regression in this path is invisible to the test suite.


#### Fix

Add the four unit tests listed in plan Task 07 Steps 3-4 to `dot/tests/test_configure.py`,
mocking `shutil.which` and `subprocess.run`.


#### Outcome


---


#### S03: `creds set` stores raw string into `SecretStr` field without wrapping


#### Where

`work-dot/src/work_tools/cli/creds.py:108` (also `dot/src/dot_tools/cli/creds.py:108`)


#### Issue

When building `updated_creds_dict`, the code does `updated_creds_dict[key] = value` where
`value` is a plain `str`. The `WorkCredentialsModel` field `atlassian_pat` is typed as
`SecretStr`. Pydantic v2 coerces `str → SecretStr` on model instantiation, so this works
at runtime, but `model_dump()` of the current credentials will serialize `SecretStr` values
as `SecretStr` objects (not strings), and then re-assigning them back via `creds_model(**updated_dict)`
may produce unexpected dict values if the existing field is already a `SecretStr` and `model_dump()`
is called without `mode="json"`.

Specifically: `model_dump()` returns `SecretStr` objects for `SecretStr` fields (not plain
strings), so `updated_creds_dict` will contain `SecretStr(...)` for the unmodified fields
and a raw `str` for the updated field. Pydantic re-wraps both correctly on `creds_model(**...)`,
so this works in practice, but it is fragile and confusing. The `field_serializer` registered
with `when_used="json"` does not apply here.


#### Impact

Currently functional but fragile. A future maintainer adding a custom validator on `SecretStr`
fields could silently break the round-trip. Test `test_creds_set_persists_to_disk` passes, so
the Pydantic coercion is working correctly, but the code intention is not clearly expressed.


#### Fix

Use `model_dump(mode="json")` to get plain string values, then update the key and reconstruct.
Or explicitly wrap the new value: `updated_creds_dict[key] = SecretStr(value)` before
passing to the model constructor.


#### Outcome


---


### Trivial

#### T01: `import shutil` inside method body in `configure.py`


#### Where

`work-dot/src/work_tools/configure.py:143`


#### Issue

`import shutil` appears inside `_copy_files()` rather than at the module top-level. This is
inconsistent with Python convention and the rest of the file (which uses top-level imports).


#### Fix

Move `import shutil` to the top of `configure.py`.


#### Outcome


---


#### T02: `work-dot/pyproject.toml` references unknown `ty` rule names


#### Where

`work-dot/pyproject.toml:63-65`


#### Issue

`uv run ty check` emits three `warning[unknown-rule]` entries for `any-implicit`,
`any-explicit`, and `unused-call-result` in `[tool.ty.rules]`. These rule names are not
recognized by the installed `ty` version. They were likely copied from the `dot` repo
where they may have been experimental. The warnings do not block anything but add noise.


#### Fix

Remove or update the unrecognized rule entries to match the ty version in use.


#### Outcome


---


## Skills Applied

- `review-implementation-execution`


## Decision

**BLOCKED — CHANGES REQUIRED**

Two critical findings must be resolved before approval:

- **C01**: The `settings.jira_info` attribute removal created a new type error and runtime
  crash vector in `cli/git.py`. This is a genuine regression introduced by this plan's
  settings migration. It must be fixed.
- **C02**: The working-tree removal of wdt output prefixing (`[work]` labels) violates plan
  AC07/AC08. This must either be reverted to the committed behavior or the plan ACs must be
  explicitly updated with documented rationale before those changes are committed.

Additionally, **S01** (large volume of uncommitted changes) must be resolved — all intended
implementation changes must be committed before the plan can be considered complete per AC15.

**S02** (missing wdt-detection tests) should be addressed in the same pass.

S03 is a code quality concern that should be fixed before merging but does not block the
implementation from functioning. T01 and T02 are housekeeping items.

Once C01, C02, and S01 are resolved and committed, request re-review (iteration 02).
