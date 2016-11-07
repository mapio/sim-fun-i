# -*- coding: utf-8 -*-

from argparse import ArgumentParser, REMAINDER
from sys import argv, stderr, exit

from colorama import Fore, Style

from sf.solution import autodetect_solution, SourceNotFoundException

from sf.zipgettext import DEFAULT_GETTEXT
_ = DEFAULT_GETTEXT

def main():
    parser = ArgumentParser( prog = 'sf run' )
    parser.add_argument( '--solution-dir', '-s', help = 'The directory where the solution is to be found.', default = '.' )
    parser.add_argument('args', nargs = REMAINDER)
    args = parser.parse_args()

    try:
        solution = autodetect_solution(args.solution_dir)
    except SourceNotFoundException:
        stderr.write(Fore.RED + _('No source file found!\n') + Style.RESET_ALL)
        exit(1)

    result = solution.run(args.args)
    if result.exception:
        stderr.write(Fore.RED + _('Exception raised during execution:\n') + Style.RESET_ALL)
        stderr.write(result.exception)
    elif result.returncode:
        stderr.write(Fore.RED + _('Execution returned non-zero exit code:\n') + Style.RESET_ALL)
        stderr.write(result.stderr)
    else:
        print result.stdout,
