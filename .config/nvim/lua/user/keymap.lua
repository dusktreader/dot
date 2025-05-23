-- Remaps K to split lines under cursor. Basically the inverse of J
vim.keymap.set("n", "K", "i<CR><Esc>", { noremap = true })

-- Mapping for toggling word wrap
vim.keymap.set("n", "<leader>W", "<cmd>set wrap!<CR>", { noremap = true })

-- Mappings to switch windows
vim.keymap.set("n", "<TAB>", "<C-w>w")
vim.keymap.set("n", "<C-k>", "<C-w>k")
vim.keymap.set("n", "<C-j>", "<C-w>j")
vim.keymap.set("n", "<C-h>", "<C-w>h")
vim.keymap.set("n", "<C-l>", "<C-w>l")

-- Mapping to escape terminal mode
vim.keymap.set("t", "<Esc><Esc><Esc>", "<C-\\><C-n>", { noremap = true })

-- Mapping to open nerdtree on the current file
vim.keymap.set("n", "<leader>e", ":Neotree<CR>", { noremap = true })


-- Mapping to reload init script
vim.keymap.set("n", "<leader>RR", function() require('config.user.reload').Reload() end)


-- Mapping to edit vim config
vim.keymap.set("n", "<leader>EE", ":e $MYVIMRC <CR>", { noremap = true })


-- Mapping to clear search pattern highlight
vim.keymap.set("n",  "<leader>NN", ":noh <CR>", { noremap = true })


-- Mapping to source the current vim file
vim.keymap.set("n",  "<leader>ss", ":so %<CR>", { noremap = true })


-- Mapping to open buffer-tree-explorer
vim.keymap.set("n", "<leader>be", function() require("telescope.builtin").buffers() end)


-- Mapping for Overseer
vim.keymap.set("n", "<leader>mt", "<cmd>OverseerToggle<cr>", { noremap = true })
vim.keymap.set("n", "<leader>mr", "<cmd>OverseerRun<cr>", { noremap = true })
vim.keymap.set("n", "<leader>mq", "<cmd>OverseerQuickAction<cr>", { noremap = true })

-- Mappings for vim-bookmark
vim.keymap.set("n", "<leader>bb", "<Plug>BookmarkToggle")
vim.keymap.set("n", "<leader>gb", "<Plug>BookmarkNext")
vim.keymap.set("n", "<leader>gB", "<Plug>BookmarkPrev")
vim.keymap.set("n", "<leader>BB", "<Plug>BookmarkShowAll")


-- Mappings for vim-test/neotest
vim.keymap.set("n", "<leader>t",  function () require("neotest").run.run() end)
vim.keymap.set("n", "<leader>T",  function () require("neotest").run.run(vim.fn.expand("%")) end)
vim.keymap.set("n", "<leader>TT", function () require("neotest").run.run(vim.uv.cwd()) end)
vim.keymap.set("n", "<leader>tl", function () require("neotest").run.run_last() end)
vim.keymap.set("n", "<leader>to", function () require("neotest").output.open({ enter = true, auto_close = true }) end)
vim.keymap.set("n", "<leader>tp", function () require("neotest").output_panel.toggle() end)
vim.keymap.set("n", "<leader>ts", function () require("neotest").summary.toggle() end)
vim.keymap.set("n", "<leader>tw", function () require("neotest").watch.toggle(vim.fn.expand("%")) end)
vim.keymap.set("n", "<leader>td", function () require("neotest").run.run({strategy = "dap"}) end)


-- Mappings for nvim-dap
vim.keymap.set("n", "<leader>db", require("dap").toggle_breakpoint)
vim.keymap.set("n", "<leader>dc", require("dap").continue)
vim.keymap.set("n", "<leader>do", require("dap").step_over)
vim.keymap.set("n", "<leader>di", require("dap").step_into)
vim.keymap.set("n", "<leader>dO", require("dap").step_out)
vim.keymap.set("n", "<leader>dt", require("dap-view").toggle)
vim.keymap.set("n", "<leader>dX", function ()
  local dap = require("dap")
  local dapview = require("dap-view")
  dap.disconnect()
  dap.close()
  dapview.close()
end)

-- Mappings for telescope
vim.keymap.set("n", "<leader>ff", "<cmd>Telescope find_files<cr>", { noremap = true })
vim.keymap.set("n", "<leader>fg", "<cmd>Telescope live_grep<cr>",  { noremap = true })
vim.keymap.set("n", "<leader>fb", "<cmd>Telescope buffers<cr>",    { noremap = true })
vim.keymap.set("n", "<leader>fh", "<cmd>Telescope help_tags<cr>",  { noremap = true })

vim.keymap.set("n", "<leader>sp", function () require("telescope.builtin").spell_suggest() end)


-- Mappings for trees
vim.keymap.set("n", "<leader>j", require("treesj").split)
vim.keymap.set("n", "<leader>k", require("treesj").join)


-- Mappings for toggleterm
vim.keymap.set("n", "`", "<CMD>ToggleTerm<CR>")
vim.keymap.set("t", "`", "<CMD>ToggleTerm<CR>")


-- Mappings to resize splits
vim.keymap.set({"n", "i", "v"}, "<Down>", "<CMD>resize +2<CR>")
vim.keymap.set({"n", "i", "v"}, "<Up>", "<CMD>resize -2<CR>")
vim.keymap.set({"n", "i", "v"}, "<Right>", "<CMD>vertical resize +4<CR>")
vim.keymap.set({"n", "i", "v"}, "<Left>", "<CMD>vertical resize -4<CR>")


-- Mapping to open lsp hover
vim.keymap.set("n", "<leader>H", function () vim.lsp.buf.hover() end)

-- Mapping to open issue hover
vim.keymap.set("n", "<leader>h", function () vim.diagnostic.open_float() end)

-- Mapping to toggle the undotree
vim.keymap.set("n", "<leader>u", vim.cmd.UndotreeToggle)

-- Dropbar mappings
vim.keymap.set('n', '<Leader>;', function () require("dropbar.api").pick() end, { noremap = true })

-- Mappings for Copilot Chat
vim.keymap.set("n", "<leader>AA", "<cmd>CopilotChatOpen<cr>", { noremap = true })

-- Restart LSP
vim.keymap.set("n", "<leader>ll", "<cmd>RestartLSP<cr>", { noremap = true })

-- Open the aerial code outline viewer
vim.keymap.set("n", "<leader>o", "<cmd>AerialOpen<cr>", { noremap = true })

-- Dismiss Noice notifications
vim.keymap.set("n", "<leader>n", "<cmd>Noice dismiss<cr>", { noremap = true })

-- Toggle render-markdown
vim.keymap.set("n", "<leader>M", "<cmd>RenderMarkdown toggle<cr>", { noremap = true })
