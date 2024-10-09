" Auto install plug-vim if not installed
let data_dir = has('nvim') ? stdpath('data') . '/site' : '~/.vim'
if empty(glob(data_dir . '/autoload/plug.vim'))
  silent execute '!curl -fLo '.data_dir.'/autoload/plug.vim --create-dirs  https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim'
  autocmd VimEnter * PlugInstall --sync | source $MYVIMRC
endif

source ~/.config/nvim/plugins.vim

" Make sure the backup directory exists correctly
let g:backupdir=expand(stdpath('data') . '/backup')
if !isdirectory(g:backupdir)
   call mkdir(g:backupdir, "p")
endif
let &backupdir=g:backupdir

" Sets the leader character for commands
let mapleader=","

" Tells vim to use indentation based on filetype
filetype indent on

" make bell visual only
set visualbell

" Turn off vi compatibility mode
set nocompatible

" Turn on syntax highlighting
syntax enable

" Disable wrapping by default
set nowrap

" Remaps K to split lines under cursor
nnoremap K i<CR><Esc>

" Maintain undo history between sessions
set undofile
set undodir=~/.local/share/nvim/undodir

" remove trailing whitespace right before writing file
autocmd bufwritepre  * :%s/\s\+$//e

" Shows line numbers
set number

" Tells vim to always show a status line
set laststatus=2

" Makes backspace behave the way you would expect
set backspace=indent,eol,start

" Sets scroll offsets to keep the cursor away from the edge of the screen
set scrolloff=3
set sidescrolloff=10

" Keeps the cursor in the current column when jumping to other lines
set nostartofline

" Shows an underscore where there are trailing whitespaces
set list listchars=trail:_

" Makes vim remember the last 10000 commands
set history=10000

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

" Map <TAB> to switch windows
nmap <TAB> <C-W>w

" Enables smart indentation for newlines (without dedenting # lines)
" see: http://vim.wikia.com/wiki/Restoring_indent_after_typing_hash
set cindent
set cinkeys-=0#
set indentkeys-=0#

" Put backup files and swap files in a sane place
set backup
set writebackup
set backupdir=~/.local/share/nvim/backup/
set directory=~/.local/share/nvim/swap/

" Puts in column markers based on black config (if exists)
set termguicolors
let g:line_length=trim(system('get-black-line-length'))
execute "set colorcolumn=" . join(range(g:line_length + 1,335), ',')
highlight ColorColumn ctermbg=0 guibg=#333333
highlight EndOfBuffer ctermbg=0 guibg=#333333
highlight PMenu ctermbg=0 guibg=DarkSlateGray
highlight PMenuSel ctermbg=0 guibg=DarkBlue

" Makes vim uses the right number of spaces instead of a tab
set tabstop=4
set shiftwidth=4
set expandtab
set smarttab
autocmd FileType html setlocal tabstop=2 softtabstop=2 shiftwidth=2
autocmd FileType javascript setlocal tabstop=2 softtabstop=2 shiftwidth=2
autocmd FileType typescript setlocal tabstop=2 softtabstop=2 shiftwidth=2
autocmd FileType yaml       setlocal tabstop=2 softtabstop=2 shiftwidth=2
autocmd FileType yml        setlocal tabstop=2 softtabstop=2 shiftwidth=2

" Cursor settings for windows terminal
if &term =~ '^xterm'
    " normal mode
    let &t_EI .= "\<Esc>[0 q"
    " insert mode
    let &t_SI .= "\<Esc>[6 q"
endif

" ---Clipboard Settings---

let has_wsl=eval(trim(system("cat /proc/version | grep -qi wsl2 && echo 1 || echo 0")))
if(has_wsl)
    " If in wsl, do NOT check has('clipboard') and just set things
    " See: https://github.com/neovim/neovim/issues/8017
    set clipboard+=unnamedplus
    let g:clipboard = {
          \   'name': 'WslClipboard',
          \   'copy': {
          \      '+': 'clip.exe',
          \      '*': 'clip.exe',
          \    },
          \   'paste': {
          \      '+': 'powershell.exe -c [Console]::Out.Write($(Get-Clipboard -Raw).tostring().replace("`r", ""))',
          \      '*': 'powershell.exe -c [Console]::Out.Write($(Get-Clipboard -Raw).tostring().replace("`r", ""))',
          \   },
          \   'cache_enabled': 0,
          \ }
    " let g:clipboard = {
    "       \   'name': 'win32yank-wsl',
    "       \   'copy': {
    "       \      '+': 'win32yank.exe -i --crlf',
    "       \      '*': 'win32yank.exe -i --crlf',
    "       \    },
    "       \   'paste': {
    "       \      '+': 'win32yank.exe -o --lf',
    "       \      '*': 'win32yank.exe -o --lf',
    "       \   },
    "       \   'cache_enabled': 0,
    "       \ }
else
    " On non WSL systems, check for clipboard availability
    if has('clipboard')
        set clipboard=unnamed
        if has('xterm_clipboard')
            set clipboard=unnamedplus
        endif
    endif
endif

" ---Key Mappings---

" Map <TAB> to switch windows
nmap <TAB> <C-W>w

" Map ,e to open nerdtree on the current file
nnoremap <leader>e :NERDTreeFind<CR>

" Map ,RR to reload vimrc
nnoremap <leader>RR :source $MYVIMRC <CR>

" Map ,EE to edit vim config
nnoremap <leader>EE :e $MYVIMRC <CR>

" Map ,NN to clear search pattern hilight
nnoremap <leader>NN :noh <CR>

" Map ,pp to paste from windows clipboard in WSL
nnoremap <silent> <leader>pp :r !powershell.exe -Command Get-Clipboard<CR>

" Starts sphinx-view for the current file
nmap <leader>v :Start! sphinx-view %<CR>

" Map ,ss to source the current vim file
nnoremap <leader>ss :so %<CR>

" Map ,be to open buffer-tree-explorer
nnoremap <leader>be :Tree<CR>


" ---Plugin Settings---

" Have NERDTree close when I open a file
let NERDTreeQuitOnOpen=1

" Automatically delete the buffere when I delete or remanem a file
let NERDTreeAutoDeleteBuffer=1

" Set the default size of the NERDTree window
let NERDTreeWinSize=80

" Use compressed buffer-tree-explorer
let g:buffer_tree_explorer_compress=1

" Close buffer-tree-explorer when buffer is selected
let g:buffertree_close_on_enter=1

" Bindings for vim-bookmark
let g:bookmark_no_default_key_mappings = 1
nmap <leader>bb <Plug>BookmarkToggle
nmap <leader>gb <Plug>BookmarkNext
nmap <leader>gB <Plug>BookmarkPrev
nmap <leader>BB <Plug>BookmarkShowAll

" Mappings for vim-test/neotest?
nmap <silent> <leader>t :w<CR> :TestNearest --color=yes<CR>
nmap <silent> <leader>ts :w<CR> :TestNearest --color=yes --capture=no<CR>
nmap <silent> <leader>tv :w<CR> :TestNearest --color=yes --verbose<CR>
nmap <silent> <leader>tvv :w<CR> :TestNearest --color=yes --verbose --verbose<CR>
nmap <silent> <leader>T :w<CR> :TestFile --color=yes --maxfail=1<CR>
nmap <silent> <leader>l :w<CR> :TestLast --color=yes<CR>
nmap <silent> <leader>lv :w<CR> :TestLast --color=yes --verbose<CR>
nmap <silent> <leader>lvv :w<CR> :TestLast --color=yes --verbose --verbose<CR>
let test#python#runner = 'pytest'
let test#python#pytest#options = { 'file': '--no-cov', 'nearest': '--no-cov' }
let test#strategy = "neovim"

" Map ,aa to Tabularize on space after comma (or colon for dicts)
nmap <leader>aa :Tab /,\zs<CR>
vmap <leader>aa :Tab /,\zs<CR>
nmap <leader>aad :Tab /:\zs<CR>
vmap <leader>aad :Tab /:\zs<CR>

" map ,tt to transpose
vmap <leader>tt :!transpose<CR>
vmap <leader>ttd :!transpose --to-dict<CR>

" Map ,AA to arrange columns
nmap <leader>AA :%ArrangeColumn<CR>
vmap <leader>AA :ArrangeColumn<CR>
nmap <leader>UA :%UnArrangeColumn<CR>
vmap <leader>UA :UnArrangeColumn<CR>

" CoC Settings
nmap <leader>ff :CocConfig<CR>
autocmd FileType python let b:coc_root_patterns = ["pyproject.toml"]
" For CoC, use tab for trigger completion with characters ahead and navigate.
" NOTE: Use command ':verbose imap <tab>' to make sure tab is not mapped by
" other plugin before putting this into your config.
inoremap <silent><expr> <TAB>
      \ coc#pum#visible() ? coc#pum#next(1) :
      \ CheckBackspace() ? "\<Tab>" :
      \ coc#refresh()
inoremap <expr><S-TAB> coc#pum#visible() ? coc#pum#prev(1) : "\<C-h>"

" Make <CR> to accept selected completion item or notify coc.nvim to format
" <C-g>u breaks current undo, please make your own choice
inoremap <silent><expr> <CR> coc#pum#visible() ? coc#pum#confirm()
                              \: "\<C-g>u\<CR>\<c-r>=coc#on_enter()\<CR>"

function! CheckBackspace() abort
 let col = col('.') - 1
  return !col || getline('.')[col - 1]  =~# '\s'
endfunction

" CoC GoTo code navigation.
nmap <silent> gd <Plug>(coc-definition)
nmap <silent> gy <Plug>(coc-type-definition)
nmap <silent> gi <Plug>(coc-implementation)
nmap <silent> gr <Plug>(coc-references)

" arg-wrap settings and bindings
let g:argwrap_tail_comma=1
nnoremap <leader>a :ArgWrap<CR>

" Add a word to the user dictionary
nmap <leader>sp :CocCommand cSpell.addWordToUserDictionary<CR>
