return {
  -- Powerful treesitter integration into neovim
  "nvim-treesitter/nvim-treesitter",
  branch = "main",
  version = false,
  build = ":TSUpdate",
  lazy = false,
  opts = {
    ensure_installed = {
      "bash",
      "c",
      "cpp",
      "css",
      "go",
      "html",
      "javascript",
      "json",
      "lua",
      "markdown",
      "markdown_inline",
      "python",
      "query",
      "regex",
      "rust",
      "typescript",
      "yaml",
      "vim",
      "vimdoc",
    },
    auto_install = true,
    indent = {
      enable = true,
      disable = { "python" },
    },
  },
  config = function(_, opts)
    -- On Apple Silicon, ensure parsers are compiled for ARM64
    if vim.fn.has("mac") == 1 and vim.fn.system("uname -m"):match("arm64") then
      vim.fn.setenv("CFLAGS", "-arch arm64")
      -- Prefer git clones over tree-sitter CLI to avoid x86_64 CLI issues from Mason
      local ok, install = pcall(require, "nvim-treesitter.install")
      if ok then
        install.prefer_git = true
      end
    end
    
    local ok, configs = pcall(require, "nvim-treesitter.configs")
    if ok then
      configs.setup(opts)
    else
      vim.notify("nvim-treesitter.configs not available yet. Try running :TSUpdate", vim.log.levels.WARN)
    end
  end,
}
