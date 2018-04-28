#!/usr/bin/env python3
# coding: utf-8

from badlinkfinder import __version__ as blf_version
from badlinkfinder.cli import parser, extra_parse_logic
from badlinkfinder.crawler import Crawler


def main():
    args = extra_parse_logic(parser.parse_args())

    crawler = Crawler(args)
    errors = crawler.run(args.url)

    if not errors:
        print('\nNo Issues Found!')
    else:
        print('\nHere are the issues that were found:')
        for error in errors:
            print(error)
