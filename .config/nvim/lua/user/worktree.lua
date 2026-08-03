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

local function show_diff(worktree, root)
  local lines = vim.fn.systemlist({ "git", "-C", worktree.path, "diff", "--no-color", "--no-ext-diff", "main" })
  if vim.v.shell_error ~= 0 then
    vim.notify("Unable to show diff for " .. worktree.text, vim.log.levels.ERROR)
    return
  end

  vim.cmd("enew")
  vim.bo.buftype = "nofile"
  vim.bo.bufhidden = "wipe"
  vim.bo.swapfile = false
  vim.bo.filetype = "diff"
  vim.api.nvim_buf_set_lines(0, 0, -1, false, #lines > 0 and lines or { "" })
  vim.api.nvim_buf_set_var(0, "worktree_diff_metadata", require("user.diff_context").parse_diff(lines, worktree.path, root))
  vim.cmd("normal! gg")
end

function M.diff(query)
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
