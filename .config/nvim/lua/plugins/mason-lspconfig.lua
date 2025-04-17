return {
  -- automated language server installation and configuration
  "williamboman/mason-lspconfig.nvim",
  dependencies = {
    "neovim/nvim-lspconfig",
    "williamboman/mason.nvim",
    "saghen/blink.cmp",
  },
  opts = {
    ensure_installed = {
      'typos_lsp',
      'basedpyright',
      'gopls',
      'lua_ls',
      'ruff',
      'pylsp',
    },
    handlers = {
      function (server_name)
        require('lspconfig')[server_name].setup({
          capabilities = require('blink.cmp').get_lsp_capabilities(),
        })
      end,
      ['pylsp'] = function ()
        require('lspconfig').pylsp.setup({
          capabilities = require('blink.cmp').get_lsp_capabilities(),
          settings = {
            pylsp = {
              plugins = {
                mypy = { enabled = true },
                autopep8 = { enabled = false },
                jedi_completion = { enabled = false },
                mccabe = { enabled = false },
                pycodestyle = { enabled = false },
                pyflakes = { enabled = false },
                yapf = { enabled = false },
              },
            },
          },
        })
      end,
      ['typos_lsp'] = function ()
        require('lspconfig').typos_lsp.setup({
          capabilities = require('blink.cmp').get_lsp_capabilities(),
          init_options = {
            config = "pyproject.toml",
          }
        })
      end,
      ['ruff'] = function ()
        require('lspconfig').ruff.setup({
          capabilities = require('blink.cmp').get_lsp_capabilities(),
        })
      end,
      ['basedpyright'] = function ()
        require('lspconfig').basedpyright.setup({
          capabilities = require('blink.cmp').get_lsp_capabilities(),
          -- on_new_config = poetry_helper,
          settings = {
            basedpyright = {
              analysis = {
                diagnosticSeverityOverrides = {
                  reportAny = false,
                  reportExplicitAny = false,
                  reportUnusedCallResult = false,
                },
              },
            },
          }
        })
      end,
      ['gopls'] = function ()
        require('lspconfig').gopls.setup({
          capabilities = require('blink.cmp').get_lsp_capabilities(),
          settings = {
            gopls = {
              staticcheck = true,
            },
          },
        })
      end,
      ['ts_ls'] = function ()
        require('lspconfig').ts_ls.setup({
          capabilities = require('blink.cmp').get_lsp_capabilities(),
          exclude = {"node_modules"}
        })
      end,
      ['lua_ls'] = function ()
        require('lspconfig').lua_ls.setup({
          capabilities = require('blink.cmp').get_lsp_capabilities(),
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
        })
      end
    },
  },
}




-- Add completion capabilities settings to lspconfig
-- This should be executed before you configure any language server
--local tinytoml = require('tinytoml')

-- local function poetry_helper(config, root_dir)
--   -- See if there is a local virtual env (as uv uses)
--   local venv_path = root_dir .. "/.venv"
--   if vim.fn.isdirectory(venv_path) == 1 then
--     return
--   end
--
--   local pyproject_path = root_dir .. "/pyproject.toml"
--   if not vim.fn.filereadable(pyproject_path) then
--     return
--   end
--
--   -- local pyproject = tinytoml.parse(pyproject_path)
--   -- print("PYPROJECT: " .. vim.inpspect(pyproject))
--
--   -- Get pyright to use poetry's virtual environment
--   -- Adapted from from: https://www.reddit.com/r/neovim/comments/wls43h/pyright_lsp_configuration_for_python_poetry/
--   if (vim.g.basedpyright_poetry == nil) then
--     vim.g.basedpyright_poetry = {}
--   end
--
--   if (vim.g.basedpyright_poetry[root_dir] == nil) then
--     local env = vim.trim(
--       vim.fn.system('cd "' .. root_dir .. '" && poetry env info --path 2>/dev/null')
--     )
--
--     if string.len(env) > 0 then
--       -- This suuuucks: https://github.com/nanotee/nvim-lua-guide#caveats-3
--       local stupid_temp = vim.g.basedpyright_poetry
--       stupid_temp[root_dir] = env
--       local function wtf(st)
--         vim.g.basedpyright_poetry = stupid_temp
--       end
--       local status, err = pcall(wtf)
--       if status then
--         print("OK")
--       else
--         print("NOT OK: " .. vim.inspect(err))
--       end
--     else
--       -- When we parse the toml file to determine if it's a poetry package, we might explode here on purpose
--       return
--     end
--   end
--   config.settings.python.pythonPath = vim.g.basedpyright_poetry[root_dir] .. '/bin/python'
-- end
