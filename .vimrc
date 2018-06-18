" Enable powerline fonts for airline
let g:airline_powerline_fonts=1

" Set the airline theme
let g:airline_theme='simple'

" load a vimrc for the current project if available
if filereadable("etc/vim/vimrc.local")
    source etc/vim/vimrc.local
endif

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

" Remaps F5 to open the gundo graph
nnoremap <leader>G :GundoToggle<CR>

" Puts in column markers for 80, 100, and 120 characters
set colorcolumn=80
set colorcolumn+=100
set colorcolumn+=120
highlight ColorColumn ctermbg=4

" remove trailing whitespace right before writing file
autocmd bufwritepre  * :%s/\s\+$//e

" Strips leading and tailing whitespace from a string
function! Strip(input_string)
    " Shamelessly copied from http://stackoverflow.com/a/4479072/642511
    return substitute(a:input_string, '^\s*\(.\{-}\)\s*\n*$', '\1', '')
endfunction

" shows flake8 indicators in the gutter
let g:flake8_show_in_gutter=1

" hook for behaviors following writes
function! PostWrite()
    let current_file = expand('%:t')

    " For python, run flake8 against the current file
    if &filetype == 'python'
        " Set up flake8 to use appropriate config
        let toplevel = Strip(system('git rev-parse --show-toplevel'))
        let config_dir = toplevel . '/etc/flake8'
        let config_file = ''
        if match(current_file, "^test_") != -1
            let config_file = config_dir . '/' .  'test-style-config.ini'
        else
            let config_file = config_dir . '/' .  'src-style-config.ini'
        endif
        if filereadable(config_file)
            echom "config file selected as " . config_file
            let g:flake8_config_file = config_file
        else
            echom "config_file isn't readable"
            let g:flake8_config_file = ''
        endif
        call Flake8()
    endif

endfunction

" Execute flake8 against python files on save
augroup dotautocommands
    autocmd!
    autocmd BufWritePost * call PostWrite()
augroup END

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

" Let me edit crontab on osx without whining about backups
autocmd filetype crontab setlocal nobackup nowritebackup

" Set indentation for javascript and html files
autocmd filetype html setlocal tabstop=2 shiftwidth=2
autocmd filetype javascript setlocal tabstop=2 shiftwidth=2

" Map <TAB> to swithc windows
nmap <TAB> <C-W>w

" Map ,e to open nerdtree on the current file
nnoremap <leader>e :NERDTreeFind<CR>

" Map ,RR to reload vimrc
nnoremap <leader>RR :source $MYVIMRC <CR>

" Put yanked text in the 'clipboard' buffer.  Will not fucking work!!!
if has('clipboard')
    set clipboard=unnamed
    if has('xterm_clipboard')
        set clipboard+=unnamedplus
    endif
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
nmap <silent> <leader>t :w<CR> :TestNearest<CR>
nmap <silent> <leader>tv :w<CR> :TestNearest --verbose<CR>
nmap <silent> <leader>tvv :w<CR> :TestNearest --verbose --verbose<CR>
nmap <silent> <leader>T :w<CR> :TestFile --maxfail=1<CR>
nmap <silent> <leader>l :w<CR> :TestLast<CR>
let test#strategy = "dispatch"
let test#python#runner = 'pytest'

" Shortcut for navigating to the test file for a particular source file
function! JumpToTest()
    execute ":edit " . system('find-test-file ' . expand('%'))
endfunction
nmap <leader>gt :call JumpToTest()<CR>

" Shortcut for navigating to the source file for a particular test file
function! JumpToSource()
    execute ":edit " . system('find-source-file ' . expand('%'))
endfunction
nmap <leader>gi :call JumpToSource()<CR>

" Starts sphinx-view for the current file
nmap <leader>v :Start! sphinx-view %<CR>

" Map ,aa to Tabularize on space after comma (or colon for dicts)
nmap <leader>aa :Tab /,\zs<CR>
vmap <leader>aa :Tab /,\zs<CR>
nmap <leader>aad :Tab /:\zs<CR>
vmap <leader>aad :Tab /:\zs<CR>
"
" map ,tt to transpose
vmap <leader>tt :!transpose<CR>
vmap <leader>ttd :!transpose --to-dict<CR>

" Map ,AA to arrange columns
nmap <leader>AA :%ArrangeColumn<CR>
vmap <leader>AA :ArrangeColumn<CR>
nmap <leader>UA :%UnArrangeColumn<CR>
vmap <leader>UA :UnArrangeColumn<CR>
