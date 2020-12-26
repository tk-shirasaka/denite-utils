# ============================================================================
# FILE: git/stash.py
# AUTHOR: Takahiro Shirasaka <tk.shirasaka@gmail.com>
# License: MIT license
# ============================================================================

import os
import sys
import re

sys.path.insert(1, os.path.dirname(os.path.dirname(__file__)))

from utils import AsyncSource, AsyncKind
from denite.kind.file import Kind as File


class Source(AsyncSource):
    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'git/stash'
        self.kind = Kind(vim)
        self.vars['command'] = ['git', 'stash', 'list']

    def build_candidate(self, line, context):
        line = line.replace('\t', '  ')
        index = line.find(':')
        return {
            'word': line[index + 1:],
            'action__rev': line[:index],
        }


class Kind(AsyncKind):
    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'git/stash'
        self.default_action = 'pop'
        self.persist_actions += ['delete']
        self.redraw_actions += ['delete']

    def action_pop(self, context):
        self.run(['git', 'stash', 'pop'] + [target['action__rev'] for target in context['targets']], context)
        context['sources_queue'].append([{'name': 'git/status', 'args': []}])

    def action_delete(self, context):
        self.run(['git', 'stash', 'drop'] + [target['action__rev'] for target in context['targets']], context)

    def action_diff(self, context):
        self.terminal('git difftool %s' % context['targets'][0]['action__rev'], context)
