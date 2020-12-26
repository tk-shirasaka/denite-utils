# ============================================================================
# FILE: docker/container.py
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

        self.name = 'docker/container'
        self.kind = Kind(vim)
        self.vars = {'command': ['docker', 'container', 'ls', '-a', '--format', '{{.ID}} {{.Names}}:{{.Image}} - {{.Status}}']}
        self.vars['highlight'] = {
            'ID': {'pattern': r'\<[0-9a-f]\{12\}\>', 'link': 'Title'},
            'Container': {'pattern': r'\s\zs.\{-}\:.\{-}\ze\s', 'link': 'Constant'},
            'Status': {'pattern': r'\s-\s\zs.*', 'link': 'Keyword'},
        }

    def build_candidate(self, line, context):
        line = line.strip('\'')
        return {
            'word': line,
            'action__id': line.split(' ')[0],
        }


class Kind(AsyncKind):
    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'docker/container'
        self.default_action = 'exec'
        self.persist_actions += ['start', 'stop', 'restart', 'delete']
        self.redraw_actions += ['start', 'stop', 'restart', 'delete']

    def action_exec(self, context):
        for target in context['targets']:
            command = self.vim.call('input', 'command: ')
            self.terminal('docker container exec -ti %s %s' % (target['action__id'], command), context)

    def action_log(self, context):
        ids = [target['action__id'] for target in context['targets']]
        self.terminal('docker container logs -f %s' % ' '.join(ids), context)

    def action_start(self, context):
        ids = [target['action__id'] for target in context['targets']]
        self.run(['docker', 'container', 'start'] + ids, context)

    def action_stop(self, context):
        ids = [target['action__id'] for target in context['targets']]
        self.run(['docker', 'container', 'stop'] + ids, context)

    def action_restart(self, context):
        ids = [target['action__id'] for target in context['targets']]
        self.run(['docker', 'container', 'restart'] + ids, context)

    def action_delete(self, context):
        ids = [target['action__id'] for target in context['targets']]
        self.run(['docker', 'container', 'rm'] + ids, context)
