# -*- coding: utf-8 -*-

from argparse import ArgumentParser
from sys import argv, stderr, exit

from colorama import Fore, Style

from sf.solution import autodetect_solution, SourceNotFoundException
from sf.testcases import TestCases

from sf.zipgettext import DEFAULT_GETTEXT
_ = DEFAULT_GETTEXT

def main():
    parser = ArgumentParser( prog = 'sf test' )
    parser.add_argument( '--solution-dir', '-s', help = 'The directory where the solution is to be found.', default = '.' )
    parser.add_argument( '--cases-dir', '-c', help = 'The directory where the test cases are to be found.' )
    parser.add_argument( '--actual-dir', '-o', help = 'The direcotry where to write the generated actual files.', default = '.' )
    parser.add_argument( '--overwrite', '-O', help = 'Whether to overwrite the actual files, if present.', default = False )
    args = parser.parse_args()
    if args.cases_dir is None: args.cases_dir = args.solution_dir

    try:
        solution = autodetect_solution(args.solution_dir)
    except SourceNotFoundException:
        stderr.write(Fore.RED + _('No source file found!\n') + Style.RESET_ALL)
        exit(1)

    cases = TestCases(args.cases_dir)
    stderr.write(Fore.BLUE + _('Using {} processor…\n').format(solution.NAME) + Style.RESET_ALL)
    cases.fill(solution, 'actual')
    cases.write(args.actual_dir, args.overwrite)
    stderr.write(Fore.BLUE + _('Generated actual for cases: {}\n').format(', '.join(sorted(cases.keys()))) + Style.RESET_ALL)
