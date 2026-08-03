# Add source context to worktree diffs

Extend the Neovim worktree diff workflow so visual selections sent to nvim-sidekick include the source file and line
context represented by the selected diff lines, not only the raw patch text.


## Goal

When `:wtdiff` or `,wtd` opens a worktree diff in a scratch buffer, selecting diff lines and sending them to Sidekick
should identify the corresponding file and source location. The context should remain useful for added, deleted, and
unchanged lines across multiple files and hunks.


## Scope

- Update the worktree diff module in `~/.config/nvim/lua/user/worktree.lua`.
- Update the Sidekick integration in `~/.config/nvim/lua/user/opencode.lua` and/or
  `~/.config/nvim/lua/plugins/sidekick.lua` as needed.
- Preserve the existing `:wtdiff` command, `,wtd` mapping, Snacks picker, relative worktree display paths, and diff
  scratch-buffer behavior.
- Do not make the scratch buffer pretend to be a real source file. Sidekick should receive explicit synthetic location
  context instead.


## Required behavior

### Diff metadata

While creating the scratch diff buffer, parse the patch headers and hunks and store buffer-local metadata for each
rendered diff line:

- Worktree-relative source path, such as `api/src/openapi.ts`.
- Absolute worktree path when needed to identify the source file unambiguously.
- Base-file line number for context and deleted lines.
- Worktree-file line number for context and added lines.
- An insertion anchor for added lines, because an added line has no corresponding base-file line.

Support multiple files and multiple hunks. Account for hunk headers, context lines, additions, deletions, and the
selection range rather than assuming the selected line number equals the source line number.


### Sidekick context

Add a custom Sidekick context variable or equivalent integration used by the visual-selection mapping. The submitted
context should contain:

1. The selected patch text.
2. The source file path for the selected diff section.
3. The relevant source line or range.
4. A clear explanation for added lines, such as `inserted before base line 147`.

Use Sidekick's context/location APIs where practical. The existing visual-selection behavior for real files must remain
unchanged.


### Example

Selecting these lines from a diff:

```diff
+      modelId: z.string(),
+      modelFamily: z.enum(['anthropic', 'gpt']),
+      region: z.string().openapi({ example: 'us-east-1' }),
+      requestTimeout: z.number().int().nullable(),
+      maxTokens: z.number().int().nullable(),
```

should send Sidekick context identifying the source file, for example:

```text
File: api/src/openapi.ts
Worktree: .worktrees/feat/FUS-303--migrate-bedrock-sdk
Location: inserted before base line 147
```

The exact presentation can follow Sidekick's location conventions, but raw diff text without source context is not
enough.


## Acceptance criteria

- AC01: `:wtdiff` and `,wtd` continue to open a relative-path worktree picker and a diff scratch buffer.
- AC02: A visual selection from a single-file diff sends Sidekick the selected patch text plus the source file path and
  source location.
- AC03: A visual selection from an added line reports an insertion anchor instead of inventing a base-file line number.
- AC04: Context and deleted lines report the correct base-file line numbers from the hunk metadata.
- AC05: Selections spanning multiple files or hunks produce context for every affected file/range, or clearly reject the
  selection with a useful message rather than silently sending incomplete context.
- AC06: Visual selections from ordinary named files retain their existing Sidekick behavior.
- AC07: The implementation handles a diff with no hunks, a new file, a deleted file, and multiple hunks without errors.


## Verification

Use the existing Neovim configuration checks where available. At minimum:

```shell
luac -p ~/.config/nvim/lua/user/worktree.lua
luac -p ~/.config/nvim/lua/user/opencode.lua
luac -p ~/.config/nvim/lua/plugins/sidekick.lua
nvim --headless -u NONE -c 'set rtp+=~/.config/nvim' -c 'lua require("user.worktree")' -c 'qa!'
```

Manually verify:

- A normal source-file visual selection still sends the usual Sidekick context.
- A selected added diff block identifies its file and insertion anchor.
- A selected context or deleted diff block identifies its base-file line.
- A multi-file selection includes all affected source locations.


## Technical notes

The current worktree diff buffer is a `nofile` scratch buffer with no source filename, so Sidekick's normal `{this}`
location context cannot resolve it automatically. Sidekick's `{selection}` context only supplies selected text. The
implementation must therefore bridge the diff buffer's local metadata into a custom textual context before calling the
Sidekick CLI.
