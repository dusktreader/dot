# Implementation Plan Review: Carve work-specific configuration into private work-dot repository

**Iteration 03**


## Source Artifact

.artifacts/20260713--carve-out-work-agents-file/implementation-plan.md


## Overview

All findings are resolved. The plan is approved for execution with no remaining blocking findings.

- **Critical**:    0
- **Significant**: 0
- **Trivial**:     0 (1 resolved)


## Prior Review Resolution

- **S01** ✓: Task 05 is now a full standalone task implementing `dt secrets fetch` in `dot`, with
  its own `dot/src/dot_tools/cli/secrets.py`, unit tests, and manual verification step. Design plan
  AC17 is now covered.
- **S02** ✓: Task 06 AC09 is present and matches the suggested wording verbatim: running
  `wdt configure --override-home /tmp/test-wdt-seed-live` must complete without error and a
  subsequent `wdt secrets fetch <any-seeded-key>` must exit non-zero, confirming end-to-end seeding
  from within the live CLI context.
- **S03** ✓: The old Task 11 (redundant `--root` argument passing) has been replaced entirely by
  a new Task 11 covering work-specific agent instructions. The subprocess construction, including
  `--root`, `--override-home`, and `--force` argument passing, is now consolidated in Task 07
  (formerly Task 06) AC03–AC05 and Step 2.
- **T01** ✓: Task 12 AC01 and AC02 now read "meets or exceeds the configured floor (70%)" rather
  than the incorrect 80% figure.
- **T02** ✓: The canonical private repository URL is confirmed as `https://github.com/Tucker-Beck_mcgraw/work-dot`
  with the underscore being intentional. No correction required.


## Findings


### Summary

| Finding | Title                                                | Outcome |
| ------- | ---------------------------------------------------- | ------- |
| T01     | GitHub org name `Tucker-Beck_mcgraw` still contains an invalid underscore | ✓ Rejected |


### Trivial


#### T01: GitHub org name `Tucker-Beck_mcgraw` still contains an invalid underscore

##### Where

Goal — line 15; Execution — Task 01 — introduction line 167, AC04 line 177, step 6 line 197.


##### Issue

GitHub organization and user names permit hyphens but not underscores. The name
`Tucker-Beck_mcgraw` is syntactically invalid and will be rejected by GitHub at account-creation
or remote-configuration time. The correct GitHub Cloud account name for the McGraw Hill work
account has not been confirmed in the plan.


##### Impact

Task 01 AC04 and step 6 will fail if the remote is configured with an invalid URL. The URL
also appears in the Goal section, where it serves as the canonical reference for the `work-dot`
repository location. Using an invalid name risks confusion during execution even if GitHub
account creation is deferred.


##### Suggestion

Confirm the correct GitHub Cloud account name for the McGraw Hill work account and replace all
occurrences of `Tucker-Beck_mcgraw` with the verified name. If the account does not yet exist,
note this as a prerequisite in Task 01 and add an AC for account creation before the remote
is configured.


##### Outcome

**Rejected.** The canonical private repository URL has been explicitly confirmed as
`https://github.com/Tucker-Beck_mcgraw/work-dot`. The underscore in the account name is
intentional and correct. No further correction is required.


----


## Notes

All findings have been resolved. The plan is ready for execution with no remaining blocking issues.
The canonical URL `https://github.com/Tucker-Beck_mcgraw/work-dot` has been explicitly confirmed,
with the underscore being intentional and correct. The two highest-priority fixes from iteration 02 —
standalone `dt secrets fetch` (Task 05) and seeding lifecycle AC (Task 06 AC09) — are fully and
correctly addressed.


## Approval

**Status: Approved**

This implementation plan has been reviewed and approved for execution. No blocking findings remain.
