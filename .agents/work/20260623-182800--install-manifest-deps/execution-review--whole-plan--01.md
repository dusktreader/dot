# Execution Review: Install manifest dependency ordering


## Source Artifacts

- **Implementation journal**: `.agents/work/20260623-182800--install-manifest-deps/implementation-journal.md`
- **Implementation plan**: `.agents/work/20260623-182800--install-manifest-deps/implementation-plan.md`


## Scope

**whole-plan** — Iteration 01


## Issue Summary

- **Critical**:    0
- **Significant**: 2
- **Trivial**:     2


## Verification Evidence

```
Linter:   uv run ruff check src tests           → 27 errors (1 in configure.py: E741 ambiguous
                                                   variable `l` at line 412; 26 pre-existing
                                                   errors in other files unrelated to this feature)
Types:    uv run ty check                        → 46 diagnostics (none in configure.py or
                                                   in new test code for this feature; all
                                                   pre-existing in other modules)
Tests:    uv run pytest tests/test_configure.py  → 43 passed, 0 failed
Tests:    uv run pytest                          → 233 passed, 0 failed, 2 warnings
Coverage: uv run pytest (whole suite)            → 75% (above 70% threshold)
Coverage: uv run pytest tests/test_configure.py  → 20% (below 70%; configure.py at 38% due to
                                                   many methods with no mocked subprocess tests;
                                                   this is a pre-existing condition, not
                                                   introduced by this feature)
```

The one ruff error in `configure.py` (`E741` at line 412) is in `_update_dotfiles`, which is
pre-existing and outside the scope of this feature. No new lint errors were introduced. All
type errors are in files unrelated to this feature.


## Acceptance Criteria Verification

| AC        | Status | Evidence                                                                                             |
| --------- | ------ | ---------------------------------------------------------------------------------------------------- |
| **Task 01**                                                                                                               |
| 01/AC01   | ✓      | `configure.py:53` — `depends_on` field declared; `test_configure.py:110–112`                         |
| 01/AC02   | ✓      | `configure.py:53`; `test_configure.py:114–121`                                                       |
| 01/AC03   | ✓      | `configure.py:53` (default_factory); `test_configure.py:110–112`                                     |
| 01/AC04   | ✓      | Pydantic handles serialization; `test_configure.py:114–131` load round-trips correctly               |
| 01/AC05   | ✓      | All existing `TestToolSpecs` tests pass; 43/43 suite green                                           |
| **Task 02**                                                                                                               |
| 02/AC01   | ✓      | `configure.py:91–129`; `test_configure.py:224–232` (`test_resolve_tool_order__no_dependencies_returns_valid_order`) |
| 02/AC02   | ✓      | `configure.py:91–129`; `test_configure.py:234–243` (`test_resolve_tool_order__simple_chain_abc`) and `test_configure.py:245–256` |
| 02/AC03   | ✓      | `configure.py:100–103`; `test_configure.py:275–283` (`test_resolve_tool_order__unknown_dependency_raises_error`) |
| 02/AC04   | ⚠      | `configure.py:121–125` raises `DotError` with cycle message, but the message format buries tool names inside a Python tuple string rather than the clean `A → B → C` format specified in the plan. Test only asserts `"Cycle detected"` in message, not that tool names are clearly surfaced. See **S01**. |
| 02/AC05   | ✓      | `configure.py:104–108`; `test_configure.py:296–302` (`test_resolve_tool_order__self_dependency_raises_error`) — self-dependency detected before `TopologicalSorter`, raises clearly |
| 02/AC06   | ✓      | `configure.py:91–92`; `test_configure.py:220–222` (`test_resolve_tool_order__empty_list_returns_empty`) |
| **Task 03**                                                                                                               |
| 03/AC01   | ✓      | `configure.py:282–283`; `test_configure.py:590–603` (`test_install_tools__calls_resolve_tool_order`) |
| 03/AC02   | ⚠      | `configure.py:282–283` iterates `resolved_tools`; however the integration test for end-to-end install order (`_install_tools` iterating resolved order with A→B→C) is absent — the test only verifies `resolve_tool_order` was called, not that the install loop actually respects the order under real conditions. See **S02**. |
| 03/AC03   | ✓      | `configure.py:282` — `resolve_tool_order` is called before the loop; any raised `DotError` propagates through `DotError.handle_errors()` in `install_dot()` at line 745 |
| 03/AC04   | ✓      | `configure.py:292–294` — check-command skip path is inside the loop over `resolved_tools`, so order is not disturbed |
| 03/AC05   | ✓      | `configure.py:285–287` — gui_only skip is inside the loop, order not disturbed                       |
| 03/AC06   | ✓      | All 43 configure tests pass                                                                          |
| **Task 04**                                                                                                               |
| 04/AC01   | ✓      | `etc/install.yaml:254–263` — `asdf` entry has no `depends_on` field                                 |
| 04/AC02   | ✓      | `etc/install.yaml:264–275` — `asdf-go` entry has `depends_on: [asdf]`                               |
| 04/AC03   | ✓      | `etc/install.yaml:287–297` — `usql` entry has `depends_on: [asdf-go]`                               |
| 04/AC04   | ✓      | `test_configure.py:179–211` loads the file without error; full suite passes                          |
| 04/AC05   | ✓      | `test_configure.py:197–211` — verifies dependency fields and `resolve_tool_order` produces correct chain |
| **Task 05**                                                                                                               |
| 05/AC01   | ✓      | `test_configure.py:224–232` — multiple independent tools produce valid topological set               |
| 05/AC02   | ⚠      | `test_configure.py:569–603` verifies `resolve_tool_order` was called, but does not assert the actual installation order of tools A → B → C. The mock returns the raw tool list unchanged, so the test does not exercise the order produced by the resolver. See **S02**. |
| **Task 06**                                                                                                               |
| 06/AC01   | ✓      | 43/43 configure tests pass; full suite 233/233 pass                                                  |
| 06/AC02   | ✓      | 11 new tests pass                                                                                    |
| 06/AC03   | ✓      | No new ruff errors introduced in `configure.py` or `tests/test_configure.py`                         |
| 06/AC04   | ✓      | No new `ty check` errors in `configure.py` or `tests/test_configure.py`                              |
| 06/AC05   | ✓      | All pre-existing `InstallManifest` and `DotInstaller` tests pass unchanged                           |
| 06/AC06   | ✓      | `configure.py:699` — `_create_local_agents_file` uses `self.install_manifest.tools` (raw YAML order) |


## Scope Verification

| File                          | Justified By                          | Status |
| ----------------------------- | ------------------------------------- | ------ |
| `src/dot_tools/configure.py`  | Task 01 (ToolSpecs), Task 02 (resolver), Task 03 (_install_tools) | ✓ |
| `tests/test_configure.py`     | Tasks 01–06 (all test requirements)   | ✓      |
| `etc/install.yaml`            | Task 04 (seed manifest)               | ✓      |


## Prior Review Resolution

*Not applicable — this is iteration 01.*


## Findings

### Summary

| Finding | Title                                                               | Outcome |
| ------- | ------------------------------------------------------------------- | ------- |
| S01     | Cycle error message buries tool names; format deviates from plan spec |        |
| S02     | Integration test does not verify actual install ordering            |         |
| T01     | Redundant `pydantic.Field` annotation on `depends_on`               |         |
| T02     | Extra blank line at `test_configure.py:315`                         |         |


### Significant

#### S01: Cycle error message buries tool names; format deviates from plan spec

##### Where

`src/dot_tools/configure.py:123–125`


##### Issue

The plan's Technical Notes section specifies the cycle error message format as:

```
"Cycle detected in tool dependencies: asdf-go → usql → asdf-go. Please check your dependency declarations."
```

The implementation produces:

```
"Cycle detected in tool dependencies. Please check your dependency declarations. Error: ('nodes are in a cycle', ['asdf-go', 'usql', 'asdf-go'])"
```

The raw Python tuple representation `('nodes are in a cycle', [...])` from `CycleError.__str__` is
user-hostile: it leaks internal stdlib internals, uses square-bracket list notation instead of `→`
arrows, and puts the tool names at the end rather than inline with the diagnostic. The design plan
explicitly calls out that error messages are part of the contract and must name offending entries
clearly enough to find them in YAML without reading source code.

The test at `test_configure.py:292–294` asserts only `"Cycle detected" in str(exc_info.value)`,
so this deviation is untested.


##### Impact

A manifest author who triggers a cycle will receive a confusing message with raw Python data
structures. This degrades the usability guarantee stated in the design plan (AC06 of the design:
"raises a clear error that names the tools involved in the cycle").


##### Fix

Extract the cycle participants from `CycleError.args[1]` (the list of tool names) and format
them as an arrow-separated chain:

```python
except CycleError as e:
    cycle_nodes = e.args[1] if len(e.args) > 1 else []
    chain = " → ".join(str(n) for n in cycle_nodes)
    raise DotError(
        f"Cycle detected in tool dependencies: {chain}. Please check your dependency declarations."
    )
```

Also strengthen the test to assert the tool names appear in the message:

```python
assert "a" in str(exc_info.value)
assert "b" in str(exc_info.value)
assert "c" in str(exc_info.value)
```

----

#### S02: Integration test does not verify actual install ordering

##### Where

`tests/test_configure.py:569–603` (`test_install_tools__calls_resolve_tool_order`)


##### Issue

The test patches `resolve_tool_order` and asserts it was called, but `mock_resolve.return_value`
is set to `installer.install_manifest.tools` — the original, unresolved order. The mock bypasses
the resolver entirely and returns the raw list, so the test never exercises whether the loop
correctly iterates resolved order when the resolver returns a different sequence.

The plan (Task 03, Step 7 and Task 05, AC02) requires a test that:
- Creates a manifest with a dependency chain (A, B→A, C→B) in reverse order in the YAML.
- Calls `_install_tools()` without patching `resolve_tool_order`.
- Verifies the subprocess calls occur in resolved order (A, B, C).

Without this test, the key behavioral guarantee — that `_install_tools` actually installs in
resolved order — is covered only by integration (visual) confidence, not by an automated assertion.


##### Impact

If a future refactor accidentally breaks the loop to iterate `self.install_manifest.tools`
instead of `resolved_tools`, no test would catch the regression.


##### Fix

Add a test that:
1. Creates a manifest with tools declared in non-dependency order: C→B, B→A, A (no dep).
2. Mocks `subprocess.run` to return `returncode=1` (so tools appear not-yet-installed) and mocks
   `subprocess.Popen` for the install step, capturing the tool name from each `spinner` context
   or from call order.
3. Calls `_install_tools()` directly (without patching `resolve_tool_order`).
4. Asserts the order of subprocess calls follows A, B, C.

Alternatively, capture the tool names passed to the `spinner` context manager to verify order,
or inspect the sequence of `subprocess.run` calls with the check commands.

----

### Trivial

#### T01: Redundant `pydantic.Field` in `depends_on` field definition

##### Where

`src/dot_tools/configure.py:53`


##### Issue

The `depends_on` field is declared as:

```python
depends_on: Annotated[list[str], pydantic.Field(default_factory=lambda: [])] = pydantic.Field(default_factory=lambda: [])
```

`pydantic.Field(default_factory=...)` appears twice — once inside `Annotated[...]` and once as the
default value assignment. Pydantic 2 honours either form; having both is redundant and inconsistent
with all other fields in the same file that use only one form. `ServiceSpecs.args` at line 60 uses
`Annotated[list[str], pydantic.Field(default_factory=lambda: [])]` with no `= pydantic.Field(...)`,
which is the canonical pattern in this codebase.


##### Fix

Choose one form. The `Annotated` form matches `ServiceSpecs.args` and the rest of the file:

```python
depends_on: Annotated[list[str], pydantic.Field(default_factory=lambda: [])]
```

----

#### T02: Spurious blank line at `test_configure.py:315`

##### Where

`tests/test_configure.py:315`


##### Issue

There is an extra blank line between the end of `TestResolveToolOrder` and the
`TestDotInstallerInit` class. Two blank lines between top-level classes is the Python standard
(PEP 8); three are present here.


##### Fix

Remove the extra blank line.

----

## Skills Applied

- `review-implementation-execution`: global fallback


## Decision

**BLOCKED — CHANGES REQUIRED**

S01 and S02 must be resolved before this review can be approved. Both address substantive
gaps: one is a user-facing error message quality regression against the plan's explicit
contract, the other is a behavioral test gap that leaves the core ordering guarantee
unverified by automation. T01 and T02 may be applied in the same pass.
