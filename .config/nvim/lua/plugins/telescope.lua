return {
  -- Fuzzy finder in neovim
  "nvim-telescope/telescope.nvim",
  tag = "0.1.8",
  dependencies = {
    -- Enable telescope ui for select contexts
    { "nvim-telescope/telescope-ui-select.nvim" },
  },
  opts = {
    pickers = {
      find_files = {
        hidden = true,
        -- this would require tlescope.utils
        -- cwd = utils.buffer_dir(),
      },
    },
   extensions = {
      ["ui-select"] = {},
    },
  },
  config = function(_, opts)
    require("telescope").setup(opts)
    require("telescope").load_extension("ui-select")
  end,
}
