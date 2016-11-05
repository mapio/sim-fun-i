import subprocess
from threading import Timer
from collections import namedtuple

Result = namedtuple('Result','returncode,stdout,stderr,exception')
TIMEOUT = 'TIMEOUT'

def run( cmd, timeout ):
    try:
        process = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    except OSError, e:
        return Result(None, None, None, exception = e)
    timer = Timer(timeout, process.kill)
    try:
        timer.start()
        stdout, stderr = process.communicate()
        if timer.is_alive():
            timer.cancel()
            return Result(process.returncode, stdout, stderr, None)
        return Result(None, None, None, exception = TIMEOUT)
    finally:
        timer.cancel()
