vim.lsp.config(
  "ty",
  {
    capabilities = require("blink.cmp").get_lsp_capabilities(),
    filetypes = { "python" },
    on_attach = function(client, _)
      local pyproject_path = client.root_dir .. "/pyproject.toml"
      if not vim.fn.filereadable(pyproject_path) then
        return
      end

      local lines = vim.fn.readfile(pyproject_path)
      local uses_poetry = false
      for _, line in ipairs(lines) do
        local begin, _ = string.find(line, "tool.poetry")
        if begin ~= nil then
          uses_poetry = true
          break
        end
      end

      local env = ""
      if uses_poetry then
        env = vim.trim(
          vim.fn.system('cd "' .. client.root_dir .. '" && poetry env info --path 2>/dev/null')
        )
      else
        -- uv / generic venv: prefer .venv in the project root
        local venv_python = client.root_dir .. "/.venv/bin/python"
        if vim.fn.filereadable(venv_python) == 1 then
          env = client.root_dir .. "/.venv"
        end
      end

      if string.len(env) > 0 then
        if client.settings.python == nil then
          client.settings.python = {}
        end
        client.settings.python.pythonPath = env .. "/bin/python"
      end
    end,
    settings = {
      ty = {
        -- ty language server settings
        -- Configuration is primarily done through pyproject.toml [tool.ty] section
      },
    },
  }
)
vim.lsp.enable({"ty"})
