# Design Plan: Carve work-specific configuration into a private work-dot repository


## Goal

Split Tucker's dotfiles into two repositories with clear ownership boundaries. The existing public `dot`
repository keeps personal identity, generic tooling, and machine-agnostic shell/agent context. A new
private repository, `Tucker-Beck_mcgraw/work-dot` (GitHub Cloud), owns everything that is McGraw Hill-specific: work agent
context, work Git configuration, work shell environment, and credentials for work services (Jira,
Confluence, Datadog, and similar). A new CLI `wdt` mirrors the shape of `dt` and bootstraps the work
layer independently. `dt configure` cooperates with `wdt` when it is present but never depends on it.

Alongside the split, credential handling moves from ad-hoc files under `~/.config/` and
`~/.agents/credentials.json` to a settings-backed credentials structure owned by each CLI. Personal
credentials live under `dt`; work credentials live under `wdt`. Each CLI exposes a `creds` command
group with two operations: `creds fetch <key>` prints a single configured credential value to
stdout so scripts and shell aliases can consume it without shelling out to `jq` against a plaintext
file, and `creds set <key> <value>` writes an individual credential into the CLI's nested
credentials sub-model as the safe interactive/manual companion to the batch `settings bind`
migration path. The design explicitly accepts the risk of `creds fetch` printing credential values
in exchange for scripting ergonomics; `creds set`, by contrast, never echoes the value it writes.

Credentials here are application-owned configuration values persisted through each CLI's Typerdrive-backed
settings store. They are not a built-in Typerdrive "secrets" facility; the term "credentials" is used
throughout this plan to keep that distinction clear and to avoid implying a Typerdrive API surface that
this design does not verify.


## Acceptance Criteria


### Repository split and CLI shape


#### AC01: The private work repository exists and is self-contained

A new private repository `Tucker-Beck_mcgraw/work-dot` (on GitHub Cloud at
`https://github.com/Tucker-Beck_mcgraw/work-dot`) exists and contains every asset needed to bootstrap
the work layer on a fresh machine, including work agent context, work shell rc, work Git config, and
the `wdt` CLI package. Cloning `dot` alone does not surface any McGraw Hill-specific content.


#### AC02: The `wdt` CLI is installable from the private repository

Installing the `work-dot` package registers a `wdt` binary on PATH. `wdt --help` lists at least
`configure` and `creds` sub-commands. `wdt` has no runtime dependency on `dt` being installed
or on any file owned by `dot`; `wdt configure` establishes every directory, symlink, and shell rc
integration it needs on its own.


#### AC03: `wdt configure` bootstraps the work layer

Running `wdt configure` places or refreshes every work-owned symlink, dotfile source line, and
Git-config include needed for the work environment. It creates any missing parent directories for
its own targets and arranges for the work shell rc to be sourced by the login shell without relying
on `dt` to have run. It does not touch personal-only assets managed by `dt`.


#### AC04: `dt configure` invokes `wdt configure` when available

When `wdt` is present on PATH, `dt configure` invokes `wdt configure` as a final step. On success,
`dt configure` reports the work step succeeded and exits zero. On failure, `dt configure` reprints
`wdt configure`'s stdout and stderr under a labeled prefix that identifies the output as coming from
the work layer, and exits non-zero. When `wdt` is not on PATH, `dt configure` completes successfully
with no warning, no error, and no reference to work configuration in its output.


#### AC05: Neither CLI mutates the other's assets

`dt configure` never writes to any file owned by `work-dot`. `wdt configure` never writes to any file
owned by `dot`. Ownership is determined by which repository tracks the source of the link or copy.

----

### Agent context ownership

#### AC06: Work agent context lives only in the private repository

Work-specific agent guidance (McGraw Hill identity, Fusion team context, work service conventions,
work project inventory) lives in `work-dot`. `wdt configure` links it into the standard system-wide
agents instructions location so agent sessions read it automatically. `dot` contains no work agent
content.


#### AC07: Personal agent context stays in the public repository

Generic personal context (writing preferences, register, working hours, machine basics that are not
employer-specific) remains in `dot` and continues to be linked into the system-wide agents directory
by `dt configure`.


#### AC08: Both layers coexist without collision

When both repositories are installed, agent sessions see both personal and work instruction files in
the system-wide agents directory. Neither file overwrites or shadows the other; each has a distinct
filename that clearly identifies its origin.

----

### Git configuration

#### AC09: Generic Git config conditionally loads a work overlay

The generic Git config tracked in `dot` conditionally includes a work Git-config overlay for
repositories located under the work source root. When the overlay file does not exist, Git behaves
exactly as it does today for non-work repositories and prints no error.


#### AC10: The work Git overlay and shell rc are owned by `work-dot`

The work Git-config overlay file and the work shell rc file are tracked in `work-dot` and linked into
the home directory by `wdt configure`. They are not present in `dot` in any form.


#### AC11: Work shell rc defines the work environment

Sourcing the work shell rc at login exports the variable that names the work source root and defines
the shortcut for jumping to that root. The generic shell rc in `dot` no longer hardcodes any work
path, alias, or environment variable.


#### AC12: All stale `github.mheducation.com` references are gone

No file in either repository references the retired GHES hostname. The work Git overlay and the work
agent context describe work GitHub as GitHub Cloud under the `Tucker-Beck_mcgraw` account.

----

### Generic Jira retention and cleanup


#### AC13: The generic branch-pattern checkout stays in `dot`

`dt git cojira` and the shell alias `cojira` remain in `dot`. Their behavior is unchanged: checkout a
branch by pattern. Neither depends on Jira credentials or on `wdt`.


#### AC14: Generic Jira code in `dot` is identity-free

Any Jira client code that remains in `dot` contains no hardcoded email address, no hardcoded tenant
identifier, no hardcoded cloud ID, and no hardcoded project key. Every such value is read from
configuration at call time. Behavior that is meaningful only inside McGraw Hill's Jira tenant is not
present in `dot`.


#### AC15: Work-specific Jira behavior lives in `work-dot`

McGraw Hill Jira conventions (FUS project defaults, ADF issue templates, tenant URLs, cloud IDs) live
in `work-dot`, either as `wdt` sub-commands, agent instructions, or both. `dt` does not carry them.

----

### Credential configuration

#### AC16: `dt` owns personal credentials; `wdt` owns work credentials

Personal-account credentials are configured through `dt`'s settings store. Work-account credentials
(at minimum Jira, Confluence, and Datadog) are configured through `wdt`'s settings store. The two
stores are separate on disk and neither CLI can read the other's credentials.


#### AC17: Credentials are modeled as a nested settings structure

In each CLI, credentials are represented as a nested model within the application's primary settings
model (for example, a `credentials` attribute whose value is itself a structured model of named
credential entries) rather than as top-level credential key/value fields alongside unrelated settings.
The exact class names, module locations, and field names for individual credentials are left to
implementation planning; this AC fixes only the structural requirement that credentials nest under a
dedicated sub-model in the primary settings schema of both `dt` and `wdt`. Every `creds` sub-command
in either CLI operates against this nested sub-model exclusively and never reaches top-level or
arbitrary settings fields.


#### AC18: `dt creds fetch <key>` prints a personal credential to stdout

Running `dt creds fetch <key>` prints the value of the configured personal credential named `<key>`
on stdout with no surrounding formatting, so it composes with shell command substitution. Missing or
unset keys exit non-zero with an error on stderr and write nothing to stdout. The `<key>` argument
resolves against the nested credentials model defined by AC17.


#### AC19: `wdt creds fetch <key>` matches `dt creds fetch` exactly

Running `wdt creds fetch <key>` behaves identically to AC18 against the work credentials store: the
raw value is written to stdout with no surrounding formatting, a missing or unset key exits non-zero
with an error on stderr and writes nothing to stdout, and the exit codes match those used by `dt
creds fetch`. More generally, every `wdt creds` sub-command has the same contract as its `dt creds`
counterpart (including `creds set`, see AC27–AC28), differing only in which credentials store it
operates against.


#### AC20: Credential values are never committed

Neither repository tracks any credential value. Credential configuration is done at runtime through
each CLI's settings interface and stored in the user's local application config directory, not in
the repo.


#### AC21: `wdt configure` initializes but does not overwrite credentials

`wdt configure` is fully non-interactive. It first seeds any missing work credential entries under
the nested credentials model by creating them with empty placeholder values. After the seeding pass
completes, it walks the resulting entries and, for each credential whose value is empty or still a
placeholder, emits a per-credential notice to stderr naming the credential and directing the operator
to populate it — either individually through `wdt creds set <key> <value>` (the interactive/manual
companion, see AC28) or in batch through `wdt settings bind` (see AC24).
It never blocks for input and, absent any other error, exits successfully even when every credential
is still empty. On subsequent runs, `wdt configure` leaves existing non-empty, non-placeholder
credential values untouched. Re-running `wdt configure` never destroys a working credential.


#### AC22: Credential-file guidance is replaced

Agent instructions no longer direct readers to `~/.agents/credentials.json` or to repo-adjacent
credential files for work services. They direct readers to fetch credentials through the appropriate
CLI: personal credentials via `dt creds fetch <key>` (documented in `dot`) and work credentials via
`wdt creds fetch <key>` (documented in `work-dot`). The old credential-file guidance is removed from
`dot` entirely.


#### AC23: The risk of printing credentials is documented

Documentation for the `creds fetch` command in each CLI states plainly that the command prints a
credential value to stdout, that this is intentional for scripting, and that callers are responsible
for not logging or echoing the output. Documentation for `creds set` states plainly that the
command does not echo the credential value it just wrote to either stdout or stderr — success
output is a non-revealing acknowledgement only — so operators can paste values interactively
without worrying about the CLI itself leaking them to a terminal transcript.


#### AC24: Settings binding is performed before legacy credentials are removed

After both CLIs are installed and configured, Tucker runs `dt settings bind ...` to migrate or
configure personal settings and `wdt settings bind ...` to migrate or configure work settings. The
`settings bind` invocations must target the nested credentials sub-model established by AC17 (for
example, by addressing dotted paths such as `credentials.<name>` rather than top-level keys). This
binding step is a required checkpoint in the migration: no legacy credential source (in particular
`~/.agents/credentials.json`) is deleted until settings binding has succeeded for both CLIs and
`creds fetch` returns the expected values for every required key. The specific settings paths and
argument shapes surface during implementation planning.


#### AC25: Legacy `~/.agents/credentials.json` is removed only after validated migration

`~/.agents/credentials.json` remains present and ignored by both CLIs until the settings-binding and
credential-fetch validation described in AC24 complete successfully. Once validation passes for
every required personal and work credential, the file and all references to it are removed from the
working tree, from ignore rules where those rules exist solely to hide it, and from any remaining
agent or shell guidance. Deletion happens in a single, clearly identified migration step, not
incrementally.


#### AC26: Agent guidance documents the CLI-mediated credential retrieval path

Agent guidance tells agents how to retrieve credentials needed for resource access. Personal-credential
retrieval uses `dt creds fetch <key>`; work-credential retrieval uses `wdt creds fetch <key>`. No
agent-facing instruction directs an agent to read a plaintext credential file. Agent guidance does
not, by default, instruct agents to configure or set credentials (via `creds set`, `settings bind`,
or otherwise); credential population is an operator task. Existing agent guidance that has a
justified need to set a credential may retain that instruction, but no new agent-facing guidance is
added purely to expose the `creds set` surface. Generic and personal guidance lives in `dot`;
work-specific guidance lives in `work-dot`. Validation confirms both that stale
`~/.agents/credentials.json` references are gone from agent guidance and that an agent-facing
credential retrieval path is documented in each repository at the appropriate scope.


#### AC27: `dt creds set <key> <value>` writes a single personal credential

Running `dt creds set <key> <value>` writes `<value>` to the personal credential named `<key>` in
`dt`'s nested credentials sub-model (see AC17) and only that sub-model. `<key>` must resolve to a
field defined by the credentials sub-model; any other key — including a valid top-level settings
field, an arbitrary dotted path outside the credentials sub-model, or an unknown credential name —
causes the command to exit non-zero with a diagnostic on stderr and leaves settings on disk
completely unchanged. On success the command exits zero and prints a non-revealing acknowledgement
(for example, confirming that credential `<key>` was updated) without echoing `<value>` — or any
derived form of it — to stdout or stderr. `creds set` is the safe individual-credential companion
to interactive/manual configuration after `configure` emits missing-credential notices; it is not
a substitute for `settings bind`, which remains the batch migration mechanism (see AC24).


#### AC28: `wdt creds set <key> <value>` matches `dt creds set` exactly

Running `wdt creds set <key> <value>` behaves identically to AC27 against the work credentials
store: the same sub-model-only scoping, the same unknown-key failure mode with a diagnostic on
stderr and no settings mutation, the same non-revealing success acknowledgement, and matching exit
codes. The work and personal stores remain fully separate — `wdt creds set` cannot write into the
personal store and `dt creds set` cannot write into the work store.


#### AC29: `wdt creds` with no subcommand shows help and exits zero

Running `wdt creds` with no subcommand and no additional arguments displays the `creds` command
group's help output and exits zero. The `creds` group is a pure subcommand wrapper: it carries no
default action of its own, performs no credential read or write when invoked bare, and never
touches the credentials store. The help output produced by the bare invocation is the same help
output produced by `wdt creds --help`.


#### AC30: `dt creds` with no subcommand matches `wdt creds` exactly

Running `dt creds` with no subcommand and no additional arguments displays the `creds` command
group's help output and exits zero, with the same pure-wrapper contract as AC29 (no default
action, no store access, help output identical to `dt creds --help`). Whether `dt creds` exists
today or is added as part of this work, its bare-invocation behavior is aligned with `wdt creds`
so operators see one consistent contract across both CLIs.

----

## Architecture

### Two-repository ownership model

The system is split along a single axis: employer-neutral vs employer-specific. Everything that
would be true of Tucker's setup regardless of employer stays in `dot`. Everything that is true only
because he works at McGraw Hill moves to `work-dot`.

`dot` is the base layer. It installs unconditionally, works standalone, and knows nothing about
McGraw Hill. `work-dot` is an optional overlay. It assumes `dot` is already installed and layers
work-specific assets on top. Neither repository imports code from the other; the coupling is
runtime-only and mediated by the presence of the `wdt` binary on PATH.


### Configuration invocation flow

`dt configure` runs its existing bootstrap steps to completion. As a final step, it probes for `wdt`
on PATH. If `wdt` is absent, `dt configure` exits successfully with no work-related output — no
warning, no notice, no reference to the work layer at all.

If `wdt` is present, `dt configure` invokes `wdt configure` as a subprocess. On zero exit, `dt
configure` reports success for the work step and exits zero. On non-zero exit, `dt configure`
reprints the subprocess's stdout and stderr under a labeled prefix that identifies the output as
coming from the work layer, and exits non-zero itself.

`wdt configure` can also be run directly and is designed to stand on its own: it creates any
directories it needs, arranges for the work shell rc to be sourced by the login shell, and does not
read or write any file owned by `dot`. It therefore does not check for the presence of the base
layer. Running `wdt configure` on a fresh machine that has never run `dt configure` is not a
supported end-to-end workflow — the resulting environment will be missing the personal base — but
`wdt configure` itself does not fail on that basis.


### Agent context layout

The system-wide agents instructions directory holds one file per source of guidance. `dot` owns the
personal guidance file. `work-dot` owns the work guidance file. Agents read both when they are
present. The two files have distinct, self-describing names so neither shadows the other and it is
obvious in an agent session where a piece of guidance came from. Existing personal-only content
stays where it is; existing work-tainted content is split at the sentence level between the two
files during migration.


### Git configuration layering

The Git configuration model uses Git's built-in conditional `includeIf` mechanism. The generic
config in `dot` declares a conditional include for the work source root. The included file itself is
owned by `work-dot` and installed by `wdt configure`. When the included file is absent, Git silently
ignores the conditional include, so `dot` alone remains valid.

The work source root is a single well-known path under `~/src/`. `dot` references the root only
inside the conditional include declaration. The corresponding environment variable and directory
alias move to the work shell rc owned by `work-dot`.


### Credentials model

Each CLI persists credentials through its own Typerdrive-backed settings file in its own application
config directory. The two directories are distinct per CLI, so personal and work credentials do not
mix.

The credentials structure is a nested sub-model on each CLI's primary settings model — that is,
credentials hang off a dedicated attribute of the top-level settings object rather than being
scattered as top-level fields alongside unrelated settings. This nested shape is a structural
requirement of the design; the concrete Python class and field names are implementation-planning
concerns.

`configure` in each CLI ensures the settings file exists and that every expected credential entry is
present under the nested credentials model, using empty or placeholder values for anything not
already set. It never overwrites a non-empty value.

A `creds` sub-command group on each CLI provides two operations that both operate exclusively
against the nested credentials sub-model: a `fetch` operation that reads a named credential and
prints its value to stdout (see AC18–AC19), and a `set` operation that writes `<value>` to a named
credential (see AC27–AC28). `creds set` is scoped to the credentials sub-model — it cannot address
top-level or arbitrary settings fields, and unknown credential names fail non-zero with a
diagnostic on stderr and no on-disk mutation. On success, `creds set` prints a non-revealing
acknowledgement and never echoes the value it just stored. It exists as the safe individual
companion for interactive/manual configuration after `configure` emits missing-credential notices;
it is not a substitute for `dt settings bind` / `wdt settings bind`, which remain the batch
migration mechanism used to populate many credentials at once against Tucker's authoritative
values (see the rollout section). Personal and work stores stay fully separate: `dt creds` operates
only on `dt`'s store and `wdt creds` operates only on `wdt`'s store, with no cross-CLI access in
either direction.

Neither the `fetch` nor `set` operation is a Typerdrive built-in. Both are application-owned
sub-commands on `dt` and `wdt` that reach into each CLI's own settings model; this plan makes no
claim about a Typerdrive-provided credentials facility.

The precise mechanism by which the CLI reaches into a nested settings sub-model — whether that uses
an existing Typerdrive primitive, dotted-path settings binding, or a thin wrapper written for these
CLIs — is treated as an implementation constraint. This design does not assume a specific Typerdrive
API surface for credential storage; the implementation plan is responsible for verifying what
Typerdrive provides and closing the gap if any.

Consumers that previously read `~/.agents/credentials.json` directly switch to invoking the
appropriate `creds fetch` command. Shell scripts and agent instructions are updated to use command
substitution against the CLI rather than `jq` against a JSON file.


### Migration inventory

This is the conceptual inventory of what moves, stays, or is deleted. Exact paths and rename choices
are for the implementation plan.

| Category                                                | Current home   | Destination                                                    |
| ------------------------------------------------------- | -------------- | -------------------------------------------------------------- |
| Personal identity and register guidance                 | `dot`          | `dot` (stays)                                                  |
| McGraw Hill / Fusion / Assess identity                  | `dot`          | `work-dot`                                                     |
| Generic machine context (OS, shell, editor)             | `dot`          | `dot` (stays)                                                  |
| Work service credential instructions                    | `dot`          | `work-dot` (as CLI-mediated guidance)                          |
| Generic Git config and personal include                 | `dot`          | `dot` (stays)                                                  |
| Work Git-config overlay                                 | `dot`          | `work-dot`                                                     |
| Retired GHES `insteadOf` rule                           | `dot`          | Deleted                                                        |
| Work source-root env var and `cdwork` alias             | `dot` shell rc | `work-dot` shell rc                                            |
| Generic branch-pattern checkout (`cojira`)              | `dot`          | `dot` (stays)                                                  |
| Generic Jira client code                                | `dot`          | `dot` (stays, identity stripped)                               |
| Hardcoded work Jira identity in client code             | `dot`          | Deleted from `dot`; moved to `work-dot`                        |
| Plaintext credentials file guidance                     | `dot`          | Deleted                                                        |
| Personal credential values                              | ad-hoc files   | `dt` credentials sub-model (batch: `dt settings bind`; individual: `dt creds set`)         |
| Work credential values (Jira, Confluence, Datadog, etc.)| ad-hoc files   | `wdt` credentials sub-model (batch: `wdt settings bind`; individual: `wdt creds set`)      |
| `~/.agents/credentials.json` plaintext credentials      | `~/.agents/`   | Deleted after validated CLI migration                          |
| Agent-facing credential-file read instructions          | `dot` agents   | Replaced by `dt`/`wdt creds fetch` guidance                    |


### Rollout and compatibility

The two repositories can be developed in either order but must be released so that `dot` alone
remains fully functional at every point. Concretely, the `dot` changes remove all work-specific
content and add the conditional cooperation with `wdt`; the `work-dot` repository is created
alongside and picks up the removed content. On machines where `work-dot` is not yet installed, the
next `dt configure` succeeds and simply lacks the work overlay.

There is no backward-compatibility surface to preserve for external consumers. The only user of both
repositories is Tucker, on a small number of machines under his direct control, so a coordinated
rollout is acceptable.

Credential migration follows a rollback-safe order that keeps the legacy credential source usable
until the CLI-backed store is proven working:

1. Deploy and install both CLIs (`dt` and `wdt`) with their nested credentials sub-models and
   `creds` sub-command groups in place.
2. Run `dt settings bind ...` and `wdt settings bind ...` — with argument shapes that target the
   nested credentials sub-model — to populate the personal and work credential stores from Tucker's
   authoritative values. `settings bind` is the batch migration mechanism used here; the
   per-credential `dt creds set` / `wdt creds set` commands are the individual-configuration
   companion for later interactive/manual updates (for example, rotating a single credential or
   filling in one that `configure` flagged as missing) and are not used as a substitute for the
   batch migration validation performed in this step.
3. Validate `dt creds fetch` and `wdt creds fetch` return the expected values for every key
   required by shell aliases, agent guidance, and scripts.
4. Only after that validation passes, delete `~/.agents/credentials.json` and remove every remaining
   reference to it from `dot` (guidance, ignore entries kept only for it, and any residual scripts).

Until step 4 completes, `~/.agents/credentials.json` remains on disk, ignored by both CLIs and
untouched by `configure` in either CLI, so the previous workflow stays available as a fallback.


### Testing and validation strategy

Validation happens at three levels.

At the unit level, both CLIs retain their existing test coverage. New behavior — the `wdt`
detection branch in `dt configure`, the credential-seeding logic in `wdt configure` against the
nested credentials sub-model, and the `creds fetch` and `creds set` commands in both CLIs — gets
targeted unit tests. Credential-store tests use a temporary application config directory so real
credentials are never touched. Tests must exercise the nested model shape explicitly, confirming
that credentials resolve through the sub-model and not through top-level settings fields. `creds
set` tests specifically cover: writing a known credential key updates only the nested credentials
sub-model and leaves the rest of settings byte-identical; passing an unknown credential key, a
top-level settings field, or a dotted path outside the credentials sub-model exits non-zero with a
diagnostic on stderr and leaves the settings file byte-identical to its pre-invocation state;
successful invocations neither print the written value nor any derived form of it to stdout or
stderr; and `dt creds set` never mutates `wdt`'s settings file and vice versa. Bare-invocation
tests cover both CLIs: running `dt creds` and `wdt creds` with no subcommand exits zero, emits the
respective group's help output on stdout, and leaves the credentials store byte-identical to its
pre-invocation state (confirming the group carries no default action and does not read or write
credentials when invoked bare).

At the integration level, `dt configure` is exercised on a scratch home directory in three modes:
with `wdt` absent from PATH (expected: succeeds silently for the work layer), with a stub `wdt` on
PATH that exits zero (expected: `dt configure` invokes it, reports work-step success, and exits
zero), and with a stub `wdt` on PATH that exits non-zero (expected: `dt configure` reprints the
stub's stdout and stderr under a labeled prefix and exits non-zero). `wdt configure` is exercised
on a scratch home directory to confirm it seeds missing credentials under the nested sub-model,
preserves existing credential values on re-run, installs the work overlay, and does not touch
personal-owned files.

At the manual acceptance level, the split is verified on Tucker's own machine by running
`dt configure` alone, confirming the work layer is inert, then installing `work-dot`, running
`wdt configure`, and confirming that agent sessions see the work instructions file, that Git in a
work repo picks up the overlay, and that `creds fetch` returns the expected values for the seeded
credentials.

Manual acceptance also covers the credential migration path end-to-end: run `dt settings bind ...`
and `wdt settings bind ...` against Tucker's real values (using argument shapes that address the
nested credentials sub-model), confirm `dt creds fetch` and `wdt creds fetch` return each required
key, then delete `~/.agents/credentials.json` and re-run the workflows that previously depended on
it to confirm they succeed against the CLI-backed store. Manual acceptance also spot-checks
`dt creds set` and `wdt creds set` end-to-end: setting a known credential updates its stored value
(verified via `creds fetch`) without echoing the value to the terminal, and setting an unknown key
(or a non-credentials settings field) fails non-zero with a stderr diagnostic and no visible
settings change. Acceptance additionally verifies that agent guidance no longer references
`~/.agents/credentials.json` or any other plaintext credential file, and that each repository
documents an agent-facing credential retrieval path (`dt creds fetch` in `dot`, `wdt creds fetch`
in `work-dot`) at the appropriate scope.


### Risks and decisions

The design accepts three risks explicitly.

First, `creds fetch` prints credential values to stdout. This is deliberate: the alternative — no
scripting affordance — is worse for the workflows Tucker actually runs. The mitigation is a plain
statement in the command's documentation. `creds set`, by contrast, is defined to never echo the
value it just wrote to stdout or stderr, so the interactive/manual configuration path does not
introduce a second, avoidable leak channel.

Second, the two repositories can drift. `dt` could accidentally regain work-specific content, or
`work-dot` could accidentally take on generic content. The mitigation is the explicit migration
inventory above and reviewer discipline; there is no mechanical enforcement.

Third, the exact shape of Typerdrive's settings API — in particular, how it addresses fields inside
a nested sub-model from `settings bind` and how it exposes reads and writes to a CLI sub-command —
is not verified at design time. If Typerdrive's current surface does not accommodate the nested
credentials model, a stdout-printing fetch against it, or a sub-model-scoped `creds set` write, the
implementation plan must either wrap the existing surface or extend it. This is called out as a
design-time constraint rather than a runtime unknown.

Decisions locked in by this plan:

- Two repositories, not a monorepo with a private submodule. Separation is enforced by repository
  boundary, not by directory convention.
- Two CLIs, not one with a `--work` flag. Ownership tracks the CLI that installs the asset.
- Cooperation is via subprocess invocation on PATH, not via a plugin API. The base repository has
  no compile-time knowledge of the overlay.
- Generic Jira code stays in `dot`. The public repository retains a working Jira client scaffold
  that any employer's tenant can configure; it just carries no employer identity of its own.
- Credentials are an application concern, modeled as a nested sub-model of each CLI's primary
  settings model and surfaced through an application-owned `creds` command group. They are not
  treated as a built-in Typerdrive "secrets" facility, and this design makes no claims about such
  a facility existing.
- The `creds` command group contains both `fetch` (script-facing, prints the value) and `set`
  (interactive/manual-facing, writes a single credential into the nested sub-model without echoing
  the value). `settings bind` remains the batch migration mechanism; `creds set` is the individual
  companion for later single-credential updates, not a replacement for batch migration validation.


## Unknowns

- None at the design level. Whether Typerdrive's current settings surface directly supports binding
  into, reading from, and writing to a nested credentials sub-model as described here — including
  the sub-model-scoped `creds set` write path — is an implementation-planning question, not a
  design unknown. If a gap surfaces during implementation planning, it is resolved there as a
  scoped decision (wrap or extend the existing surface).


## Technical Notes

- The base repository must remain publishable to public GitHub at every commit on the migration
  branch. No commit may transiently contain work-identifying material that was not already there.
- The private repository is hosted at `https://github.com/Tucker-Beck_mcgraw/work-dot` on GitHub
  Cloud. Access is via Tucker's work GitHub account (`Tucker-Beck_mcgraw`). The public repository
  continues to use his personal account.
- The work source root is `~/src/mhe/` and remains so. The directory name is not itself sensitive
  and can appear in the public `dot` repository inside the conditional Git include declaration.
- Typerdrive is already a dependency of `dot` and will be a dependency of `work-dot`. Its exact
  settings-binding and settings-read API surface — especially with respect to nested sub-models —
  is a constraint for implementation planning, not for this design. This plan intentionally makes
  no claim about a Typerdrive-provided secrets primitive; credentials here are ordinary application
  settings modeled as a nested structure.
- Settings migration is performed via `dt settings bind ...` and `wdt settings bind ...`, with
  argument shapes chosen so they can address individual credential entries inside the nested
  credentials sub-model rather than top-level keys. This design does not fix the specific dotted
  paths, class names, or field names; implementation planning enumerates the required keys from
  the current `~/.agents/credentials.json` and from any other ad-hoc credential sources still in
  use, and settles on the exact `settings bind` syntax. `settings bind` remains the batch
  migration mechanism; the individual `dt creds set <key> <value>` and
  `wdt creds set <key> <value>` commands (AC27–AC28) are the application-owned single-credential
  companion used for interactive/manual updates after migration, and they are scoped to the
  nested credentials sub-model only — they never touch top-level or arbitrary settings fields,
  and they never echo the written value.
- The legacy `~/.agents/credentials.json` file is out of scope for `dt configure` and `wdt
  configure`: neither CLI reads it, writes it, nor removes it. It is deleted by an explicit
  migration step gated on successful `creds fetch` validation, as described in the rollout
  section.
- Agent-guidance updates that remove `~/.agents/credentials.json` references and add
  `dt creds fetch` / `wdt creds fetch` instructions are in scope for this migration. Agent
  guidance covers credential *retrieval* only (`creds fetch`); it does not, by default, instruct
  agents to configure credentials via `creds set` or `settings bind`. Where existing agent
  guidance has a justified need to set a credential, that instruction may remain, but no new
  agent-facing set guidance is added by this migration. Work agent guidance ships in `work-dot`;
  personal and generic agent guidance ships in `dot`.
- No implementation plan should be produced from this design until the design has been reviewed
  and approved.
