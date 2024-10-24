lua << EOF
  require("config.init")
EOF

" Don't think this is necessary any more
" Enables smart indentation for newlines (without dedenting # lines)
" see: http://vim.wikia.com/wiki/Restoring_indent_after_typing_hash
" set cindent
" set cinkeys-=0#
" set indentkeys-=0#

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
else
    " On non WSL systems, check for clipboard availability
    if has('clipboard')
        set clipboard=unnamed
        if has('xterm_clipboard')
            set clipboard=unnamedplus
        endif
    endif
endif


" ---Plugin Settings---

" Have NERDTree close when I open a file
let NERDTreeQuitOnOpen=1

" Automatically delete the buffer when I delete or rename a file
let NERDTreeAutoDeleteBuffer=1

" Set the default size of the NERDTree window
let NERDTreeWinSize=80

" Use compressed buffer-tree-explorer
let g:buffer_tree_explorer_compress=1

" Close buffer-tree-explorer when buffer is selected
let g:buffertree_close_on_enter=1

" Do not use default vim-bookmark key mappings
let g:bookmark_no_default_key_mappings = 1

" Settings for vim-test/neotest
" let test#python#runner = 'pytest'
" let test#python#pytest#options = { 'file': '--no-cov', 'nearest': '--no-cov' }
" let test#strategy = "neovim"

" arg-wrap settings
let g:argwrap_tail_comma=1
