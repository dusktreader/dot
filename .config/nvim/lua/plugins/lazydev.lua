return {
  -- Configures the LuaLS for edting neovim configs
  "folke/lazydev.nvim",
  dependencies = {
    "rcarriga/nvim-dap-ui",
  },
  opts = {
    library = { "nvim-dap-ui" },
  },
}
