vim.lsp.config(
  "copilot-language-server",
  {
    capabilities = require("blink.cmp").get_lsp_capabilities(),
  }
)
vim.lsp.enable({"copilot-language-server"})
