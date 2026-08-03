local M = {}

local function git_unescape(value)
  if value:sub(1, 1) ~= '"' or value:sub(-1) ~= '"' then return value end
  value = value:sub(2, -2)
  return (value:gsub("\\(\\?)([0-7][0-7]?[0-7]?)", function(prefix, digits)
    if prefix == "" then return string.char(tonumber(digits, 8)) end
    return "\\" .. digits
  end):gsub("\\([abfnrtv\\\"])", {
    a = "\a", b = "\b", f = "\f", n = "\n", r = "\r", t = "\t", v = "\v", ["\\"] = "\\", ['"'] = '"',
  }))
end

local function git_words(value)
  local words, start, quoted, escaped = {}, nil, false, false
  for index = 1, #value do
    local char = value:sub(index, index)
    if not start and char ~= " " and char ~= "\t" then start = index end
    if start then
      if escaped then escaped = false
      elseif char == "\\" then escaped = true
      elseif char == '"' then quoted = not quoted
      elseif not quoted and (char == " " or char == "\t") then
        table.insert(words, git_unescape(value:sub(start, index - 1))); start = nil
      end
    end
  end
  if start then table.insert(words, git_unescape(value:sub(start))) end
  return words
end

local function diff_path(value, strip_prefix)
  if not value then return nil end
  local path = git_unescape(value:match("^([^\t]+)") or value):gsub("^%s+", "")
  if path == "/dev/null" then return nil end
  if strip_prefix then path = path:gsub("^[ab]/", "") end
  return path
end

local function metadata(worktree, root, path, kind, base, work, anchor, old_path, new_path)
  return {
    source_path = path, source_absolute_path = path and (worktree .. "/" .. path) or nil,
    worktree_path = worktree, repo_root = root, kind = kind,
    base_line = base, worktree_line = work, insertion_anchor = anchor,
    old_path = old_path, new_path = new_path,
  }
end

--- Parse unified Git diff lines, retaining one metadata record per rendered line.
function M.parse_diff(lines, worktree, root)
  local result, old_path, new_path, source_path = {}, nil, nil, nil
  local base, work, in_hunk = nil, nil, false
  for index, line in ipairs(lines) do
    local kind, line_base, line_work, anchor = "header", nil, nil, nil
    local words = line:match("^diff %-%-git (.+)$")
    if words then
      local paths = git_words(words)
      old_path, new_path = diff_path(paths[1], true), diff_path(paths[2], true)
      source_path = new_path or old_path; in_hunk = false; base, work = nil, nil
    elseif not in_hunk and line:match("^--- ") then
      old_path = diff_path(line:sub(5), true)
      source_path = new_path or old_path
    elseif not in_hunk and line:match("^%+%+%+ ") then
      new_path = diff_path(line:sub(5), true)
      source_path = new_path or old_path
    elseif line:match("^rename from ") then
      old_path = diff_path(line:sub(13), false); source_path = new_path or old_path
    elseif line:match("^rename to ") then
      new_path = diff_path(line:sub(11), false); source_path = new_path or old_path
    else
      local old_start, _, new_start = line:match("^@@ %-(%d+),?(%d*) %+(%d+),?(%d*) @@")
      if old_start then
        base, work = tonumber(old_start), tonumber(new_start); in_hunk = true; kind = "hunk"
      elseif in_hunk and source_path and line:sub(1, 1) == " " then
        kind, line_base, line_work = "context", base, work; base, work = base + 1, work + 1
      elseif in_hunk and source_path and line:sub(1, 1) == "+" then
        kind, line_work, anchor = "add", work, base; work = work + 1
      elseif in_hunk and source_path and line:sub(1, 1) == "-" then
        kind, line_base = "delete", base; base = base + 1
      end
    end
    result[index] = metadata(worktree, root, source_path, kind, line_base, line_work, anchor, old_path, new_path)
  end
  return result
end

local function add_range(out, item)
  local last = out[#out]
  local same = last and last.kind == item.kind and last.path == item.source_path
  if item.kind == "context" and same and last.base_to + 1 == item.base_line and last.work_to + 1 == item.worktree_line then
    last.base_to, last.work_to = item.base_line, item.worktree_line; return
  elseif item.kind == "delete" and same and last.base_to + 1 == item.base_line then
    last.base_to = item.base_line; return
  elseif item.kind == "add" and same and last.anchor == item.insertion_anchor and last.work_to + 1 == item.worktree_line then
    last.work_to = item.worktree_line; return
  end
  table.insert(out, { kind = item.kind, path = item.source_path, worktree = item.worktree_path, repo_root = item.repo_root,
    base_from = item.base_line, base_to = item.base_line,
    work_from = item.worktree_line, work_to = item.worktree_line, anchor = item.insertion_anchor })
end

--- Collapse consecutive selected metadata records without crossing rendered gaps or hunks.
function M.aggregate(metadata, first, last)
  if first > last then first, last = last, first end
  local ranges, segment, previous = {}, {}, nil
  local function finish()
    for _, range in ipairs(segment) do ranges[#ranges + 1] = range end
    segment = {}
  end
  for line = first, last do
    local item = metadata[line]
    if item and (item.kind == "context" or item.kind == "delete" or item.kind == "add") and item.source_path then
      if previous ~= line - 1 then finish() end
      add_range(segment, item); previous = line
    else
      finish(); previous = nil
    end
  end
  finish()
  return ranges
end

--- Extract a visual selection, including reversed and blockwise selections.
function M.selected_lines(api, ctx)
  local range = ctx.range
  if not range then return {} end
  local from, to = range.from, range.to
  if (from[1] > to[1]) or (from[1] == to[1] and from[2] > to[2]) then from, to = to, from end
  if range.kind == "line" then return api.nvim_buf_get_lines(ctx.buf, from[1] - 1, to[1], false) end
  local lines = {}
  for line = from[1], to[1] do
    local left, right
    if range.kind == "block" then
      left, right = math.min(from[2], to[2]), math.max(from[2], to[2])
    elseif line == from[1] then
      left, right = from[2], (line == to[1] and to[2] or #((api.nvim_buf_get_lines(ctx.buf, line - 1, line, false)[1] or "")) - 1)
    elseif line == to[1] then
      left, right = 0, to[2]
    else
      left, right = 0, #((api.nvim_buf_get_lines(ctx.buf, line - 1, line, false)[1] or "")) - 1
    end
    local text = api.nvim_buf_get_lines(ctx.buf, line - 1, line, false)[1] or ""
    left, right = math.min(left, #text), math.min(right + 1, #text)
    lines[#lines + 1] = text:sub(left + 1, right)
  end
  return lines
end

return M
