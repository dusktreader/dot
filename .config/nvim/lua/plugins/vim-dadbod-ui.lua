return {
  -- DB tui
  "kristijanhusak/vim-dadbod-ui",
  dependencies = {
    {
      "tpope/vim-dadbod",
      lazy = true,
    }, {
      "kristijanhusak/vim-dadbod-completion",
      lazy = true,
      ft = {
        "sql",
        "mysql",
        "plsql",
      },
    },
  },
  config = function(_, opts)
    vim.print("ARE WE GOING TO WRAP OR NOT?")
    vim.cmd [[
      echom "TRYING THE GODDAMNED WRAPPING MADNESS"
      if exists('*db#adapter#postgresql#interactive')
        echom "ORIGINAL EXISTS"
        if !exists('g:OrigDbAdapterPostgresInteractive')
          echom "WRAPPER DOES NOT EXIST"
          let g:OrigDbAdapterPostgresInteractive = function('db#adapter#postgresql#interactive')
          function! db#adapter#postgresql#interactive(...) abort
            echom "WRAPPER"
            try
              echom "BEFORE WRAPPED CALL"
              return call(g:OrigDbAdapterPostgresInteractive, a:000)
              echom "AFTER WRAPPED CALL"
            catch
              throw string(v:exception)
            endtry
          endfunction
        else
          echom "WRAPPER EXISTS"
        endif
      else
        echom "ORIGINAL DOES NOT EXIST"
      endif
    ]]
  end,
}
