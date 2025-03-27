return {
  -- Fuzzy finder in neovim
  "nvim-telescope/telescope.nvim",
  tag = "0.1.8",
  opts = {
    pickers = {
        find_files = {
            hidden = true,
            -- this would require tlescope.utils
            -- cwd = utils.buffer_dir(),
        }
    }
  }
}
