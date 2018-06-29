import io
from os.path import isfile, join
import re

from sf import DEFAULT_ENCODING, WronglyEncodedFile
from sf.solution import Solution, execute

class JavaSolution(Solution):
    SOURCES_GLOB = '*.java'
    MAIN_SOURCE_RE = re.compile(r'public\s+static\s+void\s+main', re.MULTILINE)
    MAIN_PUBLIC_CLASS_RE = re.compile(r'public\s+class\s+(\w+)', re.MULTILINE)
    MAIN_CLASS_RE = re.compile(r'class\s+(\w+)', re.MULTILINE)
    def __init__(self, path):
        super(JavaSolution, self).__init__(path)
        if self.main_source:
            match = JavaSolution.MAIN_PUBLIC_CLASS_RE.search(self.main_source[1])
            if match:
                self.main_class = match.group(1)
            else:
                match = JavaSolution.MAIN_CLASS_RE.search(self.main_source[1])
                if match:
                    self.main_class = match.group(1)
                else:
                    self.main_class, self.main_source = None, None
            if self.main_class == 'TestRunner':
                self.main_class, self.main_source = None, None
            else:
                self.run_command = ['java', '-Duser.language=ROOT', self.main_class]
    def compile(self):
        return execute(['javac'], args = self.sources, cwd = self.path)
    def is_compiled(self):
        return isfile(join(self.path, self.main_class + '.class'))

class JavaTestRunnerSolution(JavaSolution):
    def __init__(self, path):
        super(JavaTestRunnerSolution, self).__init__(path)
        if len(self.sources) < 2:
            self.sources, self.main_class, self.main_source = None, None, None
        else:
            for name in self.sources:
                if name == 'TestRunner.java':
                    try:
                        with io.open(join(path, name), 'r', encoding = DEFAULT_ENCODING, errors = 'replace') as f: content = f.read()
                    except UnicodeDecodeError:
                        raise WronglyEncodedFile(join(path, name))
                    self.main_source = (name, content)
                    break
            else:
                self.main_class, self.main_source = None, None
        if self.main_source:
            self.main_class = 'TestRunner'
            self.run_command = ['java', '-Duser.language=ROOT', self.main_class]
