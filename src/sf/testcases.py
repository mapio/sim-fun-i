from collections import Mapping
from itertools import chain
from glob import glob
from pipes import quote
from shlex import split
import codecs
from os.path import join, isfile, basename
import re

from sf.solution import ExecutionException

DEFAULT_ENCODING = 'utf-8'

def _encode(u):
    if u is None: return u''
    return u.encode(DEFAULT_ENCODING)

def _decode(s):
    return s.decode(DEFAULT_ENCODING)

class TestCase(object):

    KINDS = 'args input output actual errors diffs'.split()
    FORMATS = dict((kind, '{}-{{}}.txt'.format(kind)) for kind in KINDS)
    GLOBS = dict((kind, '{}-*.txt'.format(kind)) for kind in KINDS)
    TEST_NUM_RE = re.compile(r'(?:{})-(.+)\.txt'.format('|'.join(KINDS)))

    def _read(self, kind):
        path = join(self.path, self.FORMATS[kind].format(self.name))
        if isfile(path):
            with codecs.open(path, 'rU', DEFAULT_ENCODING) as f: data = f.read()
            if kind == 'args': data = map(_decode, split(_encode(data), posix=True))
        else:
            data = None
        setattr(self, kind, data)

    def __init__(self, path, name):
        self.path = path
        self.name = name
        for kind in TestCase.KINDS: self._read(kind)

    def fill(self, solution, kind):
        result = solution.run(self.args, self.input)
        if result.exception:
            raise ExecutionException(result.exception)
        if result.returncode:
            raise ExecutionException(result.stderr)
        setattr(self, kind, result.stdout)

    def _write(self, kind, path, overwrite):
        data = getattr(self, kind)
        if data is None: return None
        if kind == 'args': data = _decode(' '.join(map(quote, map(_encode, self.args))) + '\n')
        path = join(path,self.FORMATS[kind].format(self.name))
        if overwrite or not isfile(path):
            with codecs.open(path, 'w', DEFAULT_ENCODING) as f: f.write(data)
        return basename(path)

    def write(self, path, overwrite = False):
        return filter(None, (self._write(kind, path, overwrite) for kind in TestCase.KINDS))

    def __str__(self):
        args = ', '.join(map(_encode, self.args)) if self.args else ''
        return 'Path: {}\n\nName: {}\n\nInput:\n{}\nArgs: {}\n\nOutput:\n{}\nActual:\n{}\n'.format(self.path, self.name, _encode(self.input), args, _encode(self.output), _encode(self.actual))

class TestCases(Mapping):

    def __init__(self, path = '.'):
        cases_paths = chain(*map(glob, (join(path, TestCase.GLOBS[kind]) for kind in TestCase.KINDS)))
        names = set()
        for case_path in cases_paths:
            names.add(TestCase.TEST_NUM_RE.match(basename(case_path)).group(1))
        self.cases = dict((name, TestCase(path,name)) for name in names)

    def __getitem__(self, key):
        return self.cases[key]

    def __len__(self):
        return len(self.cases)

    def __iter__(self):
        return iter(self.cases)

    def fill(self, solution, what):
        for case in self.cases.values():
            case.fill(solution, what)

    def write(self, path, overwrite = False):
        written = []
        for case in self.cases.values():
            written.extend(case.write(path, overwrite))
        return written
