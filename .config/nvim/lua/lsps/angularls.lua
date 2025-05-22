vim.lsp.config(
  "angularls",
  {
    capabilities = require("blink.cmp").get_lsp_capabilities(),
  }
)
vim.lsp.enable({"angularls"})
