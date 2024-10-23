return {
    { "preservim/nerdtree" },
    { "el-iot/buffer-tree-explorer" },
    { "chaoren/vim-wordmotion" },
    { "rhysd/committia.vim" },
    { "tpope/vim-fugitive" },
    { "airblade/vim-gitgutter" },
    {
      "MattesGroeger/vim-bookmarks",
      init = function()
        vim.g.bookmark_no_default_key_mappings = 1
      end
    },

    --{ "FooSoft/vim-argwrap" },

    { "nvim-treesitter/nvim-treesitter" },
    { "folke/tokyonight.nvim" },

    { "nvim-lua/plenary.nvim" },
    { "nvim-telescope/telescope.nvim", tag = "0.1.8" },

    { "nvim-lualine/lualine.nvim" },
    { "nvim-tree/nvim-web-devicons" },

    --{ "vim-test/vim-test" },
    {
      "nvim-neotest/neotest",
      dependencies = {
        "nvim-neotest/nvim-nio",
        "nvim-lua/plenary.nvim",
        "antoinemadec/FixCursorHold.nvim",
        "nvim-treesitter/nvim-treesitter",
      },
    },
    { "nvim-neotest/neotest-python" },

    { "VonHeikemen/lsp-zero.nvim", branch = "v4.x" },
    { "williamboman/mason.nvim" },
    { "williamboman/mason-lspconfig.nvim" },
    { "neovim/nvim-lspconfig" },
    { "hrsh7th/cmp-nvim-lsp" },
    { "hrsh7th/nvim-cmp" },

    { "mechatroner/rainbow_csv" },

    { "folke/lazydev.nvim" },

    { "RRethy/vim-illuminate" },

    {
      "Wansmer/treesj",
      dependencies = { "nvim-treesitter/nvim-treesitter" },
    },
}

-- "
-- Plug 'Vimjas/vim-python-pep8-indent'
