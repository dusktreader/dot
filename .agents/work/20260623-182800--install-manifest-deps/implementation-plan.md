# Implementation Plan: Install manifest dependency ordering

Add support for declaring dependencies between tools in the install manifest and have
`dt configure` compute and respect a topologically sorted installation order. This feature
makes the manifest robust against insertion-order fragility by exposing tool relationships
as data rather than relying on YAML position.


## Goal

Implement dependency resolution for the tools section of the install manifest. Tool entries
will gain an optional `depends_on` field listing other tool names they require. A new
`resolve_tool_order()` function will validate and topologically sort the dependency graph
using Python's `graphlib.TopologicalSorter`, detecting cycles and unknown dependencies as
validation errors before any tool runs. The install loop in `_install_tools()` will iterate
over the resolved order instead of the raw manifest order. The feature is backward compatible:
manifests with no dependencies behave identically to today.


## Project Commands

### Run quality gate

Command:

```shell
uv run ruff check src tests
uv run ty check
uv run pytest
```

Expected Output:

All linting passes, no type errors, and all tests pass including new tests for dependency
resolution.


### Run tests

Command:

```shell
uv run pytest tests/test_configure.py -v
```

Expected Output:

All tests pass, including tests for `ToolSpecs` with dependencies, cycle detection, unknown
dependency errors, and order resolution.


### Install locally and test manually

Command:

```shell
uv sync
dt configure --root . --override-home /tmp/test_home
```

Expected Output:

Installation completes successfully. Tools that have dependencies are installed after their
dependencies. The setup can be repeated and idempotent: tools marked as already installed are
skipped, and the resolved order is deterministic.

----

## Project Standards

- [Python package structure](../../.dot_agents/dot.md)
- [Installation manifest schema](../../etc/install.yaml)
- [Test patterns in `tests/test_configure.py`](../../tests/test_configure.py)


## Relevant Skills

- `execute-implementation-plan`
- `review-implementation-execution`


## Execution


### 01: Update the ToolSpecs model to accept dependencies

Add an optional `depends_on` field to `ToolSpecs` to declare which other tools a tool requires.
Ensure the field defaults to an empty list and loads correctly from YAML.


#### Acceptance Criteria

- AC01: `ToolSpecs` has an optional `depends_on` field that defaults to an empty list.
- AC02: A tool entry with `depends_on: [foo, bar]` in YAML loads with `depends_on == ["foo",
  "bar"]`.
- AC03: A tool entry without `depends_on` in YAML loads with `depends_on == []`.
- AC04: The field serializes correctly when the manifest is loaded via pydantic.
- AC05: Existing tests for `ToolSpecs` still pass.


#### Steps

1. Read the current `ToolSpecs` class in `src/dot_tools/configure.py` to understand the existing
   structure.
2. Add a new field `depends_on: Annotated[list[str], pydantic.Field(default_factory=lambda: [])]`
   to `ToolSpecs`.
3. Run existing tests to ensure backward compatibility: `uv run pytest tests/test_configure.py::TestToolSpecs -v`
4. Write and run new tests for the new field:
   - Load a YAML snippet with `depends_on` and confirm it parses correctly.
    - Load a YAML snippet without `depends_on` and confirm it defaults to `[]`.
    - Verify the field is present and correct in the `ToolSpecs` instance.
5. Run all configure tests to verify no regressions: `uv run pytest tests/test_configure.py -v`


#### Technical Notes

The field should be a list of strings (tool names). The validation of whether those names
actually exist in the tools section is done at a later stage (in `resolve_tool_order()`).


### 02: Create the resolve_tool_order() function

Build a new function that takes a list of `ToolSpecs` and returns an ordered list respecting
their dependencies. The function validates the dependency graph and raises actionable errors
for cycles and unknown dependencies.


#### Acceptance Criteria

- AC01: Given tools with no dependencies, returns them in a valid topological order respecting
  any declared dependencies.
- AC02: Given tools `[A, B->A, C->B]` (B depends on A, C depends on B), returns an order where A
  comes before B and B comes before C.
- AC03: Raises `DotError` with a clear message when a tool depends on a non-existent tool.
- AC04: Raises `DotError` with a clear message naming the tools when a cycle is detected.
- AC05: Treats a self-dependency (A depends on A) as a cycle and raises with a clear message.
- AC06: Returns an empty list when given an empty input list.


#### Steps

1. Create a new function `resolve_tool_order(tools: list[ToolSpecs]) -> list[ToolSpecs]` in
   `src/dot_tools/configure.py`, placed near the tool-related models.
2. Build a map of tool name → tool object for validation.
3. Check that every dependency name in `depends_on` lists matches a tool in the input list.
   Raise `DotError` with the tool name and missing dependency if not.
4. Build a directed graph in the format expected by `graphlib.TopologicalSorter`:
   - Use tool names as nodes.
   - For each tool, call `sorter.add(tool_name, *dependency_names)`, meaning "tool_name depends
     on dependency_names", which ensures dependency_names come first in the topological order.
5. Use `graphlib.TopologicalSorter` to compute a valid order.
   - The sorter raises `CycleError` if a cycle is detected; catch it and raise a `DotError`
     with the names of the tools involved.
6. Map the sorted tool names back to the original `ToolSpecs` objects and return.
7. Write unit tests for each AC in `tests/test_configure.py`. Tests should:
   - Test no dependencies (AC01).
   - Test a simple chain A→B→C (AC02).
   - Test unknown dependency error (AC03).
   - Test cycle detection (AC04).
    - Test self-dependency as cycle (AC05).
    - Test empty input (AC06).
8. Run the new tests: `uv run pytest tests/test_configure.py::TestResolveToolOrder -v`
9. Run all configure tests: `uv run pytest tests/test_configure.py -v`


#### Technical Notes

- Use `graphlib.TopologicalSorter` from the Python standard library (no external dependencies).
- The graph direction: if A depends on B, create an edge B→A (B must come before A). This is
  the inverse of the dependency declaration because `TopologicalSorter` sorts in dependency
   order (dependencies first).
- Import `graphlib` and `CycleError` at the top of `configure.py`.
- Error messages must name the tools clearly so manifest authors can find and fix them without
   reading the source code.


### 03: Update _install_tools() to use resolved order

Modify the existing `_install_tools()` method to compute the resolved tool order before the
loop begins, then iterate over that resolved list instead of `self.install_manifest.tools`.


#### Acceptance Criteria

- AC01: `_install_tools()` calls `resolve_tool_order()` with the manifest tools before the
  iteration begins.
- AC02: Tools are installed in the resolved order, respecting their declared dependencies.
- AC03: If `resolve_tool_order()` raises an error, the error is propagated and the tool
  installation loop does not begin.
- AC04: Tools that are already installed (check command exits 0) are skipped but do not change
   the relative order of other tools.
- AC05: Tools skipped due to gui_only on a headless system are skipped but do not change the
   relative order of other tools.
- AC06: Existing tests for `_install_tools()` still pass.


#### Steps

1. Read the current `_install_tools()` method to understand the loop structure and logging.
2. After the `with spinner("Installing tools", ...)` line, add:
   ```python
   resolved_tools = resolve_tool_order(self.install_manifest.tools)
   ```
3. Change the line `for tool in self.install_manifest.tools:` to `for tool in resolved_tools:`
4. Verify the rest of the loop logic (check command, script selection, skip logic) remains
   unchanged. It should.
5. Run existing installer tests to ensure no regressions:
   `uv run pytest tests/test_configure.py::TestDotInstaller -v`
6. Manually verify the order change:
   - Create a test manifest with a dependency chain.
   - Mock or patch the subprocess calls.
   - Verify the loop iterates in resolved order.
7. Write an integration test in `tests/test_configure.py` that:
   - Creates a manifest with tools A, B→A, C→B.
   - Mocks the subprocess and skip logic.
   - Runs `_install_tools()`.
    - Verifies the tools were processed in order: A, then B, then C.
8. Run all configure tests: `uv run pytest tests/test_configure.py -v`


#### Technical Notes

- The error handling is already in place via the `DotError.handle_errors()` context manager in
  `install_dot()`, so a raised error from `resolve_tool_order()` will be caught and logged
  correctly.
- Do not modify the per-tool logic (check command, script selection, gui_only handling, skip
  logic). The resolved order is the only change to the execution flow.
- The settings section (`_apply_settings()`) is not affected by this feature; it continues to
   run in YAML order.


### 04: Seed the shipped manifest with a realistic dependency chain

Update `etc/install.yaml` to add explicit dependency declarations that form a meaningful
dependency chain. The design plan specifies: asdf → (asdf-go depends on asdf) → (usql depends
on asdf-go).


#### Acceptance Criteria

- AC01: The `asdf` tool entry has no `depends_on` declaration (or empty list).
- AC02: The `asdf-go` tool entry has `depends_on: [asdf]`.
- AC03: The `usql` tool entry has `depends_on: [asdf-go]`.
- AC04: The manifest is valid YAML and loads without error.
- AC05: The dependency chain is reflected correctly in an `InstallManifest` loaded from the file.


#### Steps

1. Open `etc/install.yaml` in an editor.
2. Locate the `asdf` tool entry (around line 203). Verify it has no `depends_on` field.
3. Locate the `asdf-go` tool entry (around line 218). Add `depends_on: [asdf]` as a new field
   after `name` or at the end of the entry (YAML is flexible; put it where it is most readable).
4. Locate the `usql` tool entry (around line 233). Add `depends_on: [asdf-go]` as a new field.
5. Verify the YAML is still valid: `uv run python -c "import yaml; yaml.safe_load(open('etc/install.yaml'))"` should not
   error.
6. Run the existing manifest loading tests to confirm no breakage:
   `uv run pytest tests/test_configure.py::TestInstallManifest -v`
7. Write a small test that:
    - Loads the real manifest.
    - Extracts the three tools.
    - Verifies the dependency fields are set correctly.
    - Calls `resolve_tool_order()` on the full tools list.
    - Confirms that asdf comes before asdf-go and asdf-go comes before usql in the resolved list.
8. Run all configure tests: `uv run pytest tests/test_configure.py -v`


#### Technical Notes

- The `usql` entry installs via `go install` on Linux (requiring golang from asdf-go) but via
  MacPorts on macOS (no dependency). The dependency declaration is safe on both platforms; on
  macOS it is effectively a no-op in terms of functionality but does not cause any harm.
- Ensure the YAML indentation is consistent with the rest of the file.

### 05: Write comprehensive tests for end-to-end scenarios

Create tests that verify the full feature end-to-end: from loading a manifest with dependencies
through resolving order to simulating tool installation.


#### Acceptance Criteria

- AC01: A manifest with multiple independent tools produces a valid topological order.
- AC02: A full install flow with dependencies installs tools in resolved order via `_install_tools()`.


#### Steps

1. In `tests/test_configure.py`, add the following test scenarios to `TestResolveToolOrder` (if not
   already covered):
   - Multiple independent tools with no dependencies between them (AC01). Verify that the resolved
     order is a valid topological sort, even though the relative order of independent tools is
     not constrained.
2. Create a new test that simulates the full install flow (AC02):
   - Create a DotInstaller with a manifest containing a dependency chain (e.g., A, B→A, C→B).
    - Mock subprocess calls to avoid running real install scripts.
    - Call `_install_tools()` and verify the tools were processed in resolved order by inspecting
      mock call order.
3. Run all tests: `uv run pytest tests/test_configure.py -v`
4. Run quality checks: `uv run ruff check src tests && uv run ty check`


#### Technical Notes

- Use `unittest.mock` to mock subprocess calls and avoid running actual install scripts during
  tests.
- The test manifest fixtures can use the helper functions already in `test_configure.py`
  (`make_dot_root()`, `make_installer()`).
- Tests should be clear and concise; each should test one scenario.

### 06: Verify backward compatibility and no regressions

Run the full test suite, lint, type check, and manual verification to confirm the feature is
backward compatible and does not break existing behavior.


#### Acceptance Criteria

- AC01: All existing tests pass without modification.
- AC02: All new tests pass.
- AC03: Linting passes with no errors.
- AC04: Type checking passes with no errors.
- AC05: A manifest with no dependencies installs identically to before the change (same order).
- AC06: The `_create_local_agents_file()` method still lists tools in YAML order, not resolved
   order (as per design plan).


#### Steps

1. Run the full test suite: `uv run pytest tests/test_configure.py -v`
2. Run linting: `uv run ruff check src tests`
3. Run type checking: `uv run ty check`
4. Run quality gate: `uv run ruff check src tests && uv run ty check && uv run pytest`
5. Verify `_create_local_agents_file()` uses `self.install_manifest.tools` (not resolved list):
   - Read the method to confirm it still uses the raw tools list for the local agents stub.
   - This is by design: the stub lists tools in manifest order, not install order.
6. Create a temporary test manifest with no dependencies and verify the install order is
   unchanged.
7. Commit and push changes (only if instructed to do so by the caller).


#### Technical Notes

- The `_create_local_agents_file()` method intentionally uses the raw manifest order, not the
  resolved order. This is documented in the design plan.
- The settings phase (`_apply_settings()`) is not affected and continues to run in manifest
  order.

----

## Unknowns

- None at this time. The design plan is comprehensive and resolves all architectural questions.

## Technical Notes

### Dependency direction in TopologicalSorter

When using `graphlib.TopologicalSorter`, the semantics are:
- `sorter.add(node, *predecessors)` means "node comes after predecessors".
- If tool B depends on tool A, we do `sorter.add(B_name, A_name)` so B comes after A.

### Error messages

Error messages must be user-facing and clearly actionable:
- Unknown dependency: `"Tool 'usql' depends on 'asdf-go', but 'asdf-go' is not in the tools section of the manifest"`
- Cycle: `"Cycle detected in tool dependencies: asdf-go → usql → asdf-go. Please check your dependency"`
  `declarations."`
- Self-dependency: `"Tool 'xyz' depends on itself. Remove this self-dependency from the manifest."`

### Testing strategy

Tests follow the existing patterns in `tests/test_configure.py`:
- Use pydantic model tests for schema validation.
- Use function tests for `resolve_tool_order()` with various graphs.
- Use integration tests for full-flow scenarios with mocked subprocess.
- Use the helper functions `make_dot_root()` and `make_installer()` for setup.

### Imports needed

Add to the top of `src/dot_tools/configure.py`:

```python
from graphlib import TopologicalSorter, CycleError
```

These are part of the Python standard library (available since Python 3.9).
