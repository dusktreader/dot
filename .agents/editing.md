# File Editing Safety

The user frequently edits files in their editor while the agent is working. Stale reads lead to clobbered changes.


## Staleness guard plugin

A global OpenCode plugin (`~/.config/opencode/plugins/staleness-guard.ts`) enforces this automatically. It tracks the
mtime of every file read and blocks edits if the file has changed on disk since the last read. If the plugin throws an
error, re-read the file and retry the edit.


## Manual fallback

If the plugin is not loaded or you are unsure, follow this procedure before every edit:

1. When reading a file, note the modification timestamp (via `stat -f '%m'` on macOS or `stat -c '%Y'` on Linux)
2. Before editing, run `stat` again and **compare** the new timestamp to the stored one
3. If the timestamps differ, re-read the file before editing
4. If they match, proceed with the edit

Just running `stat` without comparing to a previous value is useless. The point is detecting changes between the read
and the edit.

Never assume a file is unchanged. The user may have saved new content at any point between the agent's read and edit.
