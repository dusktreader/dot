# Design Plan: Install manifest dependency ordering


## Goal

Allow each tool in the install manifest to declare which other tools it depends on, and have
`dt configure` derive the actual install order from those declarations instead of relying on the
order in which entries appear in the YAML file. Today, the manifest is processed strictly
top-to-bottom; if one tool requires another to be installed first, the only way to express that is
to physically move it lower in the file, which is fragile and easy to break when the manifest is
edited.

After this change, manifest authors describe relationships ("X depends on Y") rather than positions
("X must appear below Y"). The installer reads those relationships, computes a valid ordering,
fails fast if the declared graph is inconsistent, and then installs entries in the computed order.
Manifests that declare no dependencies behave exactly as they do today, so this is a purely
additive feature.


## Acceptance Criteria


### Manifest schema


#### AC01: Tool entries may declare dependencies on other tools

Each tool entry in the install manifest accepts an optional list of names referring to other tool
entries in the same section. A tool with no declared dependencies behaves exactly as it does today.


#### AC02: Manifests without any declared dependencies are unchanged

A manifest that uses none of the new dependency-declaration mechanism produces exactly the same
install behavior as before this feature: the same entries run, in an order consistent with the
file as-written.


#### AC03: The shipped manifest exercises the new mechanism

The repository's own install manifest declares at least one realistic dependency chain to prove
the feature end-to-end. Specifically, the asdf-go entry depends on asdf, and the usql entry
depends on asdf-go, so the three entries form a chain that the installer must respect.

----


### Install ordering


#### AC04: Tools install in an order consistent with their declared dependencies

When `dt configure` runs the tools section, each tool is installed only after every tool it
declares as a dependency has already been processed. The ordering is computed once, before any
tool runs, and applied to the whole tools section.


#### AC05: Skipped tools do not change the order of remaining tools

A tool whose check command exits 0 (already installed) or that is skipped for another reason
(for example, a gui-only tool on a headless machine) is omitted from the execution run without
affecting the position of other tools in the resolved order. The resolved order computed before
execution remains unchanged regardless of how many tools are skipped.

----


### Error handling


#### AC06: A dependency cycle aborts the run before anything is installed

When the declared tool dependencies form a cycle (for example, A depends on B, B depends on C, C
depends on A), `dt configure` raises a clear error that names the tools involved in the cycle
and exits without running any tool installation.


#### AC07: An unknown dependency name aborts the run before anything is installed

When a tool declares a dependency on a name that is not present in the tools section of the
manifest, `dt configure` raises a clear error that names both the tool making the declaration
and the missing dependency, and exits without running any tool installation.


#### AC08: A self-dependency is treated as a cycle

When a tool declares itself as one of its own dependencies, `dt configure` raises the same class
of cycle error as in AC06. This case is called out explicitly because it is the smallest
possible cycle and the most common authoring mistake.

----


## Architecture

The change touches three conceptual layers of the installer: the manifest schema, an order
resolver that sits between manifest loading and execution, and the existing tool execution loop.
The execution loop does not change its per-tool behavior; it simply iterates over a resolved,
ordered sequence instead of the raw manifest sequence.


### Manifest schema enrichment

The tool entry type gains an optional dependency-list field. The field is a list of names matching
other tool entries in the same section. Loading a manifest that omits the field on every entry
produces the same in-memory representation that today's loader produces, which is what makes the
change backward compatible at the data layer.


### Dependency resolver

A new component takes the raw list of tool entries and returns an ordered list in which every
tool appears after all of its declared dependencies. The resolver has three responsibilities.

First, it validates the graph by confirming that every declared dependency name refers to a tool
in the same section. Names that do not resolve are surfaced as authoring errors before any
ordering work begins.

Second, it detects cycles. The resolver refuses to produce an order when the declared
dependencies form a cycle, and it surfaces the offending tools so the author can locate the
problem.

Third, it produces a valid order. Any topologically valid ordering satisfies the contract —
every tool appears after all of its declared dependencies. No tiebreak policy is imposed on
independent tools.

The resolver operates on the tools section only. There is no cross-section dependency mechanism
in this feature, and the settings section continues to run in YAML order as it does today.


### Execution loop

The tool installation loop changes in exactly one way: instead of iterating over the raw tools
list from the manifest, it iterates over the resolved order produced by the dependency resolver.
Per-tool logic — the check command, the platform-specific script selection, the
skip-on-check-success behavior, and the gui-only handling — is unchanged.


### Failure gate

Validation and cycle detection happen before any tool in the tools section runs. A bad
declaration aborts the run before any tool is installed, so the user never sees a partial run
caused by a malformed manifest.


### Data flow

1. `dt configure` loads the manifest into the existing in-memory model. Tool entries carry their
   optional dependency declarations alongside the existing fields.
2. Before the tool installation phase begins, the resolver consumes the tool entries and
   returns either an ordered list or an actionable error.
3. The tool installation phase iterates over the ordered list. Skip decisions (check passed,
   gui-only headless) are made per tool as today.
4. The settings phase runs afterward in YAML order, unchanged by this feature.

----


## Technical Notes


### Settings are out of scope for this iteration

Settings entries share a similar name/check/scripts shape with tools, but they do not gain a
dependency mechanism in this feature. The settings phase continues to run in YAML order. If a
future need for settings dependencies emerges, the resolver designed here can be reused without
schema upheaval.


### The local-agents stub continues to list tools in YAML order

The local-agents stub created by `dt configure` lists installed tools in the order they appear in
the in-memory manifest. This feature does not change that listing's ordering source; the stub
remains in YAML order even though the install loop runs in resolved order. The two orderings are
allowed to differ.


### Topological sort is a stdlib primitive

Python's standard library exposes a topological sort that handles both ordering and cycle
detection. The resolver is expected to wrap that primitive rather than introduce a hand-rolled
graph algorithm.


### The seeded dependency chain is most meaningful on Linux

The shipped manifest's `usql` entry installs via `go install` on Linux but via MacPorts on
macOS. The declared dependency on `asdf-go` (and transitively `asdf`) is therefore strictly
necessary for the Linux path and effectively a no-op for the macOS path, where the chain is
satisfied by MacPorts. The dependency declaration is still correct on both platforms because
declaring more dependencies than strictly needed only constrains ordering — it cannot cause a
failure on its own.


### No effect on other manifest sections

Linking, copying, mkdir, dotfile sourcing, SSH key generation, GitHub CLI login, and service
registration are unaffected by this feature. The manifest sections that drive those steps do
not gain a dependency mechanism in this iteration.


### Error messages are part of the contract

The cycle error and the unknown-dependency error are the only new user-facing failure modes
this feature introduces. Both must name the offending entries clearly enough that the author
can locate the problem in the YAML without needing to read the installer's source. This is
called out because vague graph errors are a common pitfall when bolting dependency resolution
onto a previously linear workflow.
