from collections import namedtuple
from glob import glob
from os.path import isfile
from re import compile as recompile
from shlex import split
import subprocess
from threading import Timer

Result = namedtuple('Result','returncode,stdout,stderr,exception')

class CompilationException(Exception):
    pass

class ExecutionException(Exception):
    pass

class TimeputException(ExecutionException):
    pass

def execute(cmd, timeout = 0, args_file = None, input_file = None):
    if args_file:
        with open(args_file, 'rU') as f: args = split(f.read())
    else:
        args = []
    if input_file:
        with open(input_file,'rU') as f: input_data = f.read()
    else:
        input_data = None
    try:
        process = subprocess.Popen(cmd + args, stdin = subprocess.PIPE if input_file else None, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
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
            return Result(None, None, None, exception = TimeputException)
        finally:
            timer.cancel()
    else:
        stdout, stderr = process.communicate(input_data)
        return Result(process.returncode, stdout, stderr, None)

TEST_TIMEOUT = 1

class Lang(object):

    INPUT_GLOB = 'input-*.txt'
    ARGS_GLOB = 'args-*.txt'
    OUTPUT_GLOB = 'output-*.txt'
    TEST_NUM_RE = recompile(r'(?:output|input|args)-(.+)\.txt')
    INPUT_FMT = 'input-{}.txt'
    ARGS_FMT = 'args-{}.txt'
    OUTPUT_FMT = 'output-{}.txt'
    ACTUAL_FMT = 'actual-{}.txt'

    def __init__(self, path):
        self.NAME = type(self).__name__
        self.path = path
        self.sources = glob(self.SOURCES_GLOB)
        main_source = []
        for source in self.sources:
            with open(source, 'rU') as f:
                for line in f:
                    if self.MAIN_SOURCE_RE.search(line):
                        main_source.append(source)
        self.main_source = main_source[0] if len(main_source) == 1 else None

    def run(self, args = None):
        return execute(self.run_command() + args)

    def generate(self, dest_path):
        self.compile()
        cases = set()
        for case in glob(self.INPUT_GLOB) + glob(self.ARGS_GLOB):
            cases.add( self.TEST_NUM_RE.match(case).group(1) )
        for case in cases:
            input_file = self.INPUT_FMT.format(case)
            if not isfile(input_file): input_file = None
            args_file = self.ARGS_FMT.format(case)
            if not isfile(args_file): args_file = None
            result = execute(self.run_command(), TEST_TIMEOUT, args_file, input_file)
            if result.exception or result.returncode: raise ExecutionException(result.exception)
            with open(self.OUTPUT_FMT.format(case), 'w') as f: f.write(result.stdout)
        return cases

    def test(self, halt_on_error = True):
        self.compile()
        results = []
        for output_file in glob(self.OUTPUT_GLOB):
            case = self.TEST_NUM_RE.match(output_file).group(1)
            input_file = self.INPUT_FMT.format(case)
            if not isfile(input_file): input_file = None
            args_file = self.ARGS_FMT.format(case)
            if not isfile(args_file): args_file = None
            result = execute(self.run_command(), TEST_TIMEOUT, args_file, input_file)
            results.append(result)
            if result.exception or result.returncode: break
            with open(self.ACTUAL_FMT.format(case), 'w') as f: f.write(result.stdout)
        return results

from sf.lang.java import JavaLang
from sf.lang.c import CLang

def autodetect_language(path):
    for cls in JavaLang, CLang:
        if glob(cls.SOURCES_GLOB): return cls(path)
