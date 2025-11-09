-- Bootstrap lazy.nvim
local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not (vim.uv or vim.loop).fs_stat(lazypath) then
  local lazyrepo = "https://github.com/folke/lazy.nvim.git"
  local out = vim.fn.system({ "git", "clone", "--filter=blob:none", "--branch=stable", lazyrepo, lazypath })
  if vim.v.shell_error ~= 0 then
    vim.api.nvim_echo({
      { "Failed to clone lazy.nvim:\n", "ErrorMsg" },
      { out, "WarningMsg" },
      { "\nPress any key to exit..." },
    }, true, {})
    vim.fn.getchar()
    os.exit(1)
  end
end
vim.opt.rtp:prepend(lazypath)

local disable_plugins = vim.env.LAZY_DISABLE_PLUGINS == "1"

if disable_plugins then
    vim.notify("Plugins disabled - use :LazyPick to load individual plugins")

    _G.lazy_load_picker = function()
        local names = {}
        local ok_cfg, cfg = pcall(require, "lazy.core.config")
        if ok_cfg and cfg and cfg.plugins then
            for name, _ in pairs(cfg.plugins) do
                table.insert(names, name)
            end
        end

        if vim.tbl_isempty(names) then
            vim.notify("No plugins configured", vim.log.levels.WARN)
            return
        end

        vim.ui.select(
            names,
            { prompt = "Load plugin:" },
            function(choice)
                if not choice then
                    return
                end
                local ok, err = pcall(require("lazy").load, { plugins = { choice } })
                if ok then
                    vim.notify("Loaded plugin: " .. choice, vim.log.levels.INFO)
                else
                    vim.notify("Failed to load " .. choice .. ": " .. tostring(err), vim.log.levels.ERROR)
                end
            end
        )
    end
    vim.api.nvim_create_user_command("LazyPick", function() _G.lazy_load_picker() end, {})
end

-- Setup lazy.nvim - always load specs but conditionally enable plugins
require("lazy").setup({
  spec = {
    { import = "plugins" }
  },
  defaults = {
    -- lazy = true,
    enabled = not disable_plugins,
  },
  checker = {
    enabled = false,
    notify = true,
    frequency = 3600,
    check_pinned = false,
  },
  dev = {
    path = "~/src/dusktreader",
    patterns = {},
  },
})
