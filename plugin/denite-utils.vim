
call denite#custom#action('file,directory', 'rename',
            \ {context -> rename(context['targets'][0]['action__path'], input('', context['targets'][0]['action__path'], 'file'))}, 
            \ {'is_quit': 0, 'is_redraw': 1})
call denite#custom#action('file,directory', 'delete',
            \ {context -> denite#util#input_yesno(context['targets'][0]['action__path'].' is delete?') ? delete(context['targets'][0]['action__path'], 'rf') : ''},
            \ {'is_quit': 0, 'is_redraw': 1})
call denite#custom#action('directory', 'bookmark',
            \ {context -> denite_utils#set_bookmark(input('Alias : ').':'.context['targets'][0]['action__path'], 'add')})
