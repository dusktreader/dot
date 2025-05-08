vim.lsp.config(
  "pylsp",
  {
    capabilities = require("blink.cmp").get_lsp_capabilities(),
    settings = {
      pylsp = {
        plugins = {
          mypy = { enabled = true },
          autopep8 = { enabled = false },
          jedi_completion = { enabled = false },
          jedi_definition = { enabled = false },
          mccabe = { enabled = false },
          pycodestyle = { enabled = false },
          pyflakes = { enabled = false },
          yapf = { enabled = false },
        },
      },
    },
  }
)
