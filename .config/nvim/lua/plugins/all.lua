return {
    {
      "preservim/nerdtree",
      init = function()
        -- Have NERDTree close when I open a file
        vim.g.NERDTreeQuitOnOpen = 1

        -- Automatically delete the buffer when I delete or rename a file
        vim.g.NERDTreeAutoDeleteBuffer = 1

        -- Set the default size of the NERDTree window
        vim.g.NERDTreeWinSize = 80
      end
    },
    {
      "el-iot/buffer-tree-explorer",
      init = function()
        -- Use compressed buffer-tree-explorer
        vim.g.buffer_tree_explorer_compress = 1

        -- Close buffer-tree-explorer when buffer is selected
        vim.g.buffertree_close_on_enter = 1
      end
    },
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
