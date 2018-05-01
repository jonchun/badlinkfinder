#!/usr/bin/env python3
# coding: utf-8

import logging
import sys

from badlinkfinder.cli.input import extra_parse_logic, parser, BLFInvalidArgument
from badlinkfinder.crawler import Crawler
import  badlinkfinder.cli.output as blf_output

logger = logging.getLogger('blf')

def main():
    try:
        args = extra_parse_logic(parser.parse_args())
        blf_output.configure(args)

        crawler = Crawler(
                workers=args.workers,
                timeout=args.timeout,
                ignore_schemes=args.ignore_schemes or [],
                ignore_domains=args.ignore_domains or [],
            )

        blf_output.display(crawler, crawler.run(args.url))
    except BLFInvalidArgument as e:
        raise e
    except KeyboardInterrupt:
        # Catch Interrupt and save progress in case you want to restart it. (TODO)
        raise Exception('ERROR: Interrupted by user')
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise e
