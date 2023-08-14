if !has("python3")
  echo "vim has to be compiled with +python3 to run this"
  finish
endif

if exists('g:vim_code_whisperer_plugin_loaded')
  finish
endif

let s:plugin_root_dir = fnamemodify(resolve(expand('<sfile>:p')), ':h')

python3 << EOF
import sys
try:
    from vimwhisperer.vim import complete
except ImportError:
    print('To use this plugin, first install `pip3 install vimwhisperer`')
EOF

let g:vim_code_whisperer_plugin_loaded = 1

function! CodeWhisperer()
  python3 complete()
endfunction

command! -nargs=0 CodeWhisperer call CodeWhisperer()
