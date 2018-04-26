#!/usr/bin/env python3
# coding: utf-8

import argparse

from badlinkfinder import __doc__

parser = argparse.ArgumentParser(
    prog='badlinkfinder',
    description='{}'.format(__doc__.strip()),
)
parser.add_argument("url")
parser.add_argument("--threads", type=int, default=5)
parser.add_argument("--output_file")
parser.add_argument("--verbose",
                    help="increase output verbosity",
                    action="store_true")
