# QA Implementation Procedure

Run the shared human-directed QA stage after an implementation passes its final blocker check.


## Required inputs

The caller must provide:

- Concise implementation summary and changed-file scope
- Approved plan path and plan type: `task` or `implementation`
- Execution journal path
- Deviation journal path
- Worktree and branch context
- Current workflow and return state after QA approval
- For epic mode, any additional human verification required before the coordinator proceeds

If any input is missing or ambiguous, ask the caller before presenting the implementation for QA.


## QA protocol

1. Tell the human the implementation is ready for QA and provide the summary, changed-file scope, and worktree/branch.
2. Keep the approved plan and reviews immutable. Wait for user-directed testing feedback. Questions, silence, and
   unverified changes are not approval.
3. Make only changes the human requests. Record every implemented QA change in the caller-supplied deviation journal,
   including source, request or trigger, plan alignment, changed files, reason when provided, and focused verification.
   Do not modify approved plans or reviews.
4. After each QA change, run focused verification and ask the human to verify the result before proceeding.
5. Close QA only after the human explicitly approves the result with no further requested changes.
6. Return QA approval evidence, QA changes, and artifact paths to the caller at the supplied return state. If the caller
   requires separate post-QA human verification, report QA approval distinctly from that verification.

The caller owns QA-stage commits and later workflow stages. Do not commit, publish, perform unrelated implementation
work, or advance the workflow yourself.
