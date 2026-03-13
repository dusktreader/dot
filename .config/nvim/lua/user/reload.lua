local exports = {}

function exports.Reload()
  for name, _ in pairs(package.loaded) do
    if name:match('^config') or name:match('^user') or name:match('^lsps') or name:match('^plugins') then
      package.loaded[name] = nil
    end
  end

  dofile(vim.env.MYVIMRC)
  vim.notify("Neovim configuration reloaded!", vim.log.levels.INFO)
end

return exports
