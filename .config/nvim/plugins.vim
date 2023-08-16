call plug#begin('~/.vim/plugged')

Plug 'neoclide/coc.nvim', {'branch': 'release'}
Plug 'preservim/nerdtree'
Plug 'el-iot/buffer-tree-explorer'
Plug 'cespare/vim-toml'
Plug 'chaoren/vim-wordmotion'
Plug 'rhysd/committia.vim'
Plug 'tpope/vim-fugitive'
Plug 'airblade/vim-gitgutter'
Plug 'Vimjas/vim-python-pep8-indent'
Plug 'MattesGroeger/vim-bookmarks'
Plug 'FooSoft/vim-argwrap'

Plug 'vim-test/vim-test'
"All for neotest...I hope it's worth all this
" Plug 'nvim-lua/plenary.nvim'
" Plug 'nvim-treesitter/nvim-treesitter'
" Plug 'antoinemadec/FixCursorHold.nvim'
" Plug 'nvim-neotest/neotest'
" Plug 'nvim-neotest/neotest-plenary'
" Plug 'nvim-neotest/neotest-python'
" Plug 'nvim-neotest/neotest-vim-test'

call plug#end()
