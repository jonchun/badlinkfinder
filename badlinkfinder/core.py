#!/usr/bin/env python3
# coding: utf-8

import logging

from badlinkfinder.cli import parser, extra_parse_logic
from badlinkfinder.crawler import Crawler
from badlinkfinder.engine import Engine

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

def main():
    args = extra_parse_logic(parser.parse_args())

    if args.verbosity == 4:
        logger.setLevel(logging.DEBUG)

    try:
        crawler = Crawler(args)
        engine = Engine(crawler=crawler, url=args.url)

        engine.main()

        errors = engine.get_errors()

        #errors = engine.crawler.run(args.url)

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

if __name__ == "__main__":
    main()