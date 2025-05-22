vim.lsp.config(
  "ruff",
  {
    capabilities = require("blink.cmp").get_lsp_capabilities(),
    filetypes = { "python" },
  }
)
vim.lsp.enable({"ruff"})
