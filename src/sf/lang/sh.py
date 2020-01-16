from os.path import isfile, join
import re

from sf.solution import Solution, Result, execute

class ShSolution(Solution):
    SOURCES_GLOB = '*.sh'
    MAIN_SOURCE_RE = re.compile(r'.*')
    def __init__(self, path):
        super(ShSolution, self).__init__(path)
        if self.main_source:
            self.run_command = ['sh', self.main_source[0]]
    def compile(self):
        return Result(None, None, None, None)
    def is_compiled(self):
        return True
