return {
  -- Colorize color code
  "catgoose/nvim-colorizer.lua",
  event = "BufReadPre",
  init = function ()
    vim.opt.termguicolors = true
  end,
}
