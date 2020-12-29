# ============================================================================
# FILE: lsp/workspace_symbols.py
# AUTHOR: Takahiro Shirasaka <tk.shirasaka@gmail.com>
# License: MIT license
# ============================================================================

from denite.util import relpath
from denite.source.file import Source as File


class Source(File):
    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'lsp/workspace_symbols'
        self.kind = 'file'

    def gather_candidates(self, context):
        candidates = self.vim.call('luaeval', 'require("denite-utils.lsp").workspace_symbols()')
        return [{
            'word': '{}:{},{} {}'.format(relpath(self.vim, x['filename']), x['lnum'], x['col'], x['text']),
            'action__path': x['filename'],
            'action__line': x['lnum'],
            'action__col': x['col'],
        } for x in candidates]
