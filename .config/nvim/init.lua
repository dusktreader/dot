require("config.lazy")
require("config.lualine")
require("config.telescope")
require("config.lsp")
require("config.cmp")
require("config.keymap")
require("config.neotest")
require("config.treesj")
require("config.tokyonight")
require("config.ibl")
require("config.treesitter")
require("config.miniai")
require("config.fterm")
require("config.colorizer")
require("config.dapui")

-- Grab the home directory for use throughout
local home = vim.fn.expand("$HOME")

-- Sets the leader character for commands
vim.mapleader=","

-- Tells neovim to use indentation based on the file-type
vim.filetype.indent = true

-- Doesn't seem to do anything any more...
-- make bell visual only
-- vim.o.visualbell = true

-- Turn off vi compatibility mode
vim.o.compatible = false

-- Disable wrapping by default
vim.o.wrap = false

-- Show line numbers
vim.o.number = true

-- Maintain undo history between sessions
vim.o.undofile = true
vim.o.undodir = home .. "/.local/share/nvim/undodir"

-- Always show a status line
vim.opt.laststatus = 2

-- Makes backspace behave the way you would expect
vim.o.backspace = "indent,eol,start"

-- Keep the cursor away from the edge of the screen
vim.o.scrolloff = 3
vim.o.sidescrolloff = 10

-- Keep the cursor in the current column when jumping to other lines
vim.o.startofline = false

-- Enable spell-check
vim.opt.spelllang = "en_us"
vim.opt.spell = true

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

-- Set the color-scheme
vim.api.nvim_cmd(
  {
    cmd = "colorscheme",
    args = {"tokyonight"},
  },
  {}
)

-- Remove all trailing whitespace on write
vim.api.nvim_create_autocmd(
  "BufWritePre",
  {
    pattern = {"*"},
    command = ":%s/\\s\\+$//e",
  }
)

-- Remove windows newlines (usually brought in from copy-pasta)
vim.api.nvim_create_autocmd(
  "BufWritePre",
  {
    pattern = {"*"},
    command = ":%s/\\r//e",
  }
)

-- Set tabstops for specified file types
vim.api.nvim_create_autocmd(
  "FileType",
  {
    pattern = {"lua", "html", "javascript", "typescript", "yaml", "yml", "typescriptreact"},
    callback = function()
      vim.opt_local.tabstop = 2
      vim.opt_local.softtabstop = 2
      vim.opt_local.shiftwidth = 2
      vim.opt_local.expandtab = true
      vim.opt_local.smarttab = true
    end
  }
)
--
-- Set tabstops for specified file types
vim.api.nvim_create_autocmd(
  "FileType",
  {
    pattern = {"go"},
    callback = function()
      vim.opt_local.tabstop = 4
      vim.opt_local.shiftwidth = 4
      vim.opt_local.expandtab = false
      vim.opt_local.smarttab = false
    end
  }
)

local setLineLength = function()
  local result = vim.system({"get-config-line-length"}, { text = true }):wait()
  local line_length = vim.trim(result["stdout"])
  local range = {}
  for i=line_length + 1, 1335 do
    table.insert(range, i)
  end
  local columns = table.concat(range, ",")
  vim.opt.colorcolumn=columns
end
setLineLength()

if vim.fn.has("wsl") then
  -- If in wsl, do NOT check has('clipboard') and just set things
  -- See: https://github.com/neovim/neovim/issues/8017
  vim.opt.clipboard:append "unnamedplus"

  -- This might be an interesting alternative: https://stackoverflow.com/a/76388417

  vim.g.clipboard = {
    name = 'WslClipboard',
    copy = {
       ["+"] = 'clip.exe',
       ["*"] = 'clip.exe',
    },
    paste = {
       ["+"] = 'powershell.exe -c [Console]::Out.Write($(Get-Clipboard -Raw).tostring().replace("`r", ""))',
       ["*"] = 'powershell.exe -c [Console]::Out.Write($(Get-Clipboard -Raw).tostring().replace("`r", ""))',
    },
    cache_enabled = 0,
  }
else
  if vim.fn.has("clipboard") then
      vim.opt.clipboard = "unnamed"
      if vim.fn.has("xterm_clipboard") then
          vim.opt.clipboard = "unnamedplus"
      end
  end
end
