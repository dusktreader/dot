execute pathogen#infect()
try
    call virtualenv#activate()
catch
    " No virtualenv to activate
endtry
execute pathogen#infect('~/.vim/bundle2/{}')
execute pathogen#helptags()

" fix up rtp a bit to exclude rusty old default scripts if they exist
" if exists("g:loaded_pathogen")
"     let list = []
"     for dir in pathogen#split(&rtp)
"         if dir !~# '/usr/share/vim/vimfiles'
"             call add(list, dir)
"         endif
"     endfor
"     let &rtp = pathogen#join(list)
" endif

let g:virtualenv_auto_activate=1
let g:airline_powerline_fonts=1
let g:airline_theme='simple'

" Load a vimrc for the current project if available
if filereadable("etc/vim/vimrc.local")
    source etc/vim/vimrc.local
endif

" Turn off vi compatibility mode
set nocompatible

" Explicitly activate plugins
filetype plugin indent on

" Turn on syntax highlighting
syntax enable

" Remaps K to split lines under cursor
nnoremap K i<CR><Esc>

" Puts in column markers for 80 and 120 characters
set colorcolumn=80
set colorcolumn+=100
highlight ColorColumn ctermbg=4

" Remove trailing whitespace on save
autocmd BufWritePre  * :%s/\s\+$//e

" Execute flake8 against python files on save
autocmd BufWritePost *.py call Flake8()

" Shows ine numbers
set number

" Tells vim to always show a status line
set laststatus=2

" Enables smart indentation for newlines
set smartindent

" Makes vim uses the right number of spaces instead of a tab
set tabstop=4
set shiftwidth=4
set expandtab
set smarttab

" Makes backspace behave the way you would expect
set backspace=indent,eol,start

" Sets scroll offsets to keep the cursor away from the edge of the screen
set scrolloff=3
set sidescrolloff=10

" Keeps the cursor in the current column when jumping to other lines
set nostartofline

" Shows an underscore where there are trailing whitespaces
set list listchars=trail:_

" Sets the leader character for commands
let mapleader=","

" Makes vim remember the last 100000 commands
set history=100000

" Put backup files and swap files in a sane place
set backup
set writebackup
set backupdir=~/.vim/local/backup/
set directory=~/.vim/local/swap/

" Don't give the attention message when an existing swap file is found
set shortmess+=A

" highlights all matches for a search
set hlsearch

" Enables the mouse in all modes
set mouse=a

" Show the first match to a search as you type it
set incsearch

" Make the background color dark
set background=dark

" Automatically change current directory to the file being edited
set autochdir

" Put yanked text in the 'clipboard' buffer.  Will not fucking work!!!
if has('clipboard')
    set clipboard=unnamed
    if has('xterm_clipboard')
        set clipboard+=unnamedplus
    endif
endif

