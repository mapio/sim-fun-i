from collections import defaultdict
from datetime import datetime
from glob import glob
from os import chmod, unlink, symlink
from os.path import join, dirname, basename, isdir, islink
import re
from shutil import copytree, rmtree
from tarfile import TarFile

from logging import basicConfig, getLogger, DEBUG, INFO
LOG_LEVEL = INFO
basicConfig(format = '%(asctime)s %(levelname)s: [%(funcName)s] %(message)s', datefmt = '%Y-%m-%d %H:%M:%S', level = LOG_LEVEL)
LOGGER = getLogger(__name__)

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

class TristoMietitoreUploads(object):
    def __init__(self, path):
        self.path = path
        uid2timestamps = defaultdict(list)
        for tf in glob(join(path, '*', '[0-9]*.tar')):
            m = UID_TIMESTAMP_RE.match(tf)
            if m:
                gd = m.groupdict()
                uid2timestamps[gd['uid']].append(gd['timestamp'])
        self.uid2timestamps = dict(uid2timestamps)

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

tmu = TristoMietitoreUploads('.')
for uid in tmu.uid2timestamps.keys():
    print uid
    print tmu.untar(uid)
