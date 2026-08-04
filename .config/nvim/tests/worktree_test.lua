local worktree = require("user.worktree")

local metadata = {
  { source_path = "src/one.lua", kind = "context", base_line = 10, worktree_line = 10 },
  { source_path = "src/two.lua", kind = "context", base_line = 20, worktree_line = 20 },
}

local line = worktree.find_reload_line(metadata, {
   source_path = "src/two.lua",
   kind = "context",
   base_line = 20,
   worktree_line = 20,
}, 1, #metadata)
assert(line == 2, "reload should follow the same source file and source line")

line = worktree.find_reload_line({
  { source_path = "src/one.lua", kind = "delete", base_line = 40 },
  { source_path = "src/one.lua", kind = "add", insertion_anchor = 40 },
}, {
  source_path = "src/one.lua",
  kind = "add",
  insertion_anchor = 40,
}, 1, 2)
assert(line == 2, "reload should preserve added-line insertion anchors")

line = worktree.find_reload_line({
  { source_path = "src/one.lua", kind = "hunk" },
  { source_path = "src/one.lua", kind = "hunk" },
}, {
  source_path = "src/one.lua",
  kind = "hunk",
}, 2, 2)
assert(line == 2, "reload should keep the nearest hunk header")

line = worktree.find_reload_line(metadata, {
  source_path = "src/missing.lua",
  kind = "context",
  worktree_line = 20,
}, 7, 2)
assert(line == 2, "reload should clamp the fallback rendered line")

print("worktree_test: all assertions passed")
