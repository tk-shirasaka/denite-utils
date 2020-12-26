" ============================================================================
" FILE: command.py
" AUTHOR: Takahiro Shirasaka <tk.shirasaka@gmail.com>
" License: MIT license
" ============================================================================

let s:bookmarkfile = expand('~/.local/share/nvim/bookmark')

function! denite_utils#get_bookmark() abort
    return findfile(s:bookmarkfile) == '' ? [] : readfile(s:bookmarkfile)
endfunction

function! denite_utils#set_bookmark(bookmark, action) abort
    let s:bookmarks = denite_utils#get_bookmark()
    if a:action == 'add'
        call add(s:bookmarks, a:bookmark)
    elseif a:action == 'delete'
        call filter(s:bookmarks, 'v:val != a:bookmark')
    end
    call writefile(sort(s:bookmarks), s:bookmarkfile)
endfunction
