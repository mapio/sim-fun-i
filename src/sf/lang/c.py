from re import compile as recompile

from sf.lang import Lang, execute

class CLang(Lang):
    SOURCES_GLOB = '*.c'
    MAIN_SOURCE_RE = recompile(r'int\s+main')
    def __init__(self, path):
        super(CLang, self).__init__(path)
    def compile(self):
        return execute(['gcc', '-o', 'soluzione'] + self.sources, cwd = self.path)
    def run_command(self):
        return ['./soluzione']
