local exports = {}

function exports.Reload()
  for name, _ in pairs(package.loaded) do
    if name:match('^config') then
      package.loaded[name] = nil
    end
  end

  dofile(vim.env.MYVIMRC)
  vim.notify("Neovim configuration reloaded!", vim.log.levels.INFO)
end

return exports
