#!/usr/bin/env python3
# coding: utf-8

from badlinkfinder import __version__ as blf_version
from badlinkfinder.cli import parser, extra_parse_logic
from badlinkfinder.crawler import Crawler


def main():
    args = extra_parse_logic(parser.parse_args())

    try:
        crawler = Crawler(args)
        errors = crawler.run(args.url)
    except KeyboardInterrupt:
        # Catch Interrupt and save progress in case you want to restart it. (TODO)
        sys.exit('\nERROR: Interrupted by user')

    if not errors:
        print('\nNo Issues Found!')
    else:
        # Output file
        if args.output_file:
            print('\nSaving Errors to {}...'.format(args.output_file))
            with open(args.output_file, 'w') as f:
                for error in errors:
                    f.write(str(error) + '\n')
        else:
            print('\nHere are the issues that were found:')
            for error in errors:
                print(error)
