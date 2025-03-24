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

    vim.keymap.set('n', '<leader>K',  vim.lsp.buf.hover, opts)
    vim.keymap.set('n', '<leader>gd', vim.lsp.buf.definition, opts)
    vim.keymap.set('n', '<leader>gD', vim.lsp.buf.declaration, opts)
    vim.keymap.set('n', '<leader>gi', vim.lsp.buf.implementation, opts)
    vim.keymap.set('n', '<leader>go', vim.lsp.buf.type_definition, opts)
    vim.keymap.set('n', '<leader>gr', vim.lsp.buf.references, opts)
    vim.keymap.set('n', '<leader>gs', vim.lsp.buf.signature_help, opts)
    vim.keymap.set('n', '<leader>rn', vim.lsp.buf.rename, opts)
    vim.keymap.set("n", "<leader>ca", vim.lsp.buf.code_action)
    -- vim.keymap.set({'n', 'x'}, '<F3>', '<cmd>lua vim.lsp.buf.format({async = true})<cr>', opts)

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

local lspconfig = require('lspconfig')

function based_new_cfg(config, root_dir)
  -- See if there is a local virtual env (as uv uses)
  local venv_path = root_dir .. "/.venv/bin/python"
  if vim.fn.filereadable(venv_path) == 1 then
    config.settings.python.pythonPath = venv_path
    return
  end

  local pyproject_path = root_dir .. "/pyproject.toml"
  if not vim.fn.filereadable(pyproject_path) then
    return
  end

  -- Get pyright to use poetry's virtual environment
  -- Adapted from from: https://www.reddit.com/r/neovim/comments/wls43h/pyright_lsp_configuration_for_python_poetry/
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
  -- return {
  --   cmd = {"based", "lsp"},
  --   filetypes = {"python"},
  --   root_pattern = {"pyproject.toml", ".git", ".venv", "setup.py", "setup.cfg", "requirements.txt"},
  --   root_dir = lspconfig.util.root_pattern("pyproject.toml", ".git", ".venv", "setup.py", "setup.cfg", "requirements.txt"),
  --   settings = {
  --     python = {
  --       analysis = {
  --         typeCheckingMode = "off",
  --       },
  --     },
  --   },
  -- }
end

lspconfig.basedpyright.setup({
  on_new_config = based_new_cfg,
  settings = {
    basedpyright = {
      analysis = {
        diagnosticSeverityOverrides = {
          reportAny = false,
          reportExplicitAny = false,
        },
      },
    },
  }
})

lspconfig.ts_ls.setup {
  exclude = {"node_modules"}
}

lspconfig.lua_ls.setup {
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
    Lua = {}
  }
}
