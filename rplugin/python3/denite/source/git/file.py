# ============================================================================
# FILE: git/file.py
# AUTHOR: Takahiro Shirasaka <tk.shirasaka@gmail.com>
# License: MIT license
# ============================================================================

import os
import sys

sys.path.insert(1, os.path.dirname(os.path.dirname(__file__)))

from utils import AsyncSource, AsyncKind
from denite.kind.file import Kind as File


class Source(AsyncSource):
    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'git/file'
        self.kind = Kind(vim)
        self.vars = {'command': ['git', 'ls-files']}

    def build_candidate(self, line, context):
        return {
            'word': line,
            'action__path': os.path.join(context['path'], line)
        }


class Kind(AsyncKind, File):
    def __init__(self, vim):
        super(AsyncKind, self).__init__(vim)
        super(File, self).__init__(vim)

        self.name = 'git/file'
        self.default_action = 'open'
        self.persist_actions += ['rename', 'delete']
        self.redraw_actions += ['rename', 'delete']
        self._previewed_target = {}
        self._previewed_winid = 0

    def action_rename(self, context):
        for target in context['targets']:
            path = self.vim.call('input', 'New file path : ', target['action__path'])
            self.run(['git', 'mv', target['action__path'], path], context)

    def action_delete(self, context):
        self.run(['git', 'rm'] + [target['action__path'] for target in context['targets']], context)
