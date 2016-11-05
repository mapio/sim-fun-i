from importlib import import_module
from sys import argv
from os.path import dirname

if __name__ == '__main__':
    try:
        import_module( 'sf.{0}'.format( argv.pop( 1 ) ) ).main()
    except ( IndexError, ImportError ):
        print 'usage: sf {compile,run,test} ...'
    except:
        raise
