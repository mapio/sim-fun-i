from pathlib import Path
import re

from sf import deread
from sf.solution import Solution, execute

def guessClass(src):
    MAIN_PUBLIC_CLASS_RE = re.compile(r'public\s+class\s+(\w+)', re.MULTILINE)
    MAIN_CLASS_RE = re.compile(r'class\s+(\w+)', re.MULTILINE)
    match = MAIN_PUBLIC_CLASS_RE.search(src)
    if match: return match.group(1)
    match = MAIN_CLASS_RE.search(src)
    if match: return match.group(1)
    return None

class JavaSolution(Solution):
    SOURCES_GLOB = '*.java'
    MAIN_SOURCE_RE = re.compile(r'public\s+static\s+void\s+main', re.MULTILINE)
    def __init__(self, path):
        super(JavaSolution, self).__init__(path)
        if self.main_source:
            main_class = guessClass(self.main_source[1])
            if main_class != 'TestRunner':
                self.run_command = ['java', '-Duser.language=ROOT', main_class]
            else:
                self.main_source = None
    def compile(self):
        return execute(['javac', '-d', '.'], args = self.sources, cwd = self.path)
    def is_compiled(self):
        return all((Path(self.path) / _).with_suffix('.class').is_file() for _ in self.sources)

class JavaTestRunnerSolution(JavaSolution):
    def __init__(self, path):
        super(JavaTestRunnerSolution, self).__init__(path)
        self.run_command = None
        if self.sources and len(self.sources) >= 2:
            for name in self.sources:
                if name == 'TestRunner.java':
                    self.main_source = (name, deread(str(Path(path)/ name)))
                    self.run_command = ['java', '-Duser.language=ROOT', 'TestRunner']
                    break
        if self.run_command is None:
            self.sources, self.main_source = None, None
