-- Set the color-scheme
vim.api.nvim_cmd(
  {
    cmd = "colorscheme",
    args = {"tokyonight"},
  },
  {}
)

-- Remove all trailing whitespace on write
vim.api.nvim_create_autocmd(
  "BufWritePre",
  {
    pattern = {"*"},
    command = ":%s/\\s\\+$//e",
  }
)

-- Remove windows newlines (usually brought in from copy-pasta)
vim.api.nvim_create_autocmd(
  "BufWritePre",
  {
    pattern = {"*"},
    command = ":%s/\\r//e",
  }
)

-- Set tabstops for specified file types
vim.api.nvim_create_autocmd(
  "FileType",
  {
    pattern = {"lua", "html", "javascript", "typescript", "yaml", "yml", "typescriptreact", "css", "json", "csv"},
    callback = function()
      vim.opt_local.tabstop = 2
      vim.opt_local.softtabstop = 2
      vim.opt_local.shiftwidth = 2
      vim.opt_local.expandtab = true
      vim.opt_local.smarttab = true
    end
  }
)

-- Set tabstops for specified file types
vim.api.nvim_create_autocmd(
  "FileType",
  {
    pattern = {"go"},
    callback = function()
      vim.opt_local.tabstop = 4
      vim.opt_local.shiftwidth = 4
      vim.opt_local.expandtab = false
      vim.opt_local.smarttab = false
    end
  }
)

local function ShowNeotestAdapterRoots()
  local ok, neotest = pcall(require, "neotest")
  if not ok then
    print("neotest not loaded")
    return
  end
  local path = vim.api.nvim_buf_get_name(0)
  print("File: " .. path)
  local adapters = neotest._config and neotest._config.adapters or {}
  print("Config: " .. #neotest._config)
  print("Adapters: " .. #adapters)
  -- adapters may be an array of adapter objects or constructor-returned tables
  for _, adapter in ipairs(adapters) do
    print("Processing adapter : " .. (adapter.name or "<unnamed adapter>"));
    if type(adapter) == "table" and adapter.root then
      local ok2, r = pcall(adapter.root, path)
      if ok2 and r then
        print( (adapter.name or "<unnamed adapter>") .. " root: " .. r)
      else
        print( (adapter.name or "<unnamed adapter>") .. " root: (nil)")
      end
    end
  end
end

vim.api.nvim_create_user_command("NeotestAdapterRoots", ShowNeotestAdapterRoots, {})
