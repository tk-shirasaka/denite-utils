# ============================================================================
# FILE: lsp.py
# AUTHOR: Takahiro Shirasaka <tk.shirasaka@gmail.com>
# License: MIT license
# ============================================================================

import os
import sys

sys.path.insert(1, os.path.dirname(__file__))

from utils import BaseSource
from denite.base.kind import Base


class Source(BaseSource):
    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'lsp'
        self.kind = Kind(vim)

    def gather_candidates(self, context):
        return [
            {'word': 'declaration'},
            {'word': 'definition'},
            {'word': 'formatting'},
            {'word': 'hover'},
            {'word': 'implementation'},
            {'word': 'signature_help'},
            {'word': 'type_definition'},
            {'word': 'references'},
            {'word': 'document_symbol'},
            {'word': 'workspace_symbol'},
            {'word': 'rename'},
        ]


class Kind(Base):
    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'lsp'
        self.default_action = 'execute'

    def action_execute(self, context):
        target = context['targets'][0]
        command = 'lua vim.lsp.buf.%s()' % target['word']
        self.vim.command(command)
