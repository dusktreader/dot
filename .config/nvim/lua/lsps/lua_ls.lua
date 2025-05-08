vim.lsp.config(
  "lua_ls",
  {
    capabilities = require("blink.cmp").get_lsp_capabilities(),
    on_init = function(client)
      client.config.settings.Lua = vim.tbl_deep_extend('force', client.config.settings.Lua, {
        runtime = {
          version = 'LuaJIT'
        },
        workspace = {
          checkThirdParty = false,
          library = {
            vim.env.VIMRUNTIME
          }
        }
      })
    end,
    settings = {
      Lua = {},
    },
  }
)
