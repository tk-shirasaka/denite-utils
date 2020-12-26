# ============================================================================
# FILE: docker/image.py
# AUTHOR: Takahiro Shirasaka <tk.shirasaka@gmail.com>
# License: MIT license
# ============================================================================

import os
import sys

sys.path.insert(1, os.path.dirname(os.path.dirname(__file__)))

from utils import AsyncSource, AsyncKind


class Source(AsyncSource):
    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'docker/image'
        self.kind = Kind(vim)
        self.vars = {'command': ['docker', 'image', 'ls', '--format', '{{.ID}} {{.Repository}}:{{.Tag}}']}
        self.vars['highlight'] = {
            'ID': {'pattern': r'.\{-}\s', 'link': 'Title'},
            'Tag': {'pattern': r':\zs.*', 'link': 'Type'},
        }

    def build_candidate(self, line, context):
        line = line.strip('\'')
        id, image = line.split(' ')
        return {
            'word': line,
            'action__id': id,
            'action__image': image,
        }


class Kind(AsyncKind):
    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'docker/image'
        self.default_action = 'run'
        self.persist_actions += ['pull', 'delete']
        self.redraw_actions += ['pull', 'delete']

    def action_run(self, context):
        for target in context['targets']:
            command = self.vim.call('input', ':docker container run ', '--rm -ti %s ' % target['action__image'])
            self.terminal('docker container run %s' % command, context)

    def action_pull(self, context):
        for target in context['targets']:
            self.run(['docker', 'image', 'pull', target['action__image']], context)

    def action_delete(self, context):
        ids = [target['action__id'] for target in context['targets']]
        args = ['docker', 'image', 'rm']
        args += ['-f'] if self.select('Force delete?', {'n': False, 'y': True}, 'n') else []
        self.run(args + ids, context)
