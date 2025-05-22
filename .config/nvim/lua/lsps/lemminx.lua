vim.lsp.config(
  "lemminx",
  {
    capabilities = require("blink.cmp").get_lsp_capabilities(),
    filetypes = { "xml" },
  }
)
vim.lsp.enable({"lemminx"})
