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

-- Mapping to reload init script
vim.keymap.set("n", "<leader>RR", function() require('user.reload').Reload() end)

-- Mapping to edit vim config
vim.keymap.set("n", "<leader>EE", ":e $MYVIMRC <CR>", { noremap = true })

-- Mapping to clear search pattern highlight
vim.keymap.set("n",  "<leader>NN", ":noh <CR>", { noremap = true })

-- Mapping to source the current vim file
vim.keymap.set("n",  "<leader>ss", ":so %<CR>", { noremap = true })

-- Mappings for vim-bookmark
vim.keymap.set("n", "<leader>bb", "<Plug>BookmarkToggle")
vim.keymap.set("n", "<leader>gb", "<Plug>BookmarkNext")
vim.keymap.set("n", "<leader>gB", "<Plug>BookmarkPrev")
vim.keymap.set("n", "<leader>BB", "<Plug>BookmarkShowAll")

-- Mappings for toggleterm
vim.keymap.set("n", "`", "<CMD>ToggleTerm<CR>")
vim.keymap.set("t", "`", "<CMD>ToggleTerm<CR>")

-- Mappings to resize splits
vim.keymap.set({"n", "i", "v"}, "<Down>",  "<CMD>resize +2<CR>")
vim.keymap.set({"n", "i", "v"}, "<Up>",    "<CMD>resize -2<CR>")
vim.keymap.set({"n", "i", "v"}, "<Right>", "<CMD>vertical resize +4<CR>")
vim.keymap.set({"n", "i", "v"}, "<Left>",  "<CMD>vertical resize -4<CR>")

-- Mapping to open lsp hover
vim.keymap.set("n", "<leader>H", function() vim.lsp.buf.hover() end)

-- Mapping to open issue hover
vim.keymap.set("n", "<leader>h", function() vim.diagnostic.open_float() end)

-- Mapping to toggle the undotree
vim.keymap.set("n", "<leader>u", vim.cmd.UndotreeToggle)

-- Dropbar mappings
vim.keymap.set('n', '<Leader>;', function() require("dropbar.api").pick() end, { noremap = true })

-- Restart LSP
vim.keymap.set("n", "<leader>ll", "<cmd>RestartLSP<cr>", { noremap = true })

-- Dismiss Noice notifications
vim.keymap.set("n", "<leader>n", "<cmd>Noice dismiss<cr>", { noremap = true })

-- Toggle render-markdown
vim.keymap.set("n", "<leader>M", "<cmd>RenderMarkdown toggle<cr>", { noremap = true })
