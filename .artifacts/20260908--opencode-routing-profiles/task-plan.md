# Task plan: Add isolated OpenCode routing profiles

Add personal and optional work OpenCode launch profiles, local LiteLLM routers, and a shared OpenCode routing plugin so
agent roles no longer need personal/work/model permutations. Keep personal implementation in `~/src/dusktreader/dot`,
keep work-specific implementation optional in `~/src/mhe/work-dot`, and preserve account, credential, and repository
isolation.


## Goal

Implement a personal `opencode-tab` profile in the personal dot repository and an optional `opencode-mhe` profile in
work-dot. Each profile must launch OpenCode with isolated runtime state and a profile-specific local LiteLLM router. The
personal router authenticates as `dusktreader` and may fall back to OpenCode Zen; the work router authenticates as
`TuckerBeck_mcgraw` and must not expose Zen. Add a shared OpenCode plugin that translates the active agent's capability
and tier metadata into LiteLLM routing headers, then simplify the personal agent definitions so profile and account are
no longer encoded into every specialist name.

The task includes repository configuration, shell launchers, router configuration, plugin implementation, tests, and
setup documentation. It does not include logging into either GitHub account, creating or storing OAuth/API credentials
in Git, changing the OpenCode upstream, modifying the shared `.agents` workflow prose beyond the routing contract
required by the refactor, or automatically installing the optional work-dot changes into a machine where work-dot is
absent.


## Project commands

### Run personal repository tests

Command:

```shell
uv run pytest
```

Expected output:

The personal dot test suite passes, including installer, launcher, plugin, and routing configuration tests.


### Run personal Python quality checks

Command:

```shell
uv run ruff check src tests && uv run ty check
```

Expected output:

Ruff and ty complete without diagnostics.


### Run work-dot tests when the optional work profile is present

Command:

```shell
uv run pytest
```

Expected output:

The work-dot test suite passes, including work profile installer and router tests. If `~/src/mhe/work-dot` is absent,
skip this command and verify that the personal repository does not require it.

Prerequisites:

- `~/src/mhe/work-dot` must exist and contain the optional work profile implementation.


### Validate shell syntax

Command:

```shell
zsh -n .dotrc bin/opencode-tab
if [[ -d "$HOME/src/mhe/work-dot" ]]; then
  zsh -n "$HOME/src/mhe/work-dot/.workrc" "$HOME/src/mhe/work-dot/bin/opencode-mhe"
fi
```

Expected output:

The command exits zero. Validate every new launcher or shell helper file explicitly if the implementation stores
launchers outside these two files.


### Validate router configuration without contacting providers

Command:

```shell
uv run python tools/validate_opencode_profiles.py --personal-root . --work-root "$HOME/src/mhe/work-dot"
```

Expected output:

The validator reports valid personal configuration and, when the work root exists, valid work configuration. It rejects
embedded credentials, missing profile boundaries, Zen in the work router, invalid model aliases, and missing fallback
restrictions. The command must not perform OAuth login or send model requests.


### Format changed Markdown

Command:

```shell
~/.agents/tools/markdown-format.py format .artifacts/20260908--opencode-routing-profiles/task-plan.md
```

Expected output:

The task plan is formatted in place according to the repository Markdown style guide.


## Project standards

- [Repository guide](../../.dot_agents/dot.md) defines the personal dot layout, `dt configure`, and installer manifest.
- [Work repository instructions](../../../.agents/instructions/work.md) define work repository location, account
  separation, and the `TuckerBeck_mcgraw` requirement.
- [OpenCode config schema](https://opencode.ai/config.json) is authoritative for all OpenCode JSON fields.
- [OpenCode plugin API](https://opencode.ai/docs/plugins/) defines the `config`, `chat.params`, and `chat.headers`
  hooks.
- [LiteLLM tag routing](https://docs.litellm.ai/docs/proxy/tag_routing) defines request tags, required `&` tags, and
  profile/capability routing behavior.
- [LiteLLM fallback routing](https://docs.litellm.ai/docs/proxy/reliability) defines personal fallback behavior and
  retry semantics.
- [Personal credential separation guide](../../.dot_agents/CREDENTIAL_MIGRATION.md) defines the boundary between `dt`
  and `wdt` stores.
- [Markdown style guide](../../.agents/instructions/markdown.md) governs this artifact and all edited Markdown files.
- [Personal project configuration](../../.config/opencode/opencode.json) is the current linked OpenCode configuration
  baseline.
- [Personal install manifest](../../etc/install.yaml) controls files linked into the personal home and installed tools.
- [Work install manifest](../../../mhe/work-dot/etc/install.yaml) controls files linked into the work home when work-dot
  is installed.


## Steps

1. Record the existing modified working-tree files in both repositories and preserve them throughout the task. In
   particular, do not overwrite the current `.dotrc` or work-dot `.workrc` changes. Decide whether the new profile
   launchers belong in repository-managed dotfiles, a `bin/` helper, or both; use one canonical implementation per
   profile and make `opencode-tab` and `opencode-mhe` stable commands on `PATH`.
2. Define the shared routing contract before changing agent files. Use an explicit profile boundary supplied by the
   launcher or router endpoint, not by model-generated text. Define capability and tier metadata with stable names such
   as `capability:coding`, `capability:analysis`, `capability:tools`, `tier:light`, `tier:standard`, and
   `tier:premium`. Use `light` for economical or low-latency model families such as Luna or Haiku, `standard` for
   the default general-purpose route, and `premium` for explicitly approved high-capability models. Require the work
   profile to use `profile:work` and the personal profile to use `profile:personal`; do not allow a request header to
   override the account profile.
3. Add a personal router configuration under the personal dot repository. Store it at
   `.config/litellm/opencode-tab.yaml` and expose stable logical model aliases for the
   shared OpenCode configuration, at minimum the `light`, `standard`, and explicitly approved `premium` aliases.
   Route personal light and standard requests to GitHub Copilot authenticated as `dusktreader`, route personal premium
   requests to the approved personal premium upstream, and configure the Zen fallback only for the personal light path.
   Keep all
   credentials in environment variables, local auth storage, or the existing credential mechanism; never put OAuth
   tokens, Zen keys, or router master keys in tracked files.
4. Add an optional work router configuration at `~/src/mhe/work-dot/.config/litellm/opencode-mhe.yaml`. Expose the same
   logical aliases and capability
   tags as the personal router so the shared OpenCode agents do not encode profile names. Route through GitHub Copilot
   authenticated as `TuckerBeck_mcgraw`, do not configure OpenCode Zen or any other personal fallback, and source work
   credentials through the work layer rather than `dt` or personal files. The work repository must remain independently
   installable and must not require changes to the personal repository's credentials.
5. Implement launcher-managed, loopback-only routers rather than adding launchd/systemd services in the first version.
   Use `127.0.0.1:4010` for personal and `127.0.0.1:4011` for work, separate Copilot token directories, a
   profile-specific PID/state directory, a health check, and cleanup of only the PID recorded by that profile. Start a
   router only when its profile launcher needs it, reuse a healthy existing process, and fail with a setup instruction
   when `litellm` is unavailable. Do not bind either router to a non-loopback address or create a work service from the
   personal installer.
6. Add the personal `bin/opencode-tab` launcher in the personal repository. It must select the personal OpenCode config
   or
   overlay, point OpenCode at the personal router endpoint, isolate OpenCode data/state/cache and router auth state from
   work, preserve `HOME` so the shared `~/.agents` link remains visible, and pass through arbitrary OpenCode arguments
   unchanged. Add an explicit status or diagnostic mode if practical so the active profile, router endpoint, and
   selected config path can be inspected without printing secrets.
7. Add the optional `bin/opencode-mhe` launcher and installation wiring in work-dot. It must select the work OpenCode
   config
   or overlay, point OpenCode at the work router endpoint, isolate work OpenCode data/state/cache and router auth state
   from personal, preserve the shared `~/.agents` link, and pass through arbitrary arguments unchanged. Make
   installation opt-in through `wdt configure` or an explicit work-dot option rather than causing `dt configure` to
   touch `~/src/mhe/work-dot`.
8. Add the shared routing plugin as `.config/opencode/plugins/router-metadata.js` in the personal dot repository. The
   personal install manifest already owns the global plugin directory, so work-dot should reuse the installed shared
   plugin rather than duplicate or fork it. The plugin must read the merged agent configuration, map the active agent to
   capability/tier metadata, and add only the routing headers LiteLLM requires. Use the OpenCode `config` hook to
   capture metadata, `chat.headers` to send `x-litellm-tags`, and `chat.params` to remove private routing options before
   they reach an upstream model. Handle primary, subagent, title, compaction, and resumed sessions deterministically; do
   not add credentials or account-selection logic to the plugin.
9. Add shared agent metadata and collapse profile permutations. Replace profile-specific specialist definitions with one
   role definition per shared specialist and, if per-task premium escalation is required, a small profile-independent
   premium set. Keep reviewers on the approved default tier unless the existing policy explicitly permits escalation.
   Update the principal and workflow skills so dispatch names are generic role names or the new profile-independent
   premium names, while project classification still controls which launcher/profile may be used and work never routes
   through Zen.
10. Update the staged agent-policy validator and its tests to validate the new invariant. Replace requirements for
    `--personal-*` and `--work-*` specialist files with checks for the shared role inventory, valid tier metadata,
    explicit profile boundaries, no Zen work route, and principal ownership of profile/tier selection. Preserve all
    existing safety checks for model escalation, worktree lifecycle, human gates, branch publication, and work/personal
    project classification.
11. Add focused personal tests. Cover launcher environment construction, argument passthrough, preserved `HOME`, XDG
    isolation, personal router model aliases and fallback restrictions, plugin tag generation for each shared role and
    tier, omission of secrets, and rejection of an invalid or missing profile. Use subprocess/environment seams rather
    than starting real routers or authenticating providers.
12. Add focused work-dot tests when the optional work repository is available. Cover work launcher isolation, work
    router configuration, `TuckerBeck_mcgraw` account boundary, absence of Zen, optional installer behavior, and
    preservation of the existing `.agents/instructions/work.md`, `.gitconfig.work`, and `.workrc` installation behavior.
    Do not read or print live work credentials in tests.
13. Add setup and troubleshooting documentation to both owning repositories. Document the two commands, ports and state
    directories, first-run Copilot and Zen authentication steps, router startup/status/stop commands, the fact that
    `.agents` remains shared, the personal-only Zen fallback, and how to enable or omit the optional work profile.
    Include an explicit warning that `gh auth switch` does not change OpenCode or LiteLLM Copilot OAuth state.
14. Add install-manifest entries, ignore rules, and cleanup behavior for local router/runtime artifacts. Add personal
    links for `bin/opencode-tab`, the personal OpenCode profile overlay, and the personal LiteLLM config. Add work-dot
    links for `bin/opencode-mhe`, the work OpenCode profile overlay, and the work LiteLLM config. Extend work-dot's
    installer only as needed to install the `litellm[proxy]` tool and make the work launcher independently usable; do
    not
    make personal installation inspect or mutate the work repository. Keep tracked
    configs and launchers in their owning repository, ignore generated LiteLLM databases, logs, token directories,
    lockfiles, and OpenCode profile runtime directories, and ensure `dt configure` and optional `wdt configure` do not
    clobber locally modified configs without their existing force behavior. Do not add secrets to `.gitignore` as a
    substitute for excluding them from tracked configuration.
15. Run personal tests and quality checks, then run work-dot checks if the optional repository is present. Validate
    shell syntax, validate both router configurations offline, inspect the installed symlink targets and launcher
    environment, and perform a local smoke test against a stub OpenAI-compatible endpoint if the test harness supports
    it. Do not perform real model calls, OAuth logins, `gh` operations, router publication, or work repository mutations
    without explicit human approval.
16. Review the final diff and status in both repositories. Confirm that unrelated existing modifications remain, that no
    credential or generated runtime file is tracked, that `opencode-tab` is usable without work-dot, and that the work
    profile is absent or fully optional when `~/src/mhe/work-dot` is not installed. Record any unresolved
    provider-specific behavior, especially whether GitHub Copilot quota exhaustion is distinguishable from general
    upstream failure for the personal Zen fallback.


## Acceptance criteria

- AC01: Running `opencode-tab` from a personal project launches OpenCode with the personal configuration, personal
  router endpoint, personal OpenCode data/state/cache directories, and the shared `~/.agents` link still readable.
- AC02: Running `opencode-mhe` is optional and, when work-dot is installed, launches OpenCode with work configuration,
  work router endpoint, work OpenCode data/state/cache directories, and the shared `~/.agents` link still readable.
- AC03: Personal router configuration exposes the documented logical model aliases and routes personal requests to the
  `dusktreader` Copilot credential; no personal credential or Zen key is present in tracked files.
- AC04: Work router configuration exposes the same logical aliases, routes work requests to the `TuckerBeck_mcgraw`
  Copilot credential, and contains no OpenCode Zen deployment or fallback.
- AC05: The personal router's Zen fallback is configured only for the explicitly approved personal model path, and
  router tests prove no work configuration can select it.
- AC06: The shared OpenCode plugin emits deterministic capability and tier routing tags for every supported shared
  agent, adds the profile boundary supplied by the launcher/router, and removes private routing options before upstream
  dispatch.
- AC07: Shared agent definitions no longer require personal/work account permutations. Principal dispatch and workflow
  validation use generic role names or profile-independent premium names while preserving explicit human approval for
  premium escalation.
- AC08: Profile selection cannot be changed by agent-generated routing metadata. The launcher or router endpoint
  establishes `profile:personal` or `profile:work`, and conflicting request tags are rejected or ignored by the router.
- AC09: `dt configure` installs the personal plugin, launchers, config, and router artifacts without touching
  `~/src/mhe/work-dot`; optional work-dot configuration installs only work-owned artifacts.
- AC10: Personal and work router authentication/token directories, OpenCode runtime directories, logs, caches, local
  databases, and generated lockfiles are separate and ignored. No secret appears in tracked content, test output, or
  documentation examples.
- AC11: Personal tests, work-dot tests when available, shell syntax checks, offline router validation, and the required
  Python quality checks pass. Existing unrelated working-tree changes remain intact.
- AC12: Documentation explains installation, first-run authentication, startup and shutdown, profile selection, fallback
   boundaries, shared `.agents` behavior, and troubleshooting for stale or mixed credentials.


## Technical notes

- The current personal installer links `.config/opencode/agents`, `.config/opencode/plugins`, `package.json`, and
  `opencode.json` into the home directory. Extend that existing manifest rather than introducing a second unmanaged
  global config tree.
- The planned personal paths are `bin/opencode-tab`, `.config/litellm/opencode-tab.yaml`, and a personal OpenCode
  profile overlay loaded by the launcher. The planned work paths are `bin/opencode-mhe`,
  `.config/litellm/opencode-mhe.yaml`, and the corresponding work profile overlay.
- OpenCode's current `task` tool accepts `subagent_type`, `description`, `prompt`, and related execution fields, but no
  arbitrary router parameter object. The plugin should derive routing metadata from agent identity/configuration and
  `chat.headers`, not rely on an unsupported Task-tool parameter.
- OpenCode's `chat.headers` hook can add request headers, and LiteLLM accepts `x-litellm-tags`. Use required tags (`&`)
  for capability and tier constraints so a missing capability fails closed instead of silently selecting an unsuitable
  deployment.
- Keep account/profile routing outside the model prompt. A model-generated `work` flag is not an authentication
  boundary. Separate launcher endpoints, keys, token directories, and router configs provide the boundary.
- The work repository already owns `.agents/instructions/work.md`, `.gitconfig.work`, and `.workrc`; its OpenCode
  additions must follow the same optional, work-owned installation pattern and must not overwrite personal dot-owned
  links.
- Existing `.dotrc` and work-dot `.workrc` files are modified in the current working trees. Preserve those changes and
  reconcile manually if the implementation touches either file.
- LiteLLM GitHub Copilot authentication and exact quota error semantics must be verified during implementation. If quota
  exhaustion is not distinguishable from other failures, narrow the fallback to confirmed retryable status/error classes
  or stop and surface the limitation rather than silently routing ambiguous failures to Zen.


### Confirmed decisions

- Personal `light` routes to GitHub Copilot first and falls back to OpenCode Zen after Copilot quota exhaustion, subject
  to verifying the provider's quota error semantics during implementation.
- Launcher-managed routers are the approved first-version lifecycle. Do not add persistent launchd or systemd services.
- The initial capability vocabulary is approved: `coding`, `analysis`, `tools`, and `large-context`.
