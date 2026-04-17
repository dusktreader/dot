vim.lsp.config(
  "gopls",
  {
    capabilities = require("blink.cmp").get_lsp_capabilities(),
    filetypes = { "go" },
    cmd = { "gopls" },
    root_dir = vim.fs.root(0, { "go.mod", ".git" }),
    on_init = function(client)
      vim.system(
        { "goenv", "exec", "go", "env", "GOPATH", "GOROOT" },
        { text = true },
        function(result)
          if result.code ~= 0 then return end
          local lines = vim.split(vim.trim(result.stdout), "\n")
          if #lines < 2 then return end
          vim.schedule(function()
            client.config.settings.gopls.env = {
              GOPATH = lines[1],
              GOROOT = lines[2],
            }
            client.notify("workspace/didChangeConfiguration", { settings = client.config.settings })
          end)
        end
      )
    end,
    settings = {
      gopls = {
        staticcheck = true,
        buildFlags = { "-tags=integration" },
        env = {},
      },
    },
  }
)
vim.lsp.enable({"gopls"})
