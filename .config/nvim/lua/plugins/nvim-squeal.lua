return {
  dir = "~/src/dusktreader/nvim-squeal",
  cond = function()
    return vim.fn.isdirectory(vim.fn.expand("~/src/dusktreader/nvim-squeal")) == 1
  end,
  dependencies = {
    "nvim-lua/plenary.nvim",
    "ColinKennedy/mega.cmdparse",
    "ColinKennedy/mega.logging",
  },
  opts = {
    log_level = "debug",
  },
}
