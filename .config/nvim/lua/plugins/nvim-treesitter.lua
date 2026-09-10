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
