" Some dumb-shit stuff that makes python indentation work
" let vim_path=fnamemodify(resolve(expand('<sfile>:p')), ':h') . '/.vim'
" let &runtimepath=vim_path.',$VIMRUNTIME'

" Enable powerline fonts for airline
let g:airline_powerline_fonts=1

" Set the airline theme
let g:airline_theme='simple'

" load a vimrc for the current project if available
if filereadable("etc/vim/vimrc.local")
    source etc/vim/vimrc.local
endif

" make bell visual only
se visualbell

" Turn off vi compatibility mode
set nocompatible

" Explicitly activate plugins
filetype plugin indent on

" disable bracketed paste mode
set t_BE=

" Add .pydon files to python syntax highlighting
au BufNewFile,BufRead *.pydon set filetype=python

" Turn on syntax highlighting
syntax enable

" Sets the leader character for commands
let mapleader=","

" Remaps K to split lines under cursor
nnoremap K i<CR><Esc>

" Disable wrapping by default
set nowrap

" Map ,W to toggle wrapping
nnoremap <leader>W :set nowrap!<CR>

" Maintain undo history between sessions
set undofile
set undodir=~/.vim/undodir

" Puts in column markers for 80, 100, and 120 characters
set termguicolors
let g:line_length=trim(system('get-black-line-length'))
execute "set colorcolumn=" . join(range(g:line_length + 1,335), ',')
highlight ColorColumn ctermbg=0 guibg=#333333
highlight EndOfBuffer ctermbg=0 guibg=#333333
highlight PMenu ctermbg=0 guibg=DarkSlateGray
highlight PMenuSel ctermbg=0 guibg=DarkBlue

" remove trailing whitespace right before writing file
autocmd bufwritepre  * :%s/\s\+$//e

" Shows line numbers
set number

" Tells vim to always show a status line
set laststatus=2

" Enables smart indentation for newlines (without dedenting # lines)
" see: http://vim.wikia.com/wiki/Restoring_indent_after_typing_hash
set cindent
set cinkeys-=0#
set indentkeys-=0#

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

" Have NERDTree close when I open a file
let NERDTreeQuitOnOpen=1

" Automatically delete the buffere when I delete or remanem a file
let NERDTreeAutoDeleteBuffer=1

" Set the default size of the NERDTree window
let NERDTreeWinSize=80

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

" Put yanked text in the 'clipboard' buffer for linux systems.
if has('clipboard')
    set clipboard=unnamed
    if has('xterm_clipboard')
        set clipboard+=unnamedplus
    endif
endif

" Map ,pp to paste from windows clipboard in WSL
nnoremap <silent> <leader>pp :r !powershell.exe -Command Get-Clipboard<CR>

" Copy yank to windows clipboard in WSL
let s:clip = '/mnt/c/Windows/System32/clip.exe'
if executable(s:clip)
    augroup WSLYank
        autocmd!
        autocmd TextYankPost * call system('echo '.shellescape(join(v:event.regcontents, "\<CR>")).' | '.s:clip)
    augroup END
end

" Cursor settings for windows terminal
if &term =~ '^xterm'
    " normal mode
    let &t_EI .= "\<Esc>[0 q"
    " insert mode
    let &t_SI .= "\<Esc>[6 q"
endif


" Replaces commonly mistyped commands with the correct one
" See: http://stackoverflow.com/questions/3878692/aliasing-a-command-in-vim/3879737#3879737
fun! SetupCommandAlias(from, to)
  exec 'cnoreabbrev <expr> '.a:from
        \ .' ((getcmdtype() is# ":" && getcmdline() is# "'.a:from.'")'
        \ .'? ("'.a:to.'") : ("'.a:from.'"))'
endfun
call SetupCommandAlias("E","e")

" Mappings for vim-test
nmap <silent> <leader>t :w<CR> :TestNearest --color=yes<CR>
nmap <silent> <leader>tv :w<CR> :TestNearest --color=yes --verbose<CR>
nmap <silent> <leader>tvv :w<CR> :TestNearest --color=yes --verbose --verbose<CR>
nmap <silent> <leader>T :w<CR> :TestFile --color=yes --maxfail=1<CR>
nmap <silent> <leader>l :w<CR> :TestLast --color=yes<CR>
nmap <silent> <leader>lv :w<CR> :TestLast --color=yes --verbose<CR>
nmap <silent> <leader>lvv :w<CR> :TestLast --color=yes --verbose --verbose<CR>
let test#strategy = "dispatch"
let test#python#runner = 'poetry run pytest'

" Shortcut for navigating to the test file for a particular source file
function! JumpToTest()
    execute ":edit " . system('find-test-file ' . expand('%'))
endfunction
nmap <leader>gt :call JumpToTest()<CR>

" Shortcut for navigating to the source file for a particular test file
" function! JumpToSource()
"     execute ":edit " . system('find-source-file ' . expand('%'))
" endfunction
" nmap <leader>gi :call JumpToSource()<CR>

" Starts sphinx-view for the current file
nmap <leader>v :Start! sphinx-view %<CR>

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

" typescript-vim settings
" let g:typescript_indent_disable = 1

" ALE Settings
highlight ALEWarning ctermbg=DarkGreen
highlight ALEError ctermbg=DarkRed
let g:ale_fix_on_save = 0
let g:ale_python_flake8_options="--max-line-length=" . g:line_length
let g:ale_disable_lsp = 1


" CoC Settings
nmap <leader>ff :CocConfig<CR>
function! s:check_back_space() abort
  let col = col('.') - 1
  return !col || getline('.')[col - 1]  =~# '\s'
endfunction

" Use tab for trigger completion with characters ahead and navigate.
" NOTE: Use command ':verbose imap <tab>' to make sure tab is not mapped by
" other plugin before putting this into your config.
inoremap <silent><expr> <TAB>
      \ pumvisible() ? "\<C-n>" :
      \ <SID>check_back_space() ? "\<TAB>" :
      \ coc#refresh()
inoremap <expr><S-TAB> pumvisible() ? "\<C-p>" : "\<C-h>"

" GoTo code navigation.
nmap <silent> gd <Plug>(coc-definition)
nmap <silent> gy <Plug>(coc-type-definition)
nmap <silent> gi <Plug>(coc-implementation)
nmap <silent> gr <Plug>(coc-references)
