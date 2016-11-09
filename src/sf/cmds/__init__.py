from importlib import import_module
from os import environ
import sys
from traceback import format_exception_only

from colorama import Fore, Style

from sf.zipgettext import DEFAULT_GETTEXT
_ = DEFAULT_GETTEXT

COMMANDS = 'compile', 'run', 'generate', 'test'

def main():
    if 'SF_DEBUG' not in environ:
        sys.excepthook = lambda t, v, tb: sys.exit(Fore.RED + _('The following error occurred: ') + Style.RESET_ALL + format_exception_only(t, v)[0])
    try:
        subcommand = sys.argv.pop(1)
    except IndexError:
        sys.stderr.write(Fore.RED + _('Available subcommands: {}\n').format(', '.join(COMMANDS)) + Style.RESET_ALL)
        sys.exit(1)
    import_module( 'sf.cmds.{0}'.format(subcommand)).main()
