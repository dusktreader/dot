# Use worktree procedure

Use an isolated worktree for all code changes involved in a branch-based skill or procedure.


## Use the `use-worktree.py` tool

Always use the provided `.agents/tools/use-worktree.py` tool to get a worktree. Never create a branch or worktree on
your own. Never use `git switch` or mutate the current git branch for the project root if your skill or procedure
directs you to use a worktree.

Collect the required inputs and pass them to the tool.


## Required inputs

You need three values to pass to the `use-worktree.py` tool:

* **summary**: a brief summary of the task. Keep it under 80 characters. Use normal sentence structure and casing.
* **branch_type**: a branch type used for conventional branches. Usually `feat`, `fix`, etc. You can invoke with
  `--help` to see a list of all types available.
* **ticket**: an optional ticket identifier. Usually a JIRA issue id. Can be "NO-TICKET". If "NO-TICKET" is provided,
  use that explicitly.


## Check for an existing worktree/branch

First, use the `search` subcommand of the tool to check if a similar worktree/branch already exists for the ticket
and summary. It may be that another agent has already worked on this task.

If another worktree/branch exists that matches the ticket and summary, use that ticket and summary explicitly and
exactly.


## Request a worktree/branch from the tool

Next, use the `switch` subcommand of the tool to use the selected worktree. Pass in the required inputs. The tool will
provision the worktree and branch and provide you the worktree path. Change to that path and then return to your caller
with the worktree path.
