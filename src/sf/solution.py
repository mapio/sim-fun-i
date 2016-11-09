from collections import namedtuple
from glob import glob
import io
from os.path import isfile, basename, join
import re
from shlex import split
import subprocess
from threading import Timer

Result = namedtuple('Result','returncode,stdout,stderr,exception')

class ExecutionException(Exception):
    pass

class NotCompiledException(ExecutionException):
    pass

class TimeoutException(ExecutionException):
    pass

from sf.testcases import DEFAULT_ENCODING # don't move, circular imports ahead

def execute(cmd, args = None, input_data = None, timeout = 0, cwd = None):
    if args is None: args = []
    try:
        process = subprocess.Popen(cmd + args, stdin = subprocess.PIPE if input_data else None, stdout = subprocess.PIPE, stderr = subprocess.PIPE, cwd = cwd)
    except OSError, e:
        return Result(None, None, None, exception = e)
    if timeout:
        timer = Timer(timeout, process.kill)
        try:
            timer.start()
            stdout, stderr = process.communicate(input_data)
            if timer.is_alive():
                timer.cancel()
                return Result(process.returncode, stdout, stderr, None)
            return Result(None, None, None, exception = TimeoutException('{}s timeout exceeded'.format(timeout)))
        finally:
            timer.cancel()
    else:
        stdout, stderr = process.communicate(input_data)
        return Result(process.returncode, stdout, stderr, None)

TEST_TIMEOUT = 1

class Solution(object):

    def __init__(self, path):
        self.NAME = type(self).__name__
        self.path = path
        self.sources = map(basename, glob(join(path,self.SOURCES_GLOB)))
        self.file_contents = dict()
        all_files = self.sources
        if self.OTHERS_GLOB: self.sources += map(basename, glob(join(path,self.OTHERS_GLOB)))
        for name in all_files:
            with io.open(join(path,name), 'rU') as f: self.file_contents[name] = f.read()
        main_source = []
        for name, content in self.file_contents.items():
            if self.MAIN_SOURCE_RE.search(content, re.MULTILINE):
                main_source.append(name)
        self.main_source = main_source[0] if len(main_source) == 1 else None

    def run(self, args = None, input_data = None, timeout = 0):
        if not self.is_compiled(): raise NotCompiledException('Cannot find the compiled solution')
        return execute(self.run_command, args, input_data, timeout = timeout, cwd = self.path)

    def __str__(self):
        return 'Lang: {}, Path: {}, Sources: {}'.format(self.NAME, self.path, ' ,'.join(self.sources))

from sf.lang import JavaSolution, CSolution, ShSolution

def autodetect_solution(path = '.'):
    for cls in JavaSolution, CSolution, ShSolution:
        if glob(join(path,cls.SOURCES_GLOB)): return cls(path)
    return None
