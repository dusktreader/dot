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
    if vim.bo.buftype == "terminal" then
      vim.wo.colorcolumn = ""
      return
    end
    local tw = vim.bo.textwidth
    if tw == 0 then
      vim.wo.colorcolumn = ""
      return
    end
    vim.wo.colorcolumn = "+0"
    local pattern = string.format("\\%%%dv.\\+", tw + 1)
    local win = vim.api.nvim_get_current_win()
    local existing = vim.w[win].overlength_match_id
    if existing then
      pcall(vim.fn.matchdelete, existing)
    end
    vim.w[win].overlength_match_id = vim.fn.matchadd("OverLength", pattern)
  end,
})

vim.api.nvim_set_hl(0, "OverLength", { bg = "#ff0000", fg = "#ffffff" })
