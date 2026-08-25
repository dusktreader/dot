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
  },
  config = function(_, opts)
    -- On Apple Silicon, ensure parsers are compiled for ARM64
    if vim.fn.has("mac") == 1 and vim.uv.os_uname().machine == "arm64" then
      vim.fn.setenv("CFLAGS", "-arch arm64")
      -- Prefer git clones over tree-sitter CLI to avoid x86_64 CLI issues from Mason
      local ok, install = pcall(require, "nvim-treesitter.install")
      if ok then
        install.prefer_git = true
      end
    end
    
    require("nvim-treesitter").setup({ install_dir = vim.fn.stdpath("data") .. "/site" })
    require("nvim-treesitter").install(opts.ensure_installed)
    vim.api.nvim_create_autocmd("FileType", {
      pattern = opts.ensure_installed,
      callback = function(args)
        vim.treesitter.start(args.buf)
      end,
    })
  end,
}
