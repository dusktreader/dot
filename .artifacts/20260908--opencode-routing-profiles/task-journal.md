# Implementation Journal: Add isolated OpenCode routing profiles

This journal records execution of the approved task plan for isolated personal and optional work OpenCode routing.


## Source plan

`.artifacts/20260908--opencode-routing-profiles/task-plan.md`


## Status

**Complete**: The personal and optional work profile implementations, tests, configuration validation, documentation,
and focused verification are complete. One pre-existing personal test expectation remains incompatible with the
checked-in
OpenCode plugin version, and full `ty` validation retains unrelated baseline diagnostics.


## Tasks

### Task 01: Isolated OpenCode routing profiles

#### Status

**Complete**


#### Overview

Added launcher-managed personal and work LiteLLM routers, isolated OpenCode and Copilot runtime state, shared role-based
routing metadata, model-neutral aliases, optional work-dot installation, offline validators, focused tests, and setup
documentation. Existing `.dotrc` and work-dot `.workrc` changes were preserved.


#### Steps taken

- Read the complete approved task plan, artifact definitions, repository guidance, and authoritative OpenCode and
  LiteLLM
  documentation before editing.
- Recorded the initial worktree state. Personal had only the untracked task artifact directory; work-dot had a modified
  `.workrc`. Neither pre-existing change was overwritten.
- Verified OpenCode config fields and plugin hook signatures against `https://opencode.ai/config.json` and the current
  plugin documentation. Verified LiteLLM model aliases, tag filtering, fallback shape, GitHub Copilot provider route,
  token directory environment variables, and retry policy documentation.
- Added `opencode-tab` and `opencode-mhe` launchers with loopback-only ports `4010` and `4011`, health checks, PID-owned
  cleanup, separate XDG/runtime/cache/log/token state, preserved `HOME`, and unchanged OpenCode argument passthrough.
- Added personal and work LiteLLM configurations with shared `light`, `standard`, and `premium` aliases and profile,
  capability, and tier tags. The work route contains no Zen deployment or fallback.
- Added the shared routing plugin. It captures merged agent metadata, emits `x-litellm-tags`, rejects missing or invalid
  profile state, and removes private routing options before upstream dispatch.
- Replaced account/model specialist permutations with generic shared role definitions and updated principal/workflow
  policy
  text to make profile and tier selection principal-owned.
- Replaced the staged policy validator inventory checks with shared-role, profile-boundary, tier, and work-Zen checks
  while
  retaining manifest, lifecycle, promotion, and unsafe-mutation checks.
- Added personal and work install-manifest links, optional work LiteLLM installation, ignore rules, README setup
  guidance,
  and focused Python and Node tests.
- Ran focused tests, shell syntax checks, Node syntax/tests, offline profile validation, and focused Ruff checks.


#### Files modified

- CREATED: `bin/opencode-tab`
- CREATED: `.config/litellm/opencode-tab.yaml`
- CREATED: `.config/opencode/profiles/personal.json`
- CREATED: `.config/opencode/plugins/router-metadata.js`
- CREATED: `.config/opencode/agents/architect-planner.md`
- CREATED: `.config/opencode/agents/architect-reviewer.md`
- CREATED: `.config/opencode/agents/engineer-executor.md`
- CREATED: `.config/opencode/agents/engineer-investigator.md`
- CREATED: `.config/opencode/agents/engineer-planner.md`
- CREATED: `.config/opencode/agents/engineer-reviewer.md`
- CREATED: `.config/opencode/agents/engineer-task-planner.md`
- CREATED: `tools/validate_opencode_profiles.py`
- CREATED: `tests/test_opencode_profiles.py`
- CREATED: `tests/test_router_metadata.js`
- CREATED: `bin/opencode-mhe` in `~/src/mhe/work-dot`
- CREATED: `.config/litellm/opencode-mhe.yaml` in `~/src/mhe/work-dot`
- CREATED: `.config/opencode/profiles/work.json` in `~/src/mhe/work-dot`
- CREATED: `tests/test_opencode_profiles.py` in `~/src/mhe/work-dot`
- UPDATED: `.config/opencode/agents/principal.md`
- UPDATED: `.config/opencode/opencode.json`
- UPDATED: `.gitignore`
- UPDATED: `etc/install.yaml`
- UPDATED: `README.md`
- UPDATED: `.agents/agents/principal.md`
- UPDATED: `.agents/skills/run-feature/SKILL.md`
- UPDATED: `.agents/skills/run-task/SKILL.md`
- UPDATED: `.agents/skills/run-bug-fix/SKILL.md`
- UPDATED: `.agents/skills/run-fix/SKILL.md`
- UPDATED: `.agents/skills/run-hack/SKILL.md`
- UPDATED: `.agents/skills/run-hotfix/SKILL.md`
- UPDATED: `tools/validate_staged_agent_policies.py`
- UPDATED: `tests/test_validate_staged_agent_policies.py`
- UPDATED: `etc/install.yaml` in `~/src/mhe/work-dot`
- UPDATED: `.gitignore` in `~/src/mhe/work-dot`
- UPDATED: `README.md` in `~/src/mhe/work-dot`
- PRESERVED: `.dotrc` in the personal repository
- PRESERVED: `.workrc` in `~/src/mhe/work-dot`
- NOT MODIFIED: the approved task plan


#### Verification commands and results

- `uv run pytest tests/test_configure.py tests/test_install.py tests/test_cli_main.py tests/test_opencode_profiles.py
  tests/test_validate_staged_agent_policies.py --no-cov`
  passed 145 tests; one pre-existing assertion failed because it expects `@opencode-ai/plugin` `1.18.14` while the
  tracked package is `1.18.27`.
- `uv run pytest tests/test_opencode_profiles.py tests/test_validate_staged_agent_policies.py --no-cov` passed 9 tests.
- `uv run pytest tests/test_configure.py tests/test_opencode_profiles.py --no-cov` in work-dot passed 12 tests.
- `uv run ruff check tools/validate_opencode_profiles.py tests/test_opencode_profiles.py
  tools/validate_staged_agent_policies.py tests/test_validate_staged_agent_policies.py` passed.
- `uv run ruff check src/work_tools/configure.py tests/test_opencode_profiles.py` in work-dot passed.
- `uv run python tools/validate_opencode_profiles.py --personal-root . --work-root "$HOME/src/mhe/work-dot"` passed with
  `Validated personal and optional work OpenCode profiles`.
- `zsh -n .dotrc bin/opencode-tab` passed.
- `zsh -n "$HOME/src/mhe/work-dot/.workrc" "$HOME/src/mhe/work-dot/bin/opencode-mhe"` passed.
- `node --check .config/opencode/plugins/router-metadata.js` passed.
- `node --test tests/test_router_metadata.js` passed 3 tests. Node emitted only the expected module-type warning for the
  local ES module.
- `uv run ty check` ran and retained unrelated baseline diagnostics for optional dependencies, existing `opencode_costs`
  typing, and existing tests. No new diagnostic was isolated to the routing implementation.
- No real router, OAuth flow, provider request, `gh` operation, publication, push, or commit was performed.


#### Acceptance criteria validation


#### Satisfied AC01: Personal launcher isolation

`bin/opencode-tab`, `tests/test_opencode_profiles.py`, and the shell syntax check establish personal router endpoint,
XDG/runtime/cache/token separation, preserved `HOME`, status/stop behavior, and argument passthrough.


#### Satisfied AC02: Optional work launcher isolation

`~/src/mhe/work-dot/bin/opencode-mhe` mirrors the personal lifecycle on port `4011`; work tests verify its links, shell
syntax, isolated state, preserved `HOME`, and argument passthrough.


#### Satisfied AC03: Personal aliases and credential separation

`.config/litellm/opencode-tab.yaml` exposes the three aliases, uses the `github_copilot` provider for personal routes,
references `OPENCODE_ZEN_API_KEY` only through an environment expression, and contains no credential value.


#### Satisfied AC04: Work aliases and account boundary

`~/src/mhe/work-dot/.config/litellm/opencode-mhe.yaml` exposes the same aliases, uses only `github_copilot` routes, and
contains no Zen deployment, Zen text, or fallback.


#### Satisfied AC05: Personal-only light fallback

The personal router maps only `light` to `personal-light-zen`. The work configuration has no fallback section. The
offline
validator and work tests reject Zen in the work route.


#### Satisfied AC06: Shared deterministic routing plugin

`router-metadata.js` has deterministic role-to-capability/tier defaults, validates `profile:personal` or `profile:work`,
emits required `x-litellm-tags`, and strips private routing options. `tests/test_router_metadata.js` covers all paths.


#### Satisfied AC07: Generic shared roles and principal ownership

Profile/model specialist permutations were removed. Generic role definitions now carry only shared role metadata, while
principal and workflow policies own project classification, profile selection, and premium approval.


#### Satisfied AC08: Model-generated text cannot change profile

The launcher sets `OPENCODE_ROUTING_PROFILE`; the plugin rejects any other value and emits the required profile tag.
Profile metadata is not read from model text or user-controlled routing options.


#### Satisfied AC09: Installer boundaries

Personal `etc/install.yaml` links only personal artifacts and does not inspect work-dot. Work-dot owns its own launcher,
router, overlay, tests, and optional `litellm[proxy]` tool entry.


#### Satisfied AC10: Runtime and secret separation

Launchers use distinct state roots, XDG directories, token directories, PID files, logs, and router keys. Runtime paths
are ignored. Tracked configs use environment references and contain no credential-looking values.


#### Satisfied AC11: Focused verification and preservation

Focused personal/work tests, Ruff checks, shell checks, Node checks, and offline validation pass. Existing `.dotrc` and
work-dot `.workrc` modifications remain in the final status. The one personal test failure is the pre-existing plugin
version expectation described above; full `ty` retains unrelated baseline diagnostics.


#### Satisfied AC12: Documentation and troubleshooting

Personal and work READMEs document commands, ports, state isolation, shared `.agents`, first-run account boundaries,
personal-only Zen behavior, opt-in work setup, status/stop commands, and the `gh auth switch` limitation.


#### Additional notes

LiteLLM's documented `router_settings.fallbacks` applies to remaining provider errors, while the authoritative provider
documentation confirms Copilot OAuth storage and the provider's 429 handling but does not expose a distinct quota-only
fallback class in the proxy configuration schema. The configuration therefore keeps the approved personal-only light
fallback isolated and records the remaining limitation: runtime behavior must be confirmed against a non-production
Copilot quota response before treating it as quota-only. No work route can reach that fallback.

The personal router's Zen deployment uses the documented OpenCode Zen OpenAI-compatible endpoint with an environment
referenced key. No provider authentication or model call was performed during execution.


## Independent review fixes

### Changes

- Hardened both launchers so a healthy port is reusable only when the recorded PID is alive and its complete command
  matches the profile-specific LiteLLM config, loopback host, and port. Any unrelated listener fails closed, and stop
  removes only the matching recorded PID.
- Migrated `run-feature`, `run-bug-fix`, `run-fix`, and `run-hotfix` dispatch prose to generic shared roles with
  explicit
  profile and tier selection, while retaining premium approval requirements.
- Restored staged-policy checks for branch workflows, review-pr, shared worktree contracts, publication and main
  integration controls, retained temporary branches, and principal ownership. Added generic role metadata and
  model-specific dispatch rejection invariants with omission regression tests.
- Added a work launcher boundary requiring an owner-controlled Copilot state directory and an exact
  `TuckerBeck_mcgraw` account marker before normal startup. Documentation records that this is an offline assertion
  seam and cannot verify provider identity without a provider call.


### Verification

- Personal focused tests: `uv run pytest tests/test_validate_staged_agent_policies.py tests/test_opencode_profiles.py
  --no-cov -q` passed 80 tests, including 71 staged-policy regression tests.
- Work focused tests: `uv run pytest tests/test_opencode_profiles.py --no-cov -q` passed 8 tests.
- Focused Ruff passed for all touched personal and work Python files.
- `zsh -n .dotrc bin/opencode-tab` and `zsh -n .workrc bin/opencode-mhe` passed.
- Offline profile validation passed for personal and optional work profiles.
- Node syntax and router metadata tests passed: 3 tests.


## Tier-default adjustment

### Changes

- Changed personal and work defaults from `standard` to `light`, selecting the economical Luna route for ordinary
  dispatches.
- Kept `standard` available for specific cases supported by task complexity or evidence, and retained `premium` behind
  explicit human approval.
- Updated principal policy tables, profile overlays, the personal global OpenCode config, generic agent metadata, the
  plugin fallback for unknown agents, and staged-policy expectations.


### Verification

- Personal focused tests: `uv run pytest tests/test_opencode_profiles.py tests/test_validate_staged_agent_policies.py
  --no-cov -q` passed 80 tests.
- Work focused tests: `uv run pytest tests/test_opencode_profiles.py --no-cov -q` passed 8 tests.
- Focused Ruff passed in both repositories.
- Shell syntax, offline profile validation, Node syntax, and router metadata tests passed.
- `git diff --check` passed in both repositories.


## Independent review resolution

### Changes

- Added `capability:tools` to the personal Luna light deployment, the personal Zen light fallback, and the work Luna
  light deployment so required principal tags match every light route without a provider call.
- Added a launcher-owned `--tier` selection seam to both profiles. Omission selects `light`; `--tier standard` selects
  the standard model alias and sets validated routing metadata for the invocation; invalid tiers fail before router
  startup; premium requires the explicit human assertion `OPENCODE_PREMIUM_APPROVED=1`.
- Added plugin validation for capability and tier metadata, explicit standard and premium routing tests, unknown-agent
  light fallback coverage, personal and work light-default overlay tests, launcher standard-selection tests, inherited
  tier isolation coverage, and launcher invalid-tier tests.
- Documented the exact standard selection command in both READMEs and the principal policy. The approved task plan and
  personal `.dotrc` and work `.workrc` were not modified.


### Verification

- Personal focused profile and staged-policy tests passed: 84 tests.
- Node router metadata tests passed: 7 tests.
- Work focused profile tests passed: 11 tests.
- Focused Ruff, shell syntax, offline profile validation, Node syntax/tests, and `git diff --check` passed in both
  applicable repositories.


## Latest re-review resolution

### Changes

- Extended staged-policy model-specific dispatch validation to `run-hack` without changing its existing lifecycle and
  safety checks. Added a regression fixture that updates the manifest checksum and rejects
  `engineer-executor--work-luna` in that skill.
- Added Node coverage for invalid capability metadata.
- Added personal and work launcher coverage that rejects premium routing without
  `OPENCODE_PREMIUM_APPROVED=1`.
- Updated both standard-selection fake OpenCode commands to capture remaining arguments and assert that
  `--session abc` reaches OpenCode unchanged.


### Verification

- Personal profile and staged-policy tests: `uv run pytest tests/test_opencode_profiles.py
  tests/test_validate_staged_agent_policies.py --no-cov -q`, 86 passed.
- Work profile tests: `uv run pytest tests/test_opencode_profiles.py --no-cov -q`, 12 passed.
- Node router metadata tests: `node --test tests/test_router_metadata.js`, 8 passed.
- Node syntax: `node --check .config/opencode/plugins/router-metadata.js` passed.
- Personal Ruff: `uv run ruff check tools/validate_staged_agent_policies.py
  tests/test_validate_staged_agent_policies.py tests/test_opencode_profiles.py` passed.
- Work Ruff: `uv run ruff check tests/test_opencode_profiles.py` passed.
- Shell syntax passed for personal `.dotrc` and `bin/opencode-tab`, and work `.workrc` and `bin/opencode-mhe`.
- Offline profile validation passed for personal and optional work profiles.
- `git diff --check` passed in both repositories.


### Residual limitations

Provider authentication, router startup, and model requests remain intentionally untested. The journaled limitation
about distinguishing Copilot quota exhaustion from other upstream failures remains unchanged. No commit, push, `gh`
call, provider contact, worktree operation, or plan modification occurred.


## CLI migration

### Changes

- Replaced the personal shell launcher with `dt opencode launch [--tier light|standard|premium] [OpenCode args...]`,
  `dt opencode status`, and `dt opencode stop`; the existing costs, trends, and staleness-guard commands remain
  registered.
- Added equivalent `wdt opencode ...` commands with a work-owned lifecycle module, `WORK_HOME` resolution, and a safe
  fallback to `~/src/mhe/work-dot`.
- Added reusable Python lifecycle modules with list-based `Popen`, `os.execvpe` seams, loopback health and port checks,
  exact router command ownership checks, PID reuse protection, safe stop, generated mode `0600` router keys, preserved
  `HOME`, isolated XDG/Copilot state, environment/config overlays, and OpenCode argument passthrough.
- Kept work account marker gating on launch only and retained work Zen exclusion. Added `oc='dt opencode launch'` and
  `woc='wdt opencode launch'` without removing the pre-existing work `helm` alias.
- Removed `bin/opencode-tab` and `bin/opencode-mhe` and removed their install-manifest links. Updated both READMEs to
  make CLI commands canonical.
- Changed premium authorization so explicit CLI `--tier premium` sets a launcher-owned authorization marker and does not
  require `OPENCODE_PREMIUM_APPROVED=1`; automated policy remains gated by that environment approval.
- Migrated shell launcher tests to Python lifecycle and CLI seams covering all tiers, invalid tiers, CLI premium,
  argument passthrough, generated environment/config, health/PID/port safety, safe stop, status, account gating,
  aliases, manifests, no Zen in work, and preservation of existing OpenCode commands.
- Did not modify the approved task plan or contact providers, authenticate, use `gh`, create worktrees, commit, or push.


### Verification

- Personal focused migration and existing OpenCode CLI tests: 55 passed.
- Work focused migration and existing CLI/configuration tests: 31 passed.
- Personal full suite: 403 passed, 1 known baseline failure in
  `tests/test_configure.py::TestDotInstallerInstallTools::test_install_manifest__installs_opencode_npm_dependencies`
  because the pre-existing assertion expects `@opencode-ai/plugin` `1.18.14` while the tracked package is `1.18.27`.
- Work full suite: 36 passed.
- Personal and work Ruff checks passed for `src` and `tests`.
- Router plugin syntax and tests passed: `node --check`, 9 Node tests.
- Offline profile validation passed for personal and optional work profiles.
- `git diff --check` passed in both repositories.


### Residual limitations

Provider authentication, router startup against LiteLLM, and model requests remain intentionally untested. The existing
personal Zen fallback limitation remains: the configured fallback cannot be proven quota-only without a controlled
provider response. The work account marker is an offline assertion seam and cannot prove provider identity without a
provider call.


## Independent review fixes

### Changes

- Removed inherited personal provider and routing credential variables from the work OpenCode and LiteLLM environments,
  including Zen, Copilot, OpenAI-compatible, and other known provider token names. Safe generic variables remain, and
  the work-owned Copilot directory and generated work router key are retained.
- Tightened router ownership checks so the executable token itself must be `litellm` or an absolute path whose basename
  is
  `litellm`; the config, loopback host, port, and complete argument shape must still match exactly. Wrapper commands
  with
  a later `litellm` token are rejected for both profiles.
- Added startup-failure cleanup for newly started routers. Exited or unhealthy new processes are terminated when still
  alive, and their PID and log state are removed. Pre-existing matching routers continue to be waited on without
  termination or state cleanup.
- Added a work launch-time check for the shared personal plugin at `~/.config/opencode/plugins/router-metadata.js`.
  Work-dot does not copy or install the plugin, and status and stop remain usable when it is absent. Work README
  guidance
  documents the prerequisite.
- Updated personal `uninstall.sh` to remove the personal OpenCode profile and LiteLLM configuration symlinks.
- Changed premium routing errors to say that explicit CLI authorization or automated approval is required without
  including credential material.


### Verification

- Personal focused profile tests: 26 passed.
- Work focused profile tests: 20 passed.
- Work full suite: 45 passed.
- Personal full suite: 409 passed and one known pre-existing failure remains in
  `tests/test_configure.py::TestDotInstallerInstallTools::test_install_manifest__installs_opencode_npm_dependencies`
  because the test expects `@opencode-ai/plugin` `1.18.14` while the tracked package is `1.18.27`.
- Personal and work Ruff checks passed for `src` and `tests`.
- Node syntax and router metadata tests passed: 9 tests.
- Shell syntax checks passed for personal `.dotrc` and work `.workrc`.


### Final review

- The final independent re-review found no Critical, Significant, or Trivial findings and approved the CLI migration.
- The known personal package-version mismatch, stale global `dt` executable during QA, and provider-specific
  limitations remain non-blocking and are not source regressions.
- Offline profile validation passed for personal and optional work profiles.
- `git diff --check` passed in both repositories.
- `uv run ty check` retained 78 existing baseline diagnostics, including unresolved optional dependencies and existing
  typing issues; no routing-specific diagnostic was isolated.
- No provider request, OAuth authentication, `gh` operation, commit, push, or worktree operation was performed.


### Residual limitations

Provider authentication, live router startup, and model requests remain intentionally untested. The existing personal
Zen fallback limitation remains: its configured fallback cannot be proven quota-only without a controlled provider
response. The work account marker remains an offline assertion and cannot prove provider identity without a provider
call.


## LiteLLM config filename cleanup

### Changes

- Renamed the personal LiteLLM configuration to `.config/litellm/personal.yaml` and the work configuration to
  `.config/litellm/work.yaml`.
- Updated lifecycle path resolution, install manifests, uninstall cleanup, offline validation, and profile tests. The
  file names are repository conventions; LiteLLM still receives each path explicitly through `--config`.


### Verification

- Personal and work focused profile tests passed after the rename.
- Offline profile validation passed for both `personal.yaml` and `work.yaml`.
- No provider calls, authentication, or router startup were performed.


## Critical re-review remediation

### Fix

- Tightened `router_pid_is_ours` in both lifecycle modules so ownership accepts only the bare executable token `litellm`
  or
  an absolute executable path whose basename is `litellm`. Relative path tokens such as `./litellm` and
  `wrapper/litellm`
  are rejected.
- Added personal and work regression coverage for bare-token acceptance, absolute-path acceptance, and relative-path
  rejection. The approved task plan, `.dotrc`, and `.workrc` were not modified.


### Verification

- Personal profile tests: `uv run pytest tests/test_opencode_profiles.py --no-cov -q`, 28 passed.
- Work profile tests: `uv run pytest tests/test_opencode_profiles.py --no-cov -q`, 22 passed.
- Personal and work focused Ruff checks passed for the lifecycle modules and profile tests.
- Node syntax and router metadata tests passed: `node --check .config/opencode/plugins/router-metadata.js` and
  `node --test tests/test_router_metadata.js`, 9 passed.
- Offline profile validation passed for personal and optional work profiles.
- Shell syntax checks passed for personal `.dotrc` and work `.workrc`.
- `git diff --check` passed in both repositories.


### Residual limitation

Provider authentication, live router startup, and model requests remain intentionally untested. No provider contact,
authentication, `gh` call, commit, push, worktree creation, or plan modification occurred.


## Active profile identifier cleanup

### Changes

- Replaced the active `opencode-tab` and `opencode-mhe` OpenCode provider/model identifiers with `personal` and `work`.
- Updated the global and profile OpenCode configs, lifecycle state roots, generated routing config, staged-policy
  validator,
  CLI help paths, and profile tests. Historical task-plan and journal references remain unchanged.


### Verification

- Personal focused tests: 100 passed.
- Work focused tests: 22 passed.
- Ruff, offline profile validation, CLI help, Node tests, shell syntax, and diff checks passed.
- No active source/config/test references to `opencode-tab/` or `opencode-mhe/` remain.


## OpenCode agent adapter cleanup

### Changes

- Replaced the OpenCode agent stub bodies with frontmatter `prompt` references to the shared role files under
  `~/.agents/agents/`.
- Removed redundant per-agent `options.routing` metadata. LiteLLM receives capability and tier tags from the shared
  routing plugin, whose centralized defaults remain authoritative.
- Removed the explicit model and variant from the principal adapter. The active launcher/profile selects the model;
  OpenCode retains the principal name, mode, description, and shared prompt.
- Renamed active OpenCode state/provider identifiers to `personal` and `work` and updated ignore rules accordingly.


### Verification

- OpenCode agent files contain no redundant model, variant, or routing option blocks.
- Focused personal/work routing tests, staged-policy validation, CLI help, offline profile validation, Node tests, Ruff,
  shell syntax, and diff checks pass.


### Residual limitation

The shared role descriptions remain external files under `~/.agents/agents/`; OpenCode loads them through the adapter
frontmatter prompt references. LiteLLM remains responsible only for model routing, not agent discovery.


## Principal default variant

### Changes

- Kept the active model at `personal/light` or `work/light` while setting the principal agent's default OpenCode
  variant to `xhigh`.
- Added `default_agent: principal` and `variant: xhigh` to launcher-generated runtime config so new sessions use the
  principal agent and requested variant without changing LiteLLM tier routing.


### Verification

- Personal and work profile tests assert `default_agent: principal`, the light model, and principal `variant: xhigh`.
- Personal focused tests: 100 passed.
- Work focused tests: 22 passed.
- CLI help, offline validation, Ruff, shell syntax, and diff checks passed.


## Provider environment scope cleanup

### Changes

- Narrowed the work-profile credential isolation list to the providers and routing controls actually used by this setup:
  OpenCode Zen, GitHub Copilot, GitHub auth tokens, the profile router key, and premium approval state.
- Removed unrelated provider variables from the cleanup list. Additional provider support can be added explicitly when
  needed.


### Verification

- Personal focused tests: 100 passed.
- Work focused tests: 22 passed.
- Ruff, offline profile validation, Node routing tests, and diff checks passed.
