return {
  -- File navigation in a side-bar
  "preservim/nerdtree",
  init = function()
    -- Have NERDTree close when I open a file
    vim.g.NERDTreeQuitOnOpen = 1

    -- Automatically delete the buffer when I delete or rename a file
    vim.g.NERDTreeAutoDeleteBuffer = 1

    -- Set the default size of the NERDTree window
    vim.g.NERDTreeWinSize = 80
  end,
}
