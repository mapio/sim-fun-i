# -*- coding: utf-8 -*-

from argparse import ArgumentParser, REMAINDER
from sys import argv, stderr, exit

from colorama import Fore, Style

from sf.cmds.compile import detect_and_compile
from sf.solution import autodetect_solution

from sf.zipgettext import DEFAULT_GETTEXT
_ = DEFAULT_GETTEXT

def main():
    parser = ArgumentParser( prog = 'sf run' )
    parser.add_argument('--solution-dir', '-s', help = 'The directory where the solution is to be found.', default = '.')
    parser.add_argument('--force-compile', '-f', help = 'Whether to force a compilation before running the solution.', default = False, action = 'store_true')
    parser.add_argument('--quiet', '-q', help = 'Whether to be more silent.', default = False, action = 'store_true')
    parser.add_argument('args', nargs = REMAINDER)
    args = parser.parse_args()

    solution = detect_and_compile(args.solution_dir, args.force_compile, args.quiet)

    result = solution.run(args.args)
    if result.exception:
        stderr.write(Fore.RED + _('Exception raised during execution:\n') + Style.RESET_ALL)
        stderr.write(result.exception)
        exit(1)
    if result.returncode:
        stderr.write(Fore.RED + _('Execution returned non-zero exit code:\n') + Style.RESET_ALL)
        stderr.write(result.stderr)
        exit(result.returncode)

    print result.stdout,
