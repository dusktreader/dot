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
    pattern = {"lua", "html", "javascript", "typescript", "yaml", "yml", "typescriptreact", "css", "json"},
    callback = function()
      vim.opt_local.tabstop = 2
      vim.opt_local.softtabstop = 2
      vim.opt_local.shiftwidth = 2
      vim.opt_local.expandtab = true
      vim.opt_local.smarttab = true
    end
  }
)

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
