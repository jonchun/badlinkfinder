#!/usr/bin/env python3
# coding: utf-8

from argparse import (
    ArgumentParser, RawDescriptionHelpFormatter
    OPTIONAL, ZERO_OR_MORE, SUPPRESS
)

from textwrap import dedent, wrap

from badlinkfinder import __doc__, __version__
from badlinkfinder.logger import E

class CustomHelpFormatter(RawDescriptionHelpFormatter):
    """A nicer help formatter.
    Help for arguments can be indented and contain new lines.
    It will be de-dented and arguments in the help
    will be separated by a blank line for better readability.

    Taken from https://github.com/jakubroztocil/httpie/
    """
    def __init__(self, max_help_position=6, *args, **kwargs):
        # A smaller indent for args help.
        kwargs['max_help_position'] = max_help_position
        super(CustomHelpFormatter, self).__init__(*args, **kwargs)

    def _split_lines(self, text, width):
        text = dedent(text).strip() + '\n\n'
        return text.splitlines()

parser = ArgumentParser(
    prog='blf',
    formatter_class=CustomHelpFormatter,
    description='{}'.format(__doc__.strip()),
    add_help=False
)

#######################################################################
# Positional arguments.
#######################################################################

positional = parser.add_argument_group(
    title='Positional Arguments',
    description=dedent("""These arguments come after any flags and in the order they are listed here.
    Only URL is required.
    """)
)

positional.add_argument(
    'url',
    metavar='URL',
    default=None,
    help="""
    The starting seed URL to begin crawling your website. This is required to begin searching for bad links.
    """
)

#######################################################################
# Crawler Settings.
#######################################################################

crawler_settings = parser.add_argument_group(
    title='Crawler Settings',
    description=None
)

crawler_settings.add_argument(
    '--threads',
    type=int,
    default=5,
    help="""
    By default, 5 threads are used for the crawler.
    """
)

crawler_settings.add_argument(
    '--timeout',
    type=int,
    default=10,
    help="""
    By default, requests time out after 10 seconds.
    """
)

crawler_settings.add_argument(
    '--include_inbound',
    action='store_true',
    help="""
    Whether to include inbound URLs when reporting Site Errors (show where they were referenced from)
    """
)

#######################################################################
# Parser Settings.
#######################################################################

parser_settings = parser.add_argument_group(
    title='Parser Settings',
    description=None
)

parser_settings.add_argument(
    '--ignore_prefix',
    action='append',
    dest='ignore_prefixes',
    help="""
    Ignore prefix when parsing URLs so that it does not detect as invalid.
        --ignore-prefix custom
    will ignore any URL that looks like "custom:nonstandardurlhere.com"
    (You can declare this option multiple times)
    """
)

#######################################################################
# Troubleshooting
#######################################################################

troubleshooting = parser.add_argument_group(title='Troubleshooting')

troubleshooting.add_argument(
    '--help',
    action='help',
    default=SUPPRESS,
    help="""
    Show this help message and exit.
    """
)

troubleshooting.add_argument(
    '--version',
    action='version',
    version=__version__,
    help="""
    Show version and exit.
    """
)

verbosity_help = '\nThe verbosity level:\n'
for _enum in E:
    verbosity_help += '  {}: {}\n'.format(_enum.value, _enum.name)

troubleshooting.add_argument(
    '--verbosity',
    default=1,
    help=verbosity_help
)

def extra_parse_logic(args):
    # Convert verbosity to value from ENUM
    try:
        verbosity = int(args.verbosity)
    except ValueError:
        try:
            verbosity = E[args.verbosity].value
        except KeyError:
            verbosity_help = '\nThe verbosity level:\n'
            for _enum in E:
                verbosity_help += '  {}: {}\n'.format(_enum.value, _enum.name)
            
            raise BLFInvalidArgument('Verbosity value is invalid. Please use one of the following values:' + verbosity_help)
    args.verbosity = verbosity

    return args

class BLFInvalidArgument(Exception):
    pass