local M = {}

local function git_root()
  local root = vim.fn.system("git rev-parse --show-toplevel 2>/dev/null")
  if vim.v.shell_error ~= 0 then
    vim.notify("Current directory is not inside a Git repository", vim.log.levels.ERROR)
    return nil
  end
  return vim.trim(root)
end

local function relative_path(root, path)
  if path == root then return "." end
  local prefix = root .. "/"
  if vim.startswith(path, prefix) then
    return path:sub(#prefix + 1)
  end
  return path
end

local function get_worktrees(root)
  local lines = vim.fn.systemlist("git worktree list --porcelain")
  if vim.v.shell_error ~= 0 then
    vim.notify("Unable to list Git worktrees", vim.log.levels.ERROR)
    return {}
  end

  local worktrees = {}
  local current

  local function finish_worktree()
    if current and current.path and current.path ~= root then
      local branch = current.branch and current.branch:match("[^/]+$") or "detached"
      table.insert(worktrees, {
        path = current.path,
        text = relative_path(root, current.path) .. "  (" .. branch .. ")",
      })
    end
    current = nil
  end

  for _, line in ipairs(lines) do
    if line:match("^worktree ") then
      finish_worktree()
      current = { path = line:match("^worktree (.+)") }
    elseif line:match("^branch ") and current then
      current.branch = line:match("^branch (.+)")
    elseif line == "" then
      finish_worktree()
    end
  end
  finish_worktree()

  return worktrees
end

--- Find the rendered line corresponding to a previously selected diff item.
---@param metadata table[] parsed metadata for the reloaded diff
---@param previous table|nil metadata for the cursor's previous diff line
---@param fallback_line integer previous rendered line
---@param line_count integer number of lines in the reloaded diff
---@return integer
function M.find_reload_line(metadata, previous, fallback_line, line_count)
  local function location(item)
    if item.kind == "context" then return item.base_line end
    if item.kind == "delete" then return item.base_line end
    if item.kind == "add" then return item.insertion_anchor end
    return nil
  end

  local previous_location = previous and location(previous)
  local best_line, best_score
  if previous and previous.source_path then
    for line, item in ipairs(metadata) do
      if item.source_path == previous.source_path then
        local score = item.kind == previous.kind and 100 or 0
        local item_location = location(item)
        if previous_location and item_location then
          score = score + 1000 - math.abs(previous_location - item_location)
        elseif not previous_location and not item_location then
          score = score + 100
        end
        if not previous_location or not item_location then
          score = score + math.max(0, 100 - math.abs(line - fallback_line))
        end
        if not best_score or score > best_score then
          best_line, best_score = line, score
        end
      end
    end
  end

  return math.max(1, math.min(best_line or fallback_line, math.max(1, line_count)))
end

local function show_diff(worktree, root, reload)
  local lines = vim.fn.systemlist({ "git", "-C", worktree.path, "diff", "--no-color", "--no-ext-diff", "main" })
  if vim.v.shell_error ~= 0 then
    vim.notify("Unable to show diff for " .. worktree.text, vim.log.levels.ERROR)
    return
  end

  local cursor, view, previous
  if reload then
    cursor = vim.api.nvim_win_get_cursor(0)
    view = vim.fn.winsaveview()
    previous = vim.b[0].worktree_diff_metadata[cursor[1]]
  else
    vim.cmd("enew")
  end

  vim.bo.buftype = "nofile"
  vim.bo.bufhidden = "wipe"
  vim.bo.swapfile = false
  vim.bo.filetype = "diff"
  local rendered_lines = #lines > 0 and lines or { "" }
  vim.api.nvim_buf_set_lines(0, 0, -1, false, rendered_lines)
  local metadata = require("user.diff_context").parse_diff(rendered_lines, worktree.path, root)
  vim.api.nvim_buf_set_var(0, "worktree_diff_metadata", metadata)
  if reload then
    local line = M.find_reload_line(metadata, previous, cursor[1], #rendered_lines)
    local column = math.min(cursor[2], #rendered_lines[line])
    vim.fn.winrestview(view)
    vim.api.nvim_win_set_cursor(0, { line, column })
  else
    vim.cmd("normal! gg")
  end
end

function M.diff(query)
  local current_metadata = vim.b[0].worktree_diff_metadata
  if current_metadata and current_metadata[1] then
    local current = current_metadata[1]
    show_diff({ path = current.worktree_path, text = current.worktree_path }, current.repo_root, true)
    return
  end

  local root = git_root()
  if not root then return end

  local worktrees = get_worktrees(root)
  if #worktrees == 0 then
    vim.notify("No Git worktrees found", vim.log.levels.WARN)
    return
  end

  Snacks.picker.select(worktrees, {
    prompt = "Worktree diff",
    format_item = function(item) return item.text end,
    snacks = { pattern = query or "" },
  }, function(worktree)
    if worktree then show_diff(worktree, root) end
  end)
end

return M
