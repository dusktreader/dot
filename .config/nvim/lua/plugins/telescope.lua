return {
  -- Fuzzy finder in neovim
  "nvim-telescope/telescope.nvim",
  tag = "0.1.8",
  dependencies = {
    -- Enable telescope ui for select contexts
    { "nvim-telescope/telescope-ui-select.nvim" },
  },
  keys = {
    { "<leader>ff", "<cmd>Telescope find_files<cr>",                                        desc = "Telescope Find Files",  noremap = true },
    { "<leader>fg", "<cmd>Telescope live_grep<cr>",                                         desc = "Telescope Live Grep",   noremap = true },
    { "<leader>fb", "<cmd>Telescope buffers<cr>",                                           desc = "Telescope Buffers",     noremap = true },
    { "<leader>fh", "<cmd>Telescope help_tags<cr>",                                         desc = "Telescope Help Tags",   noremap = true },
    { "<leader>be", function() require("telescope.builtin").buffers() end,                  desc = "Telescope Buffer List"  },
    { "<leader>sp", function() require("telescope.builtin").spell_suggest() end,            desc = "Telescope Spell Suggest" },
  },
  opts = {
    pickers = {
      find_files = {
        hidden = true,
        -- this would require telescope.utils
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
