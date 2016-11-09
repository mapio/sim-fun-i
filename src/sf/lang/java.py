from os.path import isfile, join
from re import compile as recompile

from sf.solution import Solution, execute

class JavaSolution(Solution):
    SOURCES_GLOB = '*.java'
    OTHERS_GLOB = None
    MAIN_SOURCE_RE = recompile(r'public\s+static\s+void\s+main')
    def __init__(self, path):
        super(JavaSolution, self).__init__(path)
        self.main_class = self.main_source.split('.')[0] if self.main_source else None
        self.run_command = ['java', '-Duser.language=ROOT', self.main_class]
    def compile(self):
        return execute(['javac'], args = self.sources, cwd = self.path)
    def is_compiled(self):
        return isfile(join(self.path, self.main_class + '.class'))
