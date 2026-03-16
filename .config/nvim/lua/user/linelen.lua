local textwidth = vim.opt.textwidth:get()
local overlength_pattern = string.format("\\%%%dv.\\+", textwidth + 1)

local overlength_group = vim.api.nvim_create_augroup("OverLength", { clear = true })

vim.api.nvim_create_autocmd("ColorScheme", {
  group = overlength_group,
  callback = function()
    vim.api.nvim_set_hl(0, "OverLength", { bg = "#ff0000", fg = "#ffffff" })
  end,
})

vim.api.nvim_create_autocmd("BufWinEnter", {
  group = overlength_group,
  callback = function()
    vim.fn.matchadd("OverLength", overlength_pattern)
  end,
})

vim.api.nvim_set_hl(0, "OverLength", { bg = "#ff0000", fg = "#ffffff" })
vim.fn.matchadd("OverLength", overlength_pattern)
