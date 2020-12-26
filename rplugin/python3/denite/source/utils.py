# ============================================================================
# FILE: utils.py
# AUTHOR: Takahiro Shirasaka <tk.shirasaka@gmail.com>
# License: MIT license
# ============================================================================

from denite.base.source import Base
from denite.base.kind import Base as Kind
from denite.process import Process


class BaseSource(Base):
    def highlight(self):
        for name, highlight in self.vars.get('highlight', {}).items():
            name = '%s%s' % (self.syntax_name, name)
            parent = '%s%s' % (self.syntax_name, highlight.get('parent', ''))
            if 'link' in highlight:
                self.vim.command('highlight default link %s %s' % (name, highlight['link']))
            self.vim.command('syntax match %s /%s/ contained containedin=%s' % (name, highlight['pattern'], parent))


class AsyncSource(BaseSource):
    def on_init(self, context):
        context['__proc'] = None

    def on_close(self, context):
        if context['__proc']:
            context['__proc'].kill()
            context['__proc'] = None

    def gather_candidates(self, context):
        if not context['__proc']:
            context['__proc'] = Process(self.build_command(context), context, context['path'])

        outs, errs = context['__proc'].communicate(0.5)

        if errs:
            self.error_message(context, errs)

        context['is_async'] = not context['__proc'].eof()

        if context['__proc'].eof():
            context['__proc'] = None

        if not outs:
            return []

        outs = outs if getattr(self, 'duplicatable', None) else list(dict.fromkeys(outs))
        candidates = [self.build_candidate(x, context) for x in outs]
        return [x for x in candidates if x]

    def build_command(self, context):
        return self.vars['command'] + [arg for arg in context['args'] if arg]

    def build_candidate(self, line, context):
        pass


class AsyncKind(Kind):
    def run(self, command, context):
        proc = Process(command, context, context['path'])
        while not proc.eof():
            outs, errs = proc.communicate(1)

            if len(errs):
                self.debug('\n'.join(errs).replace('\t', '    '))

    def terminal(self, command, context):
        self.vim.command('tabedit term://%s//0:%s' % (context['path'], command))
        self.vim.command('startinsert | autocmd BufEnter <buffer> startinsert | autocmd BufLeave <buffer> stopinsert')

    def select(self, prompt, options, default):
        ret = self.vim.call('input', '%s [%s] : ' % (prompt, '/'.join(options)))
        return options[ret] if ret in options else options[default]
