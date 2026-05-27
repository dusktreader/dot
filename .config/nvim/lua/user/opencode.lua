local M = {}

-- Send text (and optionally submit) via sidekick's attached opencode session.
local function send_to_session(text, submit, cb)
  local State = require("sidekick.cli.state")
  local states = State.get({ name = "opencode", attached = true })

  if #states == 0 then
    vim.notify("opencode: no attached session found", vim.log.levels.ERROR)
    return
  end

  local session = states[1].session
  session:send(text)
  if submit then
    vim.defer_fn(function()
      session:submit()
      if cb then cb() end
    end, 200)
  elseif cb then
    cb()
  end
end

-- Ensure the opencode terminal is visible and attached, then call cb.
---@param focus boolean whether to focus the terminal after opening
local function ensure_open(cb, focus)
  require("sidekick.cli").show({ name = "opencode", focus = false })
  -- Give sidekick a moment to attach before we try to use the session.
  vim.defer_fn(function()
    cb()
    if focus then
      require("sidekick.cli").focus({ name = "opencode" })
    end
  end, 150)
end

-- Return true if the buffer is a real file on disk (not a neogit/diff buffer).
local function is_file_buf(buf)
  return vim.bo[buf].buflisted
    and vim.tbl_contains({ "", "help" }, vim.bo[buf].buftype)
    and vim.fn.filereadable(vim.api.nvim_buf_get_name(buf)) == 1
end

-- Scan upward from a line in the buffer to find diff context:
-- returns { file = "path/to/file.ts", line = 42 } or nil.
local function find_diff_context(buf, from_line)
  local all_lines = vim.api.nvim_buf_get_lines(buf, 0, -1, false)
  local file, hunk_start

  -- Scan upward from the selection start.
  for i = from_line, 1, -1 do
    local line = all_lines[i]

    -- Match hunk header: @@ -oldstart,oldcount +newstart,newcount @@
    if not hunk_start then
      local new_start = line:match("^@@[^+]*%+(%d+)")
      if new_start then
        hunk_start = tonumber(new_start)
      end
    end

    -- Match "modified   path/to/file" or "new file   path/to/file"
    if not file then
      local f = line:match("^%s*modified%s+(.+)$")
             or line:match("^%s*new file%s+(.+)$")
             or line:match("^%s*renamed%s+.+%->%s+(.+)$")
      if f then
        file = vim.trim(f)
      end
    end

    if file and hunk_start then break end
  end

  if file or hunk_start then
    return { file = file, line = hunk_start }
  end
end

-- Start a code review by sending the staged diff to opencode.
function M.review_staged()
  local diff = vim.fn.system({ "git", "diff", "--staged" })
  if vim.v.shell_error ~= 0 then
    vim.notify("opencode: git diff --staged failed", vim.log.levels.ERROR)
    return
  end

  if diff == "" then
    vim.notify("opencode: no staged changes", vim.log.levels.WARN)
    return
  end

  local msg = "Let's do a code review. Here are the staged changes:\n\n```diff\n" .. diff .. "\n```"

  ensure_open(function()
    send_to_session(msg, true, function()
      vim.notify("opencode: review started", vim.log.levels.INFO)
    end)
  end, false)
end

-- Send the current visual selection to opencode.
-- In a real file buffer: uses sidekick's {this} behavior (file + position context).
-- In a diff buffer: wraps the selection with file/line context extracted from the hunk.
function M.send_selection()
  -- Exit visual mode and capture the marks it leaves behind.
  local esc = vim.api.nvim_replace_termcodes("<Esc>", true, false, true)
  vim.api.nvim_feedkeys(esc, "x", false)

  local buf = vim.api.nvim_get_current_buf()

  -- For real file buffers, delegate to sidekick's own send so {this} works normally.
  if is_file_buf(buf) then
    require("sidekick.cli").send({ msg = "{this}" })
    return
  end

  local from = vim.api.nvim_buf_get_mark(buf, "<")
  local to   = vim.api.nvim_buf_get_mark(buf, ">")

  local lines = vim.api.nvim_buf_get_lines(buf, from[1] - 1, to[1], false)
  if #lines == 0 then
    vim.notify("opencode: nothing selected", vim.log.levels.WARN)
    return
  end

  -- Build a context prefix from the nearest file/hunk header above the selection.
  local ctx = find_diff_context(buf, from[1])
  local context_str = ""
  if ctx and ctx.file then
    context_str = "In `" .. ctx.file .. "`"
    if ctx.line then
      context_str = context_str .. " around line " .. ctx.line
    end
    context_str = context_str .. ", look at this part of the diff:\n\n"
  else
    context_str = "Look at this part of the diff specifically:\n\n"
  end

  local text = table.concat(lines, "\n")
  local msg = context_str .. "```diff\n" .. text .. "\n```"

  ensure_open(function()
    send_to_session(msg, false, function()
      vim.notify("opencode: selection sent", vim.log.levels.INFO)
    end)
  end, true)
end

return M
