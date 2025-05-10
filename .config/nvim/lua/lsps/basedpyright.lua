vim.lsp.config(
  "basedpyright",
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

      if not uses_poetry then
        return
      end

      local env = vim.trim(
        vim.fn.system('cd "' .. client.root_dir .. '" && poetry env info --path 2>/dev/null')
      )

      if string.len(env) > 0 then
        if client.settings.python == nil then
          client.settings.python = {}
        end
        client.settings.python.pythonPath = env .. "/bin/python"
      end
    end,
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
vim.lsp.enable({"basedpyright"})
