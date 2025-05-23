-- Sets the leader character for commands
vim.g.mapleader=","

-- Sets the leader characters for buffer specific commands
vim.g.maplocalleader = "\\"

-- Tells neovim to use indentation based on the file-type
vim.filetype.indent = true

vim.diagnostic.config({
  virtual_text = {
    current_line = true,
    prefix = "●",
  },
  float = {
    border = "rounded",
    focusable = true,
  },
})
