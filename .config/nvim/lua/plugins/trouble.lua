return {
  "folke/trouble.nvim",
  dependencies = { "nvim-tree/nvim-web-devicons" },
  keys = {
    { "<leader>xx", "<cmd>Trouble diagnostics toggle<cr>",                        desc = "Trouble Project Diagnostics" },
    { "<leader>xb", "<cmd>Trouble diagnostics toggle filter.buf=0<cr>",           desc = "Trouble Buffer Diagnostics" },
    { "<leader>xr", "<cmd>Trouble lsp_references toggle<cr>",                     desc = "Trouble LSP References" },
    { "<leader>xd", "<cmd>Trouble lsp_definitions toggle<cr>",                    desc = "Trouble LSP Definitions" },
    { "<leader>xq", "<cmd>Trouble qflist toggle<cr>",                             desc = "Trouble Quickfix" },
    { "<leader>xt", "<cmd>Trouble todo toggle<cr>",                               desc = "Trouble TODOs" },
  },
  opts = {
    modes = {
      diagnostics    = { auto_close = true },
      lsp_references = { auto_close = true },
      lsp_definitions = { auto_close = true },
      qflist         = { auto_close = true },
      todo           = { auto_close = true },
    },
  },
}
