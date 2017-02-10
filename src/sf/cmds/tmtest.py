# -*- coding: utf-8 -*-

from argparse import ArgumentParser, FileType
from sys import argv, stderr, exit

from colorama import Fore, Style

from tm.mkconf import read_uids
from sf.tmdata import TristoMietitoreConfig, TristoMietitoreUploads, tmtest
from sf.scanner import Scanner

def main():
	parser = ArgumentParser(prog = 'sf tmtest')
	parser.add_argument('--config', '-c', help = 'The path of the Tristo Mietitore config file.', required = True)
	parser.add_argument('--uploads', '-u', help = 'The uploads directory.', required = True)
	group = parser.add_mutually_exclusive_group()
	group.add_argument('--uid', '-U', help = 'The UID to test (default: all).')
	group.add_argument('--uids-file', '-F', help = 'The UIDs to test, as a tab-separated file (default: all).')
	parser.add_argument('--timestamp', '-T', help = 'The timestamp of the upload to test (default: latest).')
	parser.add_argument('--no-clean', '-n', default = False, help = 'Whether to clean the untarred upload directory first.', action = 'store_true')
	parser.add_argument('--results', '-r', help = 'The file where to store the json summary of the results', type = FileType( 'wb' ) )
	args = parser.parse_args()

	config = TristoMietitoreConfig(args.config)
	uploads = TristoMietitoreUploads(args.uploads)

	if args.uid:
		uids = [args.uid]
	elif args.uids_file:
		uids = read_uids(args.uids_file).keys()
	else:
		uids = uploads.uids()

	for uid in uids: tmtest(config, uploads, uid, args.timestamp, not args.no_clean)

	if args.results:
		args.results.write(Scanner(args.uploads).scan().sort().tojson(lambda _: _['signature']['uid'] in frozenset(uids)))
		args.results.close()
