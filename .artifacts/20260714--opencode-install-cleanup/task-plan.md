# Task plan: Clean OpenCode dependency installation

Move OpenCode's npm dependency installation from the repository checkout to the OpenCode configuration directory
installed under the target home, while retaining `package.json` as the only linked dependency-management file. Preserve
the existing OpenCode plugin, agent-model, agent-process, and Markdown-validator working-tree changes. Do not change
OpenCode's dependency set, add a lockfile to version control, or link dependency artifacts.


## Goal

Make `dt configure` install and detect `@opencode-ai/plugin` at
`$HOME/.config/opencode` (or the configured `--override-home` location), rather than at `$DOT_ROOT/.config/opencode`.
The install manifest must continue to link `package.json`, agents, tools, plugins, and `AGENTS.md`, but only
`package.json` may represent npm dependency-management content from the repository. `node_modules` and
`package-lock.json` remain local, untracked artifacts at the installed OpenCode location.


## Project commands

### Run focused installer tests

Command:

```shell
uv run pytest tests/test_configure.py
```

Expected output:

The configure test module passes, including tests that inspect the generated npm check and install commands.


### Run project quality checks

Command:

```shell
uv run pytest && uv run ruff check src tests && uv run ty check src
```

Expected output:

All tests pass, Ruff reports no errors, and the type checker reports no errors for `src`.


### Validate changed Markdown

Command:

```shell
node ~/.agents/tools/check-markdown-format.mjs .agents .config/opencode/agents .artifacts/20260714--opencode-install-cleanup/task-plan.md
```

Expected output:

The Markdown validator exits successfully with no formatting errors.


## Project standards

- [` .dot_agents/dot.md`](../../.dot_agents/dot.md) defines `dt configure`, the install manifest, and project checks.
- [`pyproject.toml`](../../pyproject.toml) configures the 120-character line limit.
- [`tests/test_configure.py`](../../tests/test_configure.py) uses one scenario per `test_<method>__<scenario>` method.
- [Markdown style guide](../../.agents/instructions/markdown.md) requires the custom Markdown validator for edited
  Markdown files.


## Steps

1. Add focused failing tests in `tests/test_configure.py` for the `opencode-npm-deps` tool using an overridden home:
   assert its check probes `<installer.home>/.config/opencode/node_modules/@opencode-ai/plugin`, and assert its
   install script invokes npm with `<installer.home>/.config/opencode` as the prefix rather than `$DOT_ROOT`.
2. Run `uv run pytest tests/test_configure.py` and confirm the new assertions fail against the current manifest.
3. Update the `opencode-npm-deps` entry in `etc/install.yaml` so both its installation check and `npm install --prefix`
   script use `$HOME/.config/opencode`. Retain the `node` dependency and NVM setup, and do not change the
   `@opencode-ai/plugin` version in `.config/opencode/package.json`.
4. Update the installer test harness only as needed to execute tool checks/scripts with the same `$HOME` value that
   `DotInstaller` uses for `--override-home`; preserve the existing `DOT_ROOT` behavior for unrelated tools.
5. Run `uv run pytest tests/test_configure.py` and confirm the new tests pass.
6. Keep the existing `.config/opencode/plugins` manifest link and add explicit `.gitignore` rules for
   `.config/opencode/node_modules/` and `.config/opencode/package-lock.json`. Do not add either artifact to Git, do
   not add either path to `link_paths`, and keep `.config/opencode/package.json` as the sole linked npm
   dependency-management file.
7. Preserve and include the existing working-tree changes: both OpenCode plugins, the OpenCode agent model updates,
   the agent-plan process updates, the Markdown validator, and the Markdown documentation updates that require it.
   Do not discard, overwrite, or fold these changes into the npm-install cleanup.
8. Remove the repository-local untracked `.config/opencode/node_modules/` and
   `.config/opencode/package-lock.json` artifacts after confirming they are ignored, then run `dt configure` with an
   isolated `--override-home` to verify the linked `package.json` and npm artifacts are created under that home.
9. Run the focused tests, full Python quality checks, and the Markdown validator. Inspect `git status --short` and
   verify it lists neither OpenCode dependency artifact while retaining the intended plugin, agent, and validator
   changes.


## Acceptance criteria

- AC01: `etc/install.yaml` makes `opencode-npm-deps` check for
  `$HOME/.config/opencode/node_modules/@opencode-ai/plugin` and run npm with
  `$HOME/.config/opencode` as its prefix; neither command references `$DOT_ROOT/.config/opencode`.
- AC02: Focused tests verify the OpenCode npm tool resolves its check and install location from the installer home,
  including an `--override-home` scenario.
- AC03: `link_paths` contains `.config/opencode/package.json` and does not contain
  `.config/opencode/node_modules` or `.config/opencode/package-lock.json`.
- AC04: `.gitignore` ignores `.config/opencode/node_modules/` and `.config/opencode/package-lock.json`, and
  `git status --short` does not report either artifact after installation.
- AC05: An isolated `dt configure --override-home <temp-home>` creates a symlink from
  `<temp-home>/.config/opencode/package.json` to the repository file and installs
  `node_modules/@opencode-ai/plugin` plus any generated lockfile under `<temp-home>/.config/opencode`, not in the
  repository.
- AC06: The working-tree changes for OpenCode plugins and agents, `.agents/tools/check-markdown-format.mjs`, and the
  associated Markdown documentation remain present after the cleanup.
- AC07: `uv run pytest`, `uv run ruff check src tests`, `uv run ty check src`, and the custom Markdown validator all
  exit 0.
