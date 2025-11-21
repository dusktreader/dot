vim.lsp.config(
  "gopls",
  {
    capabilities = require("blink.cmp").get_lsp_capabilities(),
    filetypes = { "go" },
    cmd = { "gopls" },
    root_dir = vim.fs.root(0, { "go.mod", ".git" }),
    settings = {
      gopls = {
        staticcheck = true,
        buildFlags = { "-tags=integration" },
        env = {
          GOPATH = vim.fn.system("goenv exec go env GOPATH"):gsub("\n", ""),
          GOROOT = vim.fn.system("goenv exec go env GOROOT"):gsub("\n", ""),
        },
      },
    },
  }
)
vim.lsp.enable({"gopls"})
