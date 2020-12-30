# ============================================================================
# FILE: lsp/diagnostics.py
# AUTHOR: Takahiro Shirasaka <tk.shirasaka@gmail.com>
# License: MIT license
# ============================================================================

import os
import sys

sys.path.insert(1, os.path.dirname(os.path.dirname(__file__)))

from utils import AsyncSource
from denite.util import relpath


class Source(AsyncSource):
    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'lsp/diagnostics'
        self.kind = 'file'
        self.vars['highlight'] = {
            'Header': {'pattern': r'[^:]*:\d\+:\d\+ \[.\{-}[:\]]'},
            'File': {'pattern': r'[^:]*:', 'parent': 'Header', 'link': 'Comment'},
            'Line': {'pattern': r'\d\+:\d\+', 'parent': 'Header', 'link': 'LineNR'},
            'Type': {'pattern': r'\[\zs.\{-}\ze[:\]]', 'parent': 'Header', 'link': 'Constant'},
        }

    def gather_candidates(self, context):
        candidates = self.vim.call('luaeval', 'require("denite-utils.lsp").diagnostics()')
        return [{
            'word': '{}:{}:{} {}'.format(relpath(self.vim, x['filename']), x['lnum'], x['col'], x['text']),
            'action__path': x['filename'],
            'action__line': x['lnum'],
            'action__col': x['col'],
        } for x in candidates]
