-- Grab the home directory for use throughout
local home = vim.fn.expand("$HOME")

-- Turn off vi compatibility mode
vim.o.compatible = false

-- Disable wrapping by default
vim.o.wrap = false

-- Show line numbers
vim.o.number = true
vim.o.relativenumber = true

-- Maintain undo history between sessions
vim.o.undofile = true
vim.o.undodir = home .. "/.local/share/nvim/undodir"

-- Always show a status line
-- vim.opt.laststatus = 2

-- Recommended for Avante
vim.opt.laststatus = 3

-- Makes backspace behave the way you would expect
vim.o.backspace = "indent,eol,start"

-- Keep the cursor away from the edge of the screen
vim.o.scrolloff = 3
vim.o.sidescrolloff = 10

-- Keep the cursor in the current column when jumping to other lines
vim.o.startofline = false

-- Show trailing spaces, tabs, non-breakable space characters
vim.opt.list = true

-- Show fancy characters for tab and trailing whitespace
vim.opt.listchars = {
    tab = " ",
    trail = ""
}

-- Remember the last 10000 commands
vim.opt.history = 10000

-- Don't give the attention message when an existing swap file is found
vim.opt.shortmess:append("A")

-- Highlight all matches for a search
vim.opt.hlsearch = true


-- Enable the mouse in all modes
vim.opt.mouse = "a"

-- Show the first match to a search as you type it
vim.opt.incsearch = true

-- Put backup files and swap files in a sane place
vim.opt.backup = true
vim.opt.writebackup = true
vim.opt.backupdir = home .. "/.local/share/nvim/backup/"
vim.opt.directory = home .. "/.local/share/nvim/swap/"

-- Use the right number of spaces instead of a tab
vim.opt.tabstop = 4
vim.opt.shiftwidth = 4
vim.opt.expandtab = true
vim.opt.smarttab = true

-- Format for automatic wrapping
vim.opt.formatoptions = "cqjr"

-- Gui colors?
vim.opt.termguicolors = true

-- Prevent DAP from changing the current buffer to a breakpoint if the file is already open in another buffer
vim.opt.switchbuf = "useopen,uselast"
