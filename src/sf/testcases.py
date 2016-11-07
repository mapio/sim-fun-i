from itertools import chain
from glob import glob
from pipes import quote
from shlex import split
import codecs
from os.path import join, isfile, basename
import re

DEFAULT_ENCODING = 'utf-8'

def _encode(u):
    if u is None: return u''
    return u.encode(DEFAULT_ENCODING)

def _decode(s):
    return s.decode(DEFAULT_ENCODING)

class TestCase(object):

    INPUT_FMT = 'input-{}.txt'
    ARGS_FMT = 'args-{}.txt'
    OUTPUT_FMT = 'output-{}.txt'
    ACTUAL_FMT = 'actual-{}.txt'
    INPUT_GLOB = 'input-*.txt'
    ARGS_GLOB = 'args-*.txt'
    OUTPUT_GLOB = 'output-*.txt'
    ACTUAL_GLOB = 'output-*.txt'
    TEST_NUM_RE = re.compile(r'(?:output|input|args)-(.+)\.txt')

    def __init__(self, path, name):
        self.path = path
        self.name = name
        input_file = join(path,self.INPUT_FMT.format(name))
        if isfile(input_file):
            with codecs.open(input_file, 'rU', DEFAULT_ENCODING) as f: self.input = f.read()
        else:
            self.input = None
        args_file = join(path,self.ARGS_FMT.format(name))
        if isfile(args_file):
            with codecs.open(args_file, 'rU', DEFAULT_ENCODING) as f: args = f.read()
            self.args = map(_decode, split(_encode(args), posix=True))
        else:
            self.args = None
        output_file = join(path,self.OUTPUT_FMT.format(name))
        if isfile(output_file):
            with codecs.open(output_file, 'rU', DEFAULT_ENCODING) as f: self.output = f.read()
        else:
            self.output = None
        actual_file = join(path,self.ACTUAL_FMT.format(name))
        if isfile(actual_file):
            with codecs.open(actual_file, 'rU', DEFAULT_ENCODING) as f: self.actual = f.read()
        else:
            self.actual = None

    def write(self, path, overwrite = False):
        if self.input is not None:
            input_file = join(path,self.INPUT_FMT.format(self.name))
            if overwrite or not isfile(input_file):
                with codecs.open(input_file, 'w', DEFAULT_ENCODING) as f: f.write(self.input)
        if self.args is not None:
            args_file = join(path,self.ARGS_FMT.format(self.name))
            if overwrite or not isfile(args_file):
                args = _decode(' '.join(map(quote,map(_encode,self.args))) + '\n')
                with codecs.open(args_file, 'w', DEFAULT_ENCODING) as f: args = f.write(args)
        if self.output is not None:
            output_file = join(path,self.OUTPUT_FMT.format(self.name))
            if overwrite or not isfile(output_file):
                with codecs.open(output_file, 'w', DEFAULT_ENCODING) as f: f.write(self.output)
        if self.actual is not None:
            actual_file = join(path,self.ACTUAL_FMT.format(self.name))
            if overwrite or not isfile(actual_file):
                with codecs.open(actual_file, 'w', DEFAULT_ENCODING) as f: f.write(self.actual)

    def __str__(self):
        args = ', '.join(map(_encode, self.args)) if self.args else ''
        return 'Path: {}\n\nName: {}\n\nInput:\n{}\nArgs: {}\n\nOutput:\n{}\nActual:\n{}\n'.format(self.path, self.name, _encode(self.input), args, _encode(self.output), _encode(self.actual))

class TestCases(object):

    def __init__(self, path):
        cases_paths =  chain(*map(glob,
            (join(path,TestCase.INPUT_GLOB), join(path,TestCase.ARGS_GLOB), join(path,TestCase.OUTPUT_GLOB), join(path,TestCase.ACTUAL_GLOB))
        ))
        names = set()
        for case_path in cases_paths:
            names.add(TestCase.TEST_NUM_RE.match(basename(case_path)).group(1))
        self.cases = dict((name, TestCase(path,name)) for name in names)

    def write(self, path, overwrite = False):
        for case in self.cases.values():
            case.write(path, overwrite)

    def __iter__(self):
        return iter(self.cases.items())

if __name__ == '__main__':
    tc = TestCases('.')
    tc.write('/tmp/out', True)
