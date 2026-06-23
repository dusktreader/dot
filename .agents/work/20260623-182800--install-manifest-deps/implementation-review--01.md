# Implementation Plan Review: Install manifest dependency ordering

**Iteration 01**


## Source Artifact

.agents/work/20260623-182800--install-manifest-deps/implementation-plan.md


## Overview

The plan is well-structured and covers all design plan acceptance criteria. It correctly names
the target files, functions, and test classes, and the overall task sequencing is logical. One
significant bug in the Project Commands section would cause the quality gate to fail immediately,
and two other significant issues touch AC correctness and task structure. Several formatting
violations are present but do not affect executability.

Findings:

- **Critical**:    0
- **Significant**: 3
- **Trivial**:     4


## Findings


### Summary

| Finding | Title                                                              | Outcome |
| ------- | ------------------------------------------------------------------ | ------- |
| S01     | Wrong type checker throughout: `pyright` should be `ty`           |         |
| S02     | Task 02 AC01 overspecifies ordering for independent tools          |         |
| S03     | Task 05 duplicates test scenarios already assigned to Tasks 02/04  |         |
| T01     | Task 02 Step 4 graph-direction wording contradicts itself          |         |
| T02     | Two prose lines exceed 120 characters                              |         |
| T03     | Sibling `###` task headings separated by `---` bars               |         |
| T04     | `####` subsection headings preceded by only one blank line         |         |


### Significant


#### S01: Wrong type checker throughout — `pyright` should be `ty`

##### Where

Project Commands — "Run quality gate" — line 28; Task 05 Step 7 — line 302;
Task 06 Steps 3 and 4 — lines 333–334


##### Issue

The plan references `uv run pyright src tests` in four places. This project uses `ty` (not
`pyright`) as its type checker, configured under `[tool.ty.rules]` in `pyproject.toml` and
declared as a dev dependency (`ty>=0.0.14`). Running `uv run pyright` will fail with "command
not found" because `pyright` is not installed in the project environment.

The `.dot_agents/dot.md` documents the correct command as `uv run ty check`.


##### Impact

The quality gate command in Project Commands is broken. An executor running it verbatim will
hit an error immediately, before any tool logic is exercised. Task 06 Steps 3 and 4 suffer the
same failure. Task 05 Step 7 will also fail when the executor runs the final quality check.


##### Suggestion

Replace every occurrence of `uv run pyright src tests` with `uv run ty check src tests`.

In Project Commands, replace the quality gate command block with:

```shell
uv run ruff check src tests
uv run ty check src tests
uv run pytest
```

Apply the same substitution in Task 05 Step 7 and Task 06 Steps 3–4.


##### Outcome


----


#### S02: Task 02 AC01 overspecifies ordering for independent tools

##### Where

Execution — Task 02 — Acceptance Criteria — line 128


##### Issue

AC01 states: "Given tools with no dependencies, returns them in the same order as the input
list." Python's `graphlib.TopologicalSorter` documentation explicitly says: "The particular
order that is returned may depend on the specific order in which the items were inserted in the
graph." Input order is preserved in CPython today but is not guaranteed by the specification.

More importantly, the design plan states: "No tiebreak policy is imposed on independent
tools." An AC that enforces input-order preservation contradicts the design.


##### Impact

The AC is testable and will pass under CPython, but it encodes a contract the design
intentionally does not make. A future CPython change or a different interpreter could break
the test without breaking the feature. It also tells the executor to write a test that checks
order where the design says order is undefined for independent tools.


##### Suggestion

Replace AC01 with a weaker, design-consistent assertion:

> AC01: Given tools with no dependencies, returns all tools in a valid topological order
> (each tool appears in the result exactly once; since there are no dependency constraints,
> any permutation is acceptable).

If preserving input order for independent tools is a desired property (it is a useful
predictability guarantee), state it explicitly as a design decision and update the design plan
to reflect it.


##### Outcome


----


#### S03: Task 05 duplicates test scenarios already assigned to Tasks 02 and 04

##### Where

Execution — Task 05 — Steps and Acceptance Criteria — lines 268–311


##### Issue

Task 05 is presented as a "comprehensive end-to-end" testing task, but the scenarios it
covers are substantially already assigned to earlier tasks:

- Task 02 Step 7 already covers: no-dependency ordering (Task 05 AC01), chain resolution
  (Task 05 AC02), missing-dependency error (Task 05 AC04), cycle detection (Task 05 AC05),
  and self-dependency (partially).
- Task 04 Step 7 already writes: load the real manifest, extract the three tools, verify
  dependency fields, call `resolve_tool_order()`, and confirm asdf precedes asdf-go precedes
  usql — which is exactly Task 05 AC06 and AC07.

Task 05 Step 1 acknowledges the overlap with "if not already created in task 02", but the
step list still asks the executor to add tests for AC01, AC02, AC04, and AC05 that Task 02
already covered. The net result is that the executor must decide on the fly which tests exist
and which to skip, or produce duplicate tests.

The only genuinely new scenario is Task 05 AC03 ("multiple independent tools produce a valid
topological order") and Step 5 ("full install flow with mocked subprocess").


##### Impact

The executor faces an ambiguous assignment: the task implies writing tests that may already
exist, and may end up with duplicate test methods. Alternatively, the executor may skip Task 05
steps silently. Either outcome reduces test clarity.


##### Suggestion

Restructure Task 05 to contain only the scenarios not already covered in Tasks 02 and 04:

1. Remove AC01, AC02, AC04, AC05 — point the executor back to `TestResolveToolOrder` from
   Task 02.
2. Remove Steps 1–2 — the `TestResolveToolOrder` class and those tests are already done.
3. Add AC03 ("multiple independent tools") to `TestResolveToolOrder` in Task 02 instead.
4. Consolidate the real-manifest tests (AC06, AC07) into Task 04, so the test is written
   where the manifest is seeded.
5. Keep Step 5 (full install flow with mocked subprocess) and the `TestManifestIntegration`
   class as the only remaining content of Task 05.

If the intent is that Task 05 is a pure verification pass over tests written elsewhere, say
so explicitly: "Run the tests from Tasks 02–04 together and confirm no gaps."


##### Outcome


----


### Trivial


#### T01: Task 02 Step 4 graph-direction wording conflicts with the Technical Notes

##### Where

Execution — Task 02 — Steps — line 144; Task 02 — Technical Notes — line 163


##### Issue

Step 4 says: "For each tool, add edges from the tool to each of its dependencies (reverse
direction)." The parenthetical "(reverse direction)" without further explanation is ambiguous —
reverse of what? An executor who reads only Step 4 might call `sorter.add(dep, tool)` (edge
from dependency to tool) instead of the correct `sorter.add(tool, dep)` (tool is node, dep is
predecessor).

The Technical Notes in the same task correctly describe the API: "if A depends on B, create
an edge B→A (B must come before A)" and the global Technical Notes repeat the correct call
`sorter.add(B_name, A_name)`. The contradiction is between the step prose and the notes.


##### Suggestion

Rewrite Step 4 to match the Technical Notes:

> 4. Build a directed graph using `graphlib.TopologicalSorter`:
>    - For each tool `T` with dependencies, call `sorter.add(T.name, *T.depends_on)`.
>      This registers each dependency as a predecessor that must come before `T`.
>    - Tools with no dependencies need no explicit `sorter.add()` call; they will appear
>      in the graph automatically as predecessors of other tools.


##### Outcome


----


#### T02: Two prose lines exceed the 120-character limit

##### Where

Task 04 — Steps — line 247 (127 chars); Technical Notes — "Error messages" — line 367 (122 chars)


##### Issue

Line 247: the YAML-validation command inline in a step prose line runs 127 characters.
Line 367: the cycle-error message example runs 122 characters.

Code blocks and tables are exempt from the 120-character limit, but prose lines are not.


##### Suggestion

For line 247, move the shell command to a fenced code block instead of inlining it in the
step prose:

> 5. Verify the manifest is still valid YAML:
>
> ```shell
> uv run python -c "import yaml; yaml.safe_load(open('etc/install.yaml'))"
> ```

For line 367, wrap the line at a natural break before 120 characters:

> - Cycle: `"Cycle detected in tool dependencies: asdf-go → usql → asdf-go.`
>   `Please check your dependency declarations."`


##### Outcome


----


#### T03: Sibling `###` task headings separated by `---` bars

##### Where

Execution section — between every pair of task headings — lines 118, 170, 224, 265, 312


##### Issue

The markdown style guide states: "Add a separator bar before going back to a higher-level
heading. Do not use a separator bar between siblings at the same level." All five `---` bars in
the Execution section appear between sibling `### ` task headings, not before a return to `##`.


##### Suggestion

Remove the `---` separator bars between task headings. The two blank lines required before
each `###` heading provide sufficient visual separation.


##### Outcome


----


#### T04: `####` subsection headings preceded by only one blank line

##### Where

All task subsections throughout the Execution section (e.g., line 90 "#### Acceptance
Criteria", line 99 "#### Steps", line 112 "#### Technical Notes", and equivalents in Tasks
02–06)


##### Issue

The markdown style guide requires two blank lines before any heading whose parent heading has
content. Every `###` task heading has a description paragraph, so the `####` subsections
underneath each task — Acceptance Criteria, Steps, Technical Notes — all require two blank
lines before them. The plan uses only one blank line throughout.


##### Suggestion

Add a second blank line before each `####` heading in the Execution section. For example,
before "#### Acceptance Criteria" in Task 01:

```text
Ensure the field defaults to an empty list and loads correctly from YAML.


#### Acceptance Criteria
```


##### Outcome


----


## Notes

S01 is a straightforward substitution — four occurrences of `uv run pyright src tests` become
`uv run ty check src tests`. No design judgment is needed.

S02 and S03 have a relationship: if S03 is resolved by removing the redundant AC coverage from
Task 05, the AC03 in Task 05 ("multiple independent tools") should migrate to Task 02 alongside
the other `TestResolveToolOrder` cases. Resolving S03 first makes S02's fix easier to scope.

T03 and T04 are pervasive formatting corrections that can be applied mechanically. They do not
affect executability.
