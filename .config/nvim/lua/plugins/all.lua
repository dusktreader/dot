return {

    -- File navigation in a side-bar
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

    -- Explore open buffers, but show file tree structure
    {
      "el-iot/buffer-tree-explorer",
      init = function()
        -- Use compressed buffer-tree-explorer
        vim.g.buffer_tree_explorer_compress = 1

        -- Close buffer-tree-explorer when buffer is selected
        vim.g.buffertree_close_on_enter = 1
      end
    },

    -- Have word motions respect things like camelCase, snake_case, and others
    { "chaoren/vim-wordmotion" },

    -- Provide a nice view of diff and status while editing commit messages
    { "rhysd/committia.vim" },

    -- Awesome git bindings for vim
    { "tpope/vim-fugitive" },

    -- Show git status line-by-line in the gutter
    { "airblade/vim-gitgutter" },

    -- Bookmark navigation in vim
    {
      "MattesGroeger/vim-bookmarks",
      init = function()
        vim.g.bookmark_no_default_key_mappings = 1
      end
    },

    --{ "FooSoft/vim-argwrap" },

    -- Powerful treesitter integration into neovim
    { "nvim-treesitter/nvim-treesitter" },

    -- A nice color scheme
    { "folke/tokyonight.nvim" },

    -- A bunch of stuff that's used by a lot of plugins
    { "nvim-lua/plenary.nvim" },

    -- Fuzzy finder in neovim
    { "nvim-telescope/telescope.nvim", tag = "0.1.8" },

    -- A really nice status line plugin
    { "nvim-lualine/lualine.nvim" },

    -- Webicons for neovim. Not sure I need this any more...
    { "nvim-tree/nvim-web-devicons" },

    -- Testing in neovim
    {
      "nvim-neotest/neotest",
      dependencies = {
        "nvim-neotest/nvim-nio",
        "nvim-lua/plenary.nvim",
        "antoinemadec/FixCursorHold.nvim",
        "nvim-treesitter/nvim-treesitter",
      },
    },

    -- Python extension for neotest
    { "nvim-neotest/neotest-python" },

    -- A colleciton of niceties for lsp clients in neovim
    { "VonHeikemen/lsp-zero.nvim", branch = "v4.x" },

    -- A protable package manager for neovim external dependencies
    { "williamboman/mason.nvim" },

    -- Some glue for mason and lspconfig
    { "williamboman/mason-lspconfig.nvim" },

    -- Basic, default configurations for lsp clients in neovim
    { "neovim/nvim-lspconfig" },

    -- More integration with lsp
    { "hrsh7th/cmp-nvim-lsp" },

    -- Auto-completion in neovim
    { "hrsh7th/nvim-cmp" },

    -- CSV Reader with color and formatting
    { "mechatroner/rainbow_csv" },

    -- Configures the LuaLS for edting neovim configs
    { "folke/lazydev.nvim" },

    -- Highlight the currently selected word and show where else it's used
    { "RRethy/vim-illuminate" },

    -- Automatic folding/splitting of blocks using treesitter
    {
      "Wansmer/treesj",
      dependencies = { "nvim-treesitter/nvim-treesitter" },
    },

    -- Show the span of code blocks
    { "lukas-reineke/indent-blankline.nvim" },

    -- Copilot integration into neovim
    {
      "zbirenbaum/copilot.lua",
      cmd = "Copilot",
      event = "InsertEnter",
    },

    -- Use pep8 style indentation for python
    { "Vimjas/vim-python-pep8-indent" },

    -- Extend a/i textobjects
    { "echasnovski/mini.ai" },

    -- Show key mappings
    {
      "folke/which-key.nvim",
      event = "VeryLazy",
      opts = {
        preset = "helix",
        delay = 750,
      },
      keys = {
        {
          "<leader>?",
          function()
            require("which-key").show({ global = false })
          end,
          desc = "Buffer Local Keymaps (which-key)",
        },
      },
    },

    -- Enable a floating terminal window
    { "numToStr/FTerm.nvim" },

    -- Colorize color code
    { "norcalli/nvim-colorizer.lua" },
}
