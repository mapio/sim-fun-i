from base64 import decodestring
from collections import defaultdict
from datetime import datetime
from fnmatch import fnmatch
from glob import glob
from io import BytesIO
from os import chmod, unlink, symlink
from os.path import join, dirname, basename, isdir, islink
import re
from shutil import copytree, rmtree
from tarfile import TarFile

from logging import basicConfig, getLogger, DEBUG, INFO
LOG_LEVEL = INFO
basicConfig(format = '%(asctime)s %(levelname)s: [%(funcName)s] %(message)s', datefmt = '%Y-%m-%d %H:%M:%S', level = LOG_LEVEL)
LOGGER = getLogger(__name__)

from sf.testcases import TestCase, TestCases

UID_TIMESTAMP_RE = re.compile( r'.*/(?P<uid>.+)/(?P<timestamp>[0-9]+)\.tar' )

def isots(timestamp):
    return datetime.fromtimestamp(int(timestamp)/1000).isoformat()

def rmrotree( path ):
	def _oe(f, p, e):
		if p == path: return
		pp = dirname(p)
		chmod(pp, 0700)
		chmod(p, 0700)
		unlink(p)
	rmtree(path, onerror = _oe)


class TristoMietitoreConfig(object):

    def __init__(self, path):
        config = {}
        with open(path, 'r') as f: exec f in config
        self.tar_data = BytesIO(decodestring(config['TAR_DATA']))

    def cases(self, exercise):
        self.tar_data.seek(0)
        result = {}
        with TarFile.open(mode = 'r', fileobj = self.tar_data ) as tf:
            for m in tf.getmembers():
                if m.isfile():
                    for kind in TestCase.KINDS:
                        if fnmatch(m.name, join(exercise, TestCase.GLOBS[kind])):
                            name = TestCase.TEST_NUM_RE.match(basename(m.name)).group(1)
                            data = tf.extractfile(m).read().decode('utf-8')
                            tc = result.get(name, TestCase(name))
                            if kind == 'args': data = TestCase.u2args(data)
                            setattr(tc, kind, data)
                            result[name] = tc
        return TestCases(result)


class TristoMietitoreUploads(object):

    def __init__(self, path):
        if not isdir(path): raise IOError('{} is not a directory'.format(path))
        self.path = path
        uid2timestamps = defaultdict(list)
        for tf in glob(join(path, '*', '[0-9]*.tar')):
            m = UID_TIMESTAMP_RE.match(tf)
            if m:
                gd = m.groupdict()
                uid2timestamps[gd['uid']].append(gd['timestamp'])
        self.uid2timestamps = dict(uid2timestamps)

    def uids(self):
        return self.uid2timestamps.keys()

    def untar(self, uid, timestamp = None, clean = True):
        if timestamp is None: timestamp = max(self.uid2timestamps[uid])
        dest_dir = join(self.path, uid, timestamp)
    	if not clean and isdir(dest_dir):
            LOGGER.info( 'Upload for uid {} skipped ({} already exists, corresponding to time {})'.format(uid, dest_dir, isots(timestamp)))
        else:
            rmrotree(dest_dir)
            with TarFile.open(join(self.path, uid, timestamp + '.tar'), mode = 'r') as tf: tf.extractall(dest_dir)
    	    LOGGER.info( 'Upload for uid {} untarred (in {}, corresponding to time {})'.format(uid, dest_dir, isots(timestamp)))
        latest = join(self.path, uid, 'latest')
    	if islink(latest): unlink(latest)
    	symlink(timestamp, latest)
        return map(basename, filter(isdir, glob(join(dest_dir, '*'))))

def tmtest(config, uploads, uid, timestamp = None, clean = True):
    exercises = uploads.untar(uid, timestamp, clean)
    for exercise in exercises:
        print exercise
