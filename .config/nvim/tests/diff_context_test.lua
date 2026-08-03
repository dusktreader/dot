local diff_context = require("user.diff_context")

local function equal(actual, expected, message)
  assert(vim.deep_equal(actual, expected), message or ("expected " .. vim.inspect(expected) .. ", got " .. vim.inspect(actual)))
end

local lines = {
  "diff --git a/src/one.lua b/src/one.lua",
  "--- a/src/one.lua",
  "+++ b/src/one.lua",
  "@@ -1,2 +1,3 @@",
  " one",
  "+++ added source text",
  "--- deleted source text",
  "+new source text",
  "diff --git a/src/two.lua b/src/two.lua",
  "--- a/src/two.lua",
  "+++ b/src/two.lua",
  "@@ -4 +4 @@",
  "-old",
  "+new",
}

local metadata = diff_context.parse_diff(lines, "/repo/.worktrees/topic", "/repo")
assert(metadata[6].kind == "add", "+++ content inside a hunk must be an addition")
assert(metadata[7].kind == "delete", "--- content inside a hunk must be a deletion")

local forward = diff_context.aggregate(metadata, 5, 14)
local reversed = diff_context.aggregate(metadata, 14, 5)
equal(reversed, forward, "reversed aggregation must normalize selection bounds")
assert(#forward == 6, "expected six ranges across two files")
assert(forward[1].path == "src/one.lua", "aggregated ranges must retain source_path")
assert(forward[5].path == "src/two.lua", "aggregated ranges must retain each file path")

local selected = diff_context.selected_lines({
  nvim_buf_get_lines = function() return { "alpha", "beta", "gamma" } end,
}, {
  buf = 1,
  range = { kind = "line", from = { 3, 0 }, to = { 1, 0 } },
})
equal(selected, { "alpha", "beta", "gamma" }, "reversed visual selection must preserve source order")

vim.api.nvim_buf_set_lines(0, 0, -1, false, lines)
vim.b[0].worktree_diff_metadata = metadata
local context = require("user.opencode").diff_context({
  buf = 0,
  range = { kind = "line", from = { 14, 0 }, to = { 5, 0 } },
})
assert(context:find("File: src/one.lua", 1, true), "E2E context must include the first source file")
assert(context:find("File: src/two.lua", 1, true), "E2E context must include the second source file")
assert(context:find("Worktree: .worktrees/topic", 1, true), "E2E context must use picker-compatible worktree paths")
assert(not context:find("Worktree: ./.worktrees/topic", 1, true), "E2E context must not add a redundant ./ prefix")

print("diff_context_test: all assertions passed")
