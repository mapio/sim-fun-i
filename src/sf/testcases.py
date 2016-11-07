import codecs
from collections import Mapping
from difflib import context_diff, IS_CHARACTER_JUNK
from itertools import chain
from glob import glob
from os.path import join, isfile, basename
from pipes import quote
import re
from shlex import split
from textwrap import dedent

from sf.solution import ExecutionException

DEFAULT_ENCODING = 'utf-8'
TEST_TIMEOUT = 1

def _encode(u):
    if u is None: return u''
    return u.encode(DEFAULT_ENCODING)

def _decode(s):
    return s.decode(DEFAULT_ENCODING)

def _normalized_lines(u):
    if not u.endswith('\n'): u += '\n'
    return list(map(lambda _: _.rstrip() + '\n', dedent(u).splitlines(True)))

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

    def _fill(self, solution, kind, timeout = 0):
        result = solution.run(self.args, self.input, timeout)
        if result.exception:
            raise result.exception
        if result.returncode:
            raise ExecutionException(result.stderr)
        setattr(self, kind, result.stdout)

    def fill_output(self, solution):
        self.output = None
        self._fill(solution, 'output')

    def fill_actual(self, solution):
        try:
            self._fill(solution, 'actual', TEST_TIMEOUT)
        except ExecutionException, e:
            self.actual = None
            self.errors = '[{}] {}\n'.format(type(e).__name__, str(e).rstrip())
        else:
            self.diffs = ''.join(context_diff(
                _normalized_lines(self.output), _normalized_lines(self.actual),
                TestCase.FORMATS['output'].format(self.name), TestCase.FORMATS['actual'].format(self.name)
            ))

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
        parts = ['Path: ' + self.path, 'Name: ' + self.name]
        if self.args is not None:
            parts.append('Args: ' + ', '.join(map(_encode, self.args)))
        parts.extend('{}:\n{}'.format(kind.capitalize(), _encode(getattr(self, kind)).rstrip()) for kind in TestCase.KINDS[1:] if getattr(self,kind) is not None)
        return '\n'.join(parts)

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

    def fill_actual(self, solution):
        for case in self.cases.values():
            case.fill_actual(solution)

    def fill_output(self, solution):
        for case in self.cases.values():
            case.fill_output(solution)

    def write(self, path, overwrite = False):
        written = []
        for case in self.cases.values():
            written.extend(case.write(path, overwrite))
        return written
