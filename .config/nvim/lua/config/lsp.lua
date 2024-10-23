-- Reserve a space in the gutter
-- This will avoid an annoying layout shift in the screen
vim.opt.signcolumn = 'yes'

-- Add cmp_nvim_lsp capabilities settings to lspconfig
-- This should be executed before you configure any language server
local lspconfig_defaults = require('lspconfig').util.default_config
lspconfig_defaults.capabilities = vim.tbl_deep_extend(
  'force',
  lspconfig_defaults.capabilities,
  require('cmp_nvim_lsp').default_capabilities()
)

-- This is where you enable features that only work
-- if there is a language server active in the file
vim.api.nvim_create_autocmd('LspAttach', {
  desc = 'LSP actions',
  callback = function(event)
    local opts = {buffer = event.buf}

    vim.keymap.set('n', '<leader>K', '<cmd>lua vim.lsp.buf.hover()<cr>', opts)
    vim.keymap.set('n', '<leader>gd', '<cmd>lua vim.lsp.buf.definition()<cr>', opts)
    vim.keymap.set('n', '<leader>gD', '<cmd>lua vim.lsp.buf.declaration()<cr>', opts)
    vim.keymap.set('n', '<leader>gi', '<cmd>lua vim.lsp.buf.implementation()<cr>', opts)
    vim.keymap.set('n', '<leader>go', '<cmd>lua vim.lsp.buf.type_definition()<cr>', opts)
    vim.keymap.set('n', '<leader>gr', '<cmd>lua vim.lsp.buf.references()<cr>', opts)
    vim.keymap.set('n', '<leader>gs', '<cmd>lua vim.lsp.buf.signature_help()<cr>', opts)
    -- vim.keymap.set('n', '<F2>', '<cmd>lua vim.lsp.buf.rename()<cr>', opts)
    -- vim.keymap.set({'n', 'x'}, '<F3>', '<cmd>lua vim.lsp.buf.format({async = true})<cr>', opts)
    -- vim.keymap.set('n', '<F4>', '<cmd>lua vim.lsp.buf.code_action()<cr>', opts)
  end,
})

require('mason').setup({})
require('mason-lspconfig').setup({
  handlers = {
    function(server_name)
      require('lspconfig')[server_name].setup({})
    end,
  },
})

-- Get pyright to use poetry's virtual environment
-- Adapted from from: https://www.reddit.com/r/neovim/comments/wls43h/pyright_lsp_configuration_for_python_poetry/
local lspconfig = require('lspconfig')
lspconfig.pyright.setup {
  on_new_config = function(config, root_dir)
    local pyproject_file = io.open(root_dir .. "/pyproject.toml")
    if (pyproject_file == nil) then
      return
    end
    if (vim.g.pyright_poetry_roots == nil) then
      vim.g.pyright_poetry_roots = {}
    end
    if (vim.g.pyright_poetry_roots[root_dir] == nil) then
      local env = vim.trim(
        vim.fn.system('cd "' .. root_dir .. '"; poetry env info --path 2>/dev/null')
      )
      if string.len(env) > 0 then
        -- This suuuucks: https://github.com/nanotee/nvim-lua-guide#caveats-3
        local stupid_temp = vim.g.pyright_poetry_roots
        stupid_temp[root_dir] = env
        vim.g.pyright_poetry_roots = stupid_temp
        local python_path = (env .. '/bin/python')
        config.settings.python.pythonPath = python_path
      else
      end
    else
      config.settings.python.pythonPath = vim.g.pyright_poetry_roots[root_dir] .. '/bin/python'
    end
  end
}

-- Yoinked from neotest-python
-- if lib.files.exists("pyproject.toml") then
--   print("LOOKING IN PYPROJECT.TOML")
--   local success, exit_code, data = pcall(
--     lib.process.run,
--     { "poetry", "run", "poetry", "env", "info", "-p" },
--     { stdout = true }
--   )
--   print("DATA: " .. data.stdout)
--   print("SUCCESS: " .. tostring(success))
--   print("EXIT_CODE: " .. tostring(exit_code))
--   if success and exit_code == 0 then
--     local venv = data.stdout:gsub("\n", "")
--     if venv then
--       print("LOOKING FOR PYTHON COMMAND")
--       python_command_mem[root] = { Path:new(venv, "bin", "python").filename }
--       print("PYTHON COMMAND: " .. Path:new(venv, "bin", "python").filename)
--       return python_command_mem[root]
--     end
--   end
-- end
--
--
--
-- local root = base.get_root(position.path) or vim.loop.cwd() or ""


require'lspconfig'.lua_ls.setup {
  on_init = function(client)
    -- if client.workspace_folders then
    --   local path = client.workspace_folders[1].name
    --   if vim.uv.fs_stat(path..'/.luarc.json') or vim.uv.fs_stat(path..'/.luarc.jsonc') then
    --     return
    --   end
    -- end

    client.config.settings.Lua = vim.tbl_deep_extend('force', client.config.settings.Lua, {
      runtime = {
        -- Tell the language server which version of Lua you're using
        -- (most likely LuaJIT in the case of Neovim)
        version = 'LuaJIT'
      },
      -- Make the server aware of Neovim runtime files
      workspace = {
        checkThirdParty = false,
        library = {
          vim.env.VIMRUNTIME
          -- Depending on the usage, you might want to add additional paths here.
          -- "${3rd}/luv/library"
          -- "${3rd}/busted/library",
        }
        -- or pull in all of 'runtimepath'. NOTE: this is a lot slower and will cause issues when working on your own configuration (see https://github.com/neovim/nvim-lspconfig/issues/3189)
        -- library = vim.api.nvim_get_runtime_file("", true)
      }
    })
  end,
  settings = {
    Lua = {}
  }
}