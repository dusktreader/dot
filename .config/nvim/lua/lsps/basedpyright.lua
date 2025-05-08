vim.lsp.config(
  "basedpyright",
  {
    capabilities = require("blink.cmp").get_lsp_capabilities(),
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
    },
  }
)

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
