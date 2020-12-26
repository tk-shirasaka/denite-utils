# ============================================================================
# FILE: bookmark.py
# AUTHOR: Takahiro Shirasaka <tk.shirasaka@gmail.com>
# License: MIT license
# ============================================================================

import os
import sys

sys.path.insert(1, os.path.dirname(__file__))

from utils import BaseSource
from denite.kind.directory import Kind as Directory


class Source(BaseSource):
    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'bookmark'
        self.kind = Kind(vim)

    def gather_candidates(self, context):
        return [{
            'word': x.split(':')[0],
            'action__path': x.split(':')[1],
        } for x in self.vim.call('denite_utils#get_bookmark')]


class Kind(Directory):
    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'bookmark'
        self.default_action = 'cd'
        self.persist_actions += ['rename', 'delete']
        self.redraw_actions += ['rename', 'delete']

    def action_rename(self, context):
        target = context['targets'][0]
        alias = self.vim.call('input', 'Alias : ', target['word'])
        bookmark1 = '%s:%s' % (target['word'], target['action__path'])
        bookmark2 = '%s:%s' % (alias, target['action__path'])
        if bookmark1 != bookmark2:
            self.vim.call('denite_utils#set_bookmark', bookmark1, 'delete')
            self.vim.call('denite_utils#set_bookmark', bookmark2, 'add')

    def action_delete(self, context):
        target = context['targets'][0]
        bookmark = '%s:%s' % (target['word'], target['action__path'])
        self.vim.call('denite_utils#set_bookmark', bookmark, 'delete')
