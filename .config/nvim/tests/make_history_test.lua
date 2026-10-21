local repo = vim.fn.getcwd()
package.path = repo .. "/.config/nvim/lua/?.lua;" .. package.path
local root = vim.fn.tempname()
local project = root .. "/project"
local other_project = root .. "/other-project"
vim.fn.mkdir(project, "p")
vim.fn.mkdir(other_project, "p")
vim.fn.mkdir(root .. "/state", "p")
vim.env.XDG_STATE_HOME = root .. "/state"
vim.cmd("cd " .. vim.fn.fnameescape(project))
project = vim.fn.getcwd()
vim.fn.writefile({ "check: ;" }, project .. "/Makefile")

local picker_items
Snacks = {
  picker = {
    select = function(items, options, callback)
      picker_items = vim.deepcopy(items)
      if callback and options.prompt ~= "Make command history" then callback(items[1]) end
    end,
  },
  terminal = { open = function() return nil end },
}
vim.ui.input = function(options, callback) callback(options.default) end

local make = dofile(repo .. "/.config/nvim/lua/user/make.lua")
make.run_edit()

local history_path = vim.fn.stdpath("state") .. "/make-history/" .. vim.fn.sha256(project) .. ".json"
local saved = vim.fn.readfile(history_path)
assert(vim.deep_equal(vim.fn.json_decode(table.concat(saved, "\n")), { "make check" }), "command should be saved")

make = dofile(repo .. "/.config/nvim/lua/user/make.lua")
make.history()
assert(vim.deep_equal(picker_items, { "make check" }), "saved command should load after module reload")

local oversized = {}
local expected = {}
for i = 30, 1, -1 do
  local cmd = "make target" .. i
  table.insert(oversized, cmd)
  if #expected < 25 then table.insert(expected, cmd) end
end
vim.fn.writefile({ vim.fn.json_encode(oversized) }, history_path)
make = dofile(repo .. "/.config/nvim/lua/user/make.lua")
make.history()
assert(vim.deep_equal(picker_items, expected), "history should show only the 25 most recent commands")

local plugin = dofile(repo .. "/.config/nvim/lua/plugins/make.lua")
plugin.init()
vim.cmd("MakeHistoryClear")
local cleared = vim.fn.json_decode(table.concat(vim.fn.readfile(history_path), "\n"))
assert(vim.deep_equal(cleared, {}), "clear command should remove persisted history")

local notification
vim.notify = function(message) notification = message end
make = dofile(repo .. "/.config/nvim/lua/user/make.lua")
make.history()
assert(notification == "No make command history", "cleared history should be empty")

vim.cmd("cd " .. vim.fn.fnameescape(other_project))
make.history()
assert(notification == "No make command history", "each directory should have separate history")

print("make_history_test: all assertions passed")
