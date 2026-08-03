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

local diff_context = require("user.diff_context")

local function location_text(item)
  if item.kind == "add" then return ("inserted before base line %d, worktree lines %d-%d"):format(item.anchor or 1, item.work_from, item.work_to)
  elseif item.kind == "delete" then return ("base lines %d-%d (deleted)"):format(item.base_from, item.base_to)
  elseif item.kind == "context" then return ("base lines %d-%d, worktree lines %d-%d"):format(item.base_from, item.base_to, item.work_from, item.work_to) end
end

--- Render selected lines from a worktree diff as explicit Sidekick context.
--- Sidekick calls this while the visual range is still available.
function M.diff_context(ctx)
  local metadata = vim.b[ctx.buf].worktree_diff_metadata
  if not metadata or not ctx.range then return false end
  local selected = diff_context.selected_lines(vim.api, ctx)
  if #selected == 0 then return false end

  local groups, order = {}, {}
  for _, item in ipairs(diff_context.aggregate(metadata, ctx.range.from[1], ctx.range.to[1])) do
    if item.path then
      local key = item.path
      if not groups[key] then
        groups[key] = { path = item.path, worktree = item.worktree, repo_root = item.repo_root, locations = {} }
        table.insert(order, key)
      end
      local location = location_text(item)
      if location then table.insert(groups[key].locations, location) end
    end
  end

  local context = { "Selected patch:" }
  for _, key in ipairs(order) do
    local group = groups[key]
    table.insert(context, ("File: %s"):format(group.path))
    local display = group.worktree
    local root = group.repo_root
    if root and display == root then
      display = "."
    elseif root and display:sub(1, #root + 1) == root .. "/" then
      display = display:sub(#root + 2)
    end
    table.insert(context, ("Worktree: %s"):format(display))
    if #group.locations == 0 then
      table.insert(context, "Location: selected diff header or hunk metadata")
    else
      for _, location in ipairs(group.locations) do
        table.insert(context, "Location: " .. location)
      end
    end
  end
  if #order == 0 then table.insert(context, "Location: no source hunk line selected") end
  table.insert(context, "")
  table.insert(context, "```diff")
  vim.list_extend(context, selected)
  table.insert(context, "```")
  return table.concat(context, "\n")
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
  local buf = vim.api.nvim_get_current_buf()

  -- For real file buffers, delegate to sidekick's own send so {this} works normally.
  if is_file_buf(buf) then
    require("sidekick.cli").send({ msg = "{this}" })
    return
  end

  if vim.b[buf].worktree_diff_metadata then
    require("sidekick.cli").send({ msg = "{worktree_diff}" })
  else
    require("sidekick.cli").send({ msg = "{selection}" })
  end
end

return M
