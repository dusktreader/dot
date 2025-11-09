vim.lsp.config(
  "terraform-ls",
  {
    cmd = { "terraform-ls", "serve" },
    capabilities = require("blink.cmp").get_lsp_capabilities(),
    filetypes = { "terraform", "terraform-vars" },
  }
)
vim.lsp.enable({"terraform-ls"})
