# dusktreader's todo list for dot


# general

* use fd more
* use rip-grep more


# installer todos

* add pre-reqs to the README


# dot_tools todos

* replace `setuptools.find_packages` in `git_tools.py`
* convert install.json to yaml
* port the nuke function from .dotrc to dot_tools
* convert dot_tools executables to use typer
* make them all a single executable named "dot" with sub-commands
* convert dot_tools to use pathlib
* add method for creating branch from clickup id
* modify the version tool to use pyproject.toml


## OpenCode package refactor

Refactor the OpenCode-specific Python code into a coherent `dot_tools.opencode` package and mirror the profile lifecycle
module structure in `work_tools.opencode`.


### Personal package layout

- Create `src/dot_tools/opencode/__init__.py` with the public package API.
- Move shared literals, profile names, tier names, environment-variable names, and routing constants into
  `src/dot_tools/opencode/constants.py`.
- Move `ProfileSpec`, lifecycle hook protocols/types, and other data structures into
  `src/dot_tools/opencode/schemas.py`.
- Move personal/work profile definitions and environment/config construction into
  `src/dot_tools/opencode/profile.py`.
- Move router startup, health checks, PID ownership, cleanup, status, stop, and OpenCode process replacement into
  `src/dot_tools/opencode/lifecycle.py`.
- Move `opencode_costs.py` to `src/dot_tools/opencode/costs.py`.
- Move `opencode_trends.py` to `src/dot_tools/opencode/trends.py`.
- Move `opencode_staleness_guard.py` to `src/dot_tools/opencode/staleness_guard.py`.
- Update `src/dot_tools/cli/opencode.py` and all imports to use the package modules.
- Preserve public behavior and avoid compatibility aliases unless an existing external import requires one.


### Work package layout

- Create `src/work_tools/opencode/__init__.py` with the public package API.
- Create matching `constants.py`, `schemas.py`, `profile.py`, and `lifecycle.py` modules, or share only genuinely
  profile-independent definitions without creating a personal/work import dependency.
- Keep work account validation, personal credential stripping, shared-plugin prerequisites, and work Zen exclusion in
  the work package.
- Update `src/work_tools/cli/opencode.py` and tests to use the new package paths.


### Migration requirements

- Update all personal imports, work imports, tests, type-check configuration, and package exports.
- Keep the CLI commands unchanged: `dt opencode launch/status/stop` and `wdt opencode launch/status/stop`.
- Keep active identifiers `personal` and `work`, model variants, LiteLLM config names, profile isolation, and router
  ownership checks unchanged.
- Preserve `costs`, `trends`, and `staleness-guard` command behavior.
- Preserve the shared OpenCode agent adapter prompts and centralized plugin routing. Do not reintroduce agent-level
  model or tier metadata into the refactor.
- Rename tests coherently, for example `test_opencode_costs.py` to `test_opencode/costs`, and retain focused lifecycle,
  profile, CLI, plugin, and custom-tool coverage.
- Remove stale module paths and verify no `from dot_tools.opencode_*` or `from work_tools.opencode_*` imports remain.
- Run the personal and work full test suites, Ruff, type checks, CLI help checks, offline profile validation, Node
  plugin tests, shell syntax checks, and `git diff --check`.


# miscellaneous todos

* cleanup unused scripts and executables
* make Python agent tools directly executable with `uv run --script` shebangs, inline metadata, and executable bits


# vim todos

* Investigate `vim-surround`
* Investigate `harpoon`
* Investigate `possession.nvim`
* Look into `op.nvim` + `dressing.nvim` + `parrot.nvim` for llm support in vim
