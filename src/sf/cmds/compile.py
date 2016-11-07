# -*- coding: utf-8 -*-

from argparse import ArgumentParser
from sys import argv, stderr, exit

from colorama import Fore, Style

from sf.solution import autodetect_solution, SourceNotFoundException

from sf.zipgettext import DEFAULT_GETTEXT
_ = DEFAULT_GETTEXT

def main():
    parser = ArgumentParser( prog = 'sf compile' )
    parser.add_argument( '--solution-dir', '-s', help = 'The directory where the solution is to be found.', default = '.' )
    args = parser.parse_args()

    try:
        solution = autodetect_solution(args.solution_dir)
    except SourceNotFoundException:
        stderr.write(Fore.RED + _('No source file found!\n') + Style.RESET_ALL)
        exit(1)

    stderr.write(Fore.BLUE + _('Using {} processor…\n').format(solution.NAME) + Style.RESET_ALL)
    result = solution.compile()
    if result.returncode:
        stderr.write(_('Compilation errors encountered:'))
        print result.stderr,
    else:
        stderr.write(Fore.BLUE + _('Succesfully compiled sources: {}\n').format(', '.join(solution.sources)) + Style.RESET_ALL)
