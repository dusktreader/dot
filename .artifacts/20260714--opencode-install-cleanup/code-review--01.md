# Code Review: Clean OpenCode dependency installation

**Iteration 01**


## Source

- `.gitignore`
- `etc/install.yaml`
- `src/dot_tools/configure.py`
- `tests/test_configure.py`
- `.config/opencode/plugins/ghostty-tab-indicator.js`
- `.config/opencode/plugins/staleness-guard.ts`
- `.config/opencode/agents/architect-planner.md`
- `.config/opencode/agents/engineer-executor.md`
- `.config/opencode/agents/engineer-investigator.md`
- `.config/opencode/agents/engineer-planner.md`
- `.config/opencode/agents/engineer-task-planner.md`
- `.config/opencode/agents/principal.md`
- `.agents/tools/markdown-format.py`


## Verification Evidence

Initial run (before S01/S02/T01 resolutions applied):

```text
Tests (focused):  uv run pytest tests/test_configure.py → 49 passed, 0 failed
Tests (full):     uv run pytest                         → 169 passed, 0 failed, 73% coverage (threshold: 70%)
Linter:           uv run ruff check src tests           → 0 errors, 0 warnings
Type checker:     uv run ty check src                   → 0 errors
Markdown:         skipped — pre-existing violations in .agents/ and .config/opencode/agents/ prevent a clean run;
                  no Markdown files introduced by this task are themselves malformed
```

Re-review run (after S01/S02/T01 resolutions applied):

```text
Tests (full):     uv run pytest                         → 170 passed, 0 failed, 74% coverage (threshold: 70%)
Linter:           uv run ruff check src tests           → 0 errors, 0 warnings
Type checker:     uv run ty check src                   → 0 errors
```

Test count increased from 169 to 170; the new test covering the `_apply_settings` `HOME`
environment variable (S01 resolution) is included and passing.


## Issue Summary

- **Critical**:    0
- **Significant**: 2
- **Trivial**:     3


## Findings

### Summary

| Finding | Title                                                                                                               | Outcome    |
| ------- | ------------------------------------------------------------------------------------------------------------------- | ---------- |
| S01     | Tool check subprocess does not use `install_env` in settings path                                                   | ✓ Resolved |
| S02     | `staleness-guard.ts` reads `output.args` instead of `input.args`                                                    | ✓ Resolved |
| T01     | `.gitignore` entries are not grouped with related ignore rules                                                      | ✓ Resolved |
| T02     | `test_install_tools__uses_override_home_for_opencode_npm_check` accesses `call_args` positional args via `.args[0]` | Deferred   |
| T03     | `ghostty-tab-indicator.js` plugin signature accepts `{ directory }` but the Plugin API shape is unverified          | Deferred   |


### Significant

#### S01: `_apply_settings` check subprocess does not receive `install_env`


#### Where

`src/dot_tools/configure.py:353-357`


#### Issue

`_install_tools` was updated to pass `install_env` (which now includes `HOME`) to both the
check `subprocess.run` call and the install `subprocess.Popen` call. The parallel
`_apply_settings` method runs its check at line 353 without any `env=` argument, so settings
checks inherit the process environment unchanged rather than the installer's `home`-aware
environment. While settings do not currently use `$HOME` in their check strings, the
asymmetry is a latent bug: a future setting that does use `$HOME` will silently resolve
against the real user home even when `--override-home` is in effect.


#### Impact

Isolated `dt configure --override-home` runs are not fully isolated for settings. Any setting
check or script that references `$HOME` will resolve against the real home, not the override,
producing incorrect behavior in tests or CI that rely on full isolation.


#### Fix

Build and pass `install_env` (or a parallel `settings_env`) in `_apply_settings`, mirroring
the pattern introduced in `_install_tools`. Add an analogous test asserting that the settings
check subprocess receives the correct `HOME`.


#### Outcome

✓ Resolved. `_apply_settings` now builds its own `install_env` (lines 349–352) containing
`PYTHON_VERSION`, `DOT_ROOT`, and `HOME`, and passes it to both the check `subprocess.run`
at line 358 and the install `subprocess.Popen` at line 389. A new test covering the settings
check environment was added and passes (170 total, up from 169).

----

#### S02: `staleness-guard.ts` reads `output.args` instead of `input.args` in `tool.execute.before`


#### Where

`.config/opencode/plugins/staleness-guard.ts:49`


#### Issue

The `tool.execute.before` hook signature is `(input, output)`. At line 49, `extractPaths` is
called with `output.args` rather than `input.args`. The `output` parameter in a `before` hook
is not yet populated — it represents the hook's own output channel, not the tool's resolved
arguments. The correct source of the tool's argument payload is `input.args`, which is already
used correctly in the `tool.execute.after` hook at line 38.


#### Impact

In a `before` hook the `output` argument carries no `args` property, so `output.args` will be
`undefined`. `extractPaths` receives `undefined` instead of the tool's arguments and always
returns an empty path list, silently disabling the staleness check for `edit`, `write`, and
`apply_patch`. The plugin appears to load and run without error but provides no actual
protection.


#### Fix

Replace `output.args` with `input.args` at line 49:

```typescript
const paths = extractPaths(input.tool, input.args)
```


#### Outcome

✓ Resolved. `staleness-guard.ts:49` now reads `input.args` — confirmed at line 49 of the
current file. The `tool.execute.before` hook correctly passes the tool's argument payload to
`extractPaths`, restoring the staleness-check protection for `edit`, `write`, and
`apply_patch`.

----

### Trivial

#### T01: New `.gitignore` entries are not co-located with related rules


#### Where

`.gitignore:2-3`


#### Issue

The two new entries (`.config/opencode/node_modules/` and `.config/opencode/package-lock.json`)
are inserted at the very top of the file, in the middle of the machine-local ignore block
(`.agents/instructions/local.md`, `.agents/instructions/work.md`, etc.) rather than with
other npm/packaging rules lower in the file.


#### Fix

Move the two lines to the npm-artifacts section or add a clearly labelled `# opencode local
artifacts` block at the top with the other machine-local entries, so the grouping intent is
clear to future readers.


#### Outcome

✓ Resolved. The entries are now placed in their own labelled block (`# OpenCode local npm
artifacts`, `.gitignore:7–9`), immediately after the machine-local ignore entries and before
the general Python boilerplate. The grouping intent is explicit.

----

#### T02: Test accesses `call_args.args[0]` — fragile positional extraction


#### Where

`tests/test_configure.py:630-631`


#### Issue

`test_install_tools__uses_override_home_for_opencode_npm_check` extracts the subprocess
command via `mock_run.call_args.args[0]`. `call_args.args` is the tuple of positional
arguments to the mock call; the command is passed as a positional `[0]` today, but if the
production call ever switches to a keyword argument the assertion silently passes with an
empty tuple or raises an `IndexError`. The companion install test (line 658) uses the same
pattern.


#### Fix

Use `mock_run.call_args[0][0]` (identical to the current form but intentionally explicit), or
prefer the more stable `mock_run.call_args.args[0]` with a guard, or restructure the assertion
to use `assert mock_run.call_args == call(...)` for full argument verification.

This is a style issue rather than a correctness failure given the current codebase; no change
is required before merge.


#### Outcome

Deferred — no change made. Acceptable given the style-only nature of the issue.

----

#### T03: `ghostty-tab-indicator.js` plugin signature is undocumented and untyped


#### Where

`.config/opencode/plugins/ghostty-tab-indicator.js:1`


#### Issue

The plugin factory accepts `{ directory }` as a destructured argument, but the file has no
type annotation, no import from `@opencode-ai/plugin`, and no comment explaining the expected
shape. The `staleness-guard.ts` counterpart uses a typed `Plugin` import and documents its
contract. The tab indicator is a small, low-risk plugin, but the asymmetry makes the contract
implicit.


#### Fix

Add a one-line JSDoc comment or a type annotation (or convert to TypeScript) so the expected
argument shape is explicit. This is a documentation concern only.


#### Outcome

Deferred — no change made. Acceptable given the documentation-only nature of the issue.

----

## Skills Applied

- `review-code`: global fallback


## Decision

**APPROVED**

All significant findings are resolved:

- S01 ✓: `_apply_settings` now builds and passes `install_env` (including `HOME`) to both
  its check and install subprocesses, matching the pattern in `_install_tools`. A new test
  confirms the behavior; the full suite passes at 170 tests, 74% coverage.
- S02 ✓: `staleness-guard.ts:49` now correctly reads `input.args`, restoring staleness
  protection for all edit-class tools.
- T01 ✓: The `.gitignore` entries are grouped under a labelled `# OpenCode local npm
  artifacts` block, making the intent clear.

Trivial findings T02 and T03 are deferred; neither affects correctness or safety. All quality
gates pass: 170 tests, Ruff clean, `ty check` clean, coverage at 74% (threshold 70%).
