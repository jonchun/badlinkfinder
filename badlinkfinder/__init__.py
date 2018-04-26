"""
BadLinkFinder - a recursive bot that scrapes a domain and finds all bad assets/links.
"""

#!/usr/bin/env python3
# coding: utf-8

__version__ = '1.0.0-release'
__author__ = 'Jonathan Chun'

def main(argv=None):
    try:
        from .core import main
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit('\nERROR: Interrupted by user')
