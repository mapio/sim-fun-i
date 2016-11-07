from importlib import import_module
from sys import stderr, argv, exit

from colorama import Fore, Style

from sf.zipgettext import DEFAULT_GETTEXT
_ = DEFAULT_GETTEXT

COMMANDS = 'compile', 'run', 'generate', 'test'

def main():
    try:
        subcommand = argv.pop(1)
    except IndexError:
        stderr.write(Fore.RED + _('Available subcommands: {}\n').format(', '.join(COMMANDS)) + Style.RESET_ALL)
        exit(1)
    import_module( 'sf.cmds.{0}'.format(subcommand)).main()
