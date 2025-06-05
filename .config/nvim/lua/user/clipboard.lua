local exports = {}

function exports.set()
  if vim.fn.has("wsl") ~= 0 then
    -- If in wsl, do NOT check has('clipboard') and just set things
    -- See: https://github.com/neovim/neovim/issues/8017
    vim.opt.clipboard:append "unnamedplus"

    -- This might be an interesting alternative: https://stackoverflow.com/a/76388417

    vim.g.clipboard = {
      name = 'WslClipboard',
      copy = {
         ["+"] = 'clip.exe',
         ["*"] = 'clip.exe',
      },
      paste = {
         ["+"] = 'powershell.exe -c [Console]::Out.Write($(Get-Clipboard -Raw).tostring().replace("`r", ""))',
         ["*"] = 'powershell.exe -c [Console]::Out.Write($(Get-Clipboard -Raw).tostring().replace("`r", ""))',
      },
      cache_enabled = 0,
    }
  else
    if vim.fn.has("clipboard") then
        vim.opt.clipboard = "unnamed"
        if vim.fn.has("xterm_clipboard") then
            vim.opt.clipboard = "unnamedplus"
        end
    end
  end
end
exports.set()

return exports
