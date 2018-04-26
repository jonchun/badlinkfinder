#!/usr/bin/env python3
# coding: utf-8

import sys

def main(argv=None):
    try:
        from .core import main
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit('\nERROR: Interrupted by user')

if __name__ == '__main__':
    main()
