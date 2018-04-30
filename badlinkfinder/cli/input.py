from argparse import ArgumentParser, RawDescriptionHelpFormatter, SUPPRESS
import logging
from textwrap import dedent, wrap

from badlinkfinder import __doc__, __version__
from badlinkfinder.utilities import str2LogLevel

logger = logging.getLogger('blf.cli')

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
    '--workers',
    type=int,
    default=5,
    help="""
    By default, 5 workers are used for the crawler.
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
    '--include-inbound',
    dest='include_inbound',
    action='store_true',
    help="""
    Whether to include inbound URLs when reporting Site Errors (show where they were referenced from)
    """
)

crawler_settings.add_argument(
    '--output-file',
    dest='output_file',
    type=str,
    help="""
    File name for storing the errors found.
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
    '--ignore-schemes',
    action='append',
    dest='ignore_schemes',
    help="""
    Ignore scheme when parsing URLs so that it does not detect as invalid.
        --ignore-schemes custom
    will ignore any URL that looks like "custom:nonstandardurlhere.com"
    (You can declare this option multiple times)
    """
)

parser_settings.add_argument(
    '--ignore-domains',
    action='append',
    dest='ignore_domains',
    help="""
    Ignore external domain when crawling URLs. 
        --ignore-domains example.com
    will not crawl any URL that is on "example.com".
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

log_levels = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET']
log_level_help = ''
for log_level in log_levels:
    log_level_help += '{} | '.format(log_level)
log_level_help = '[{}]'.format(log_level_help.rstrip(' |'))

troubleshooting.add_argument(
    '--log_level', '--log-level',
    dest='log_level',
    type=str,
    default='WARNING',
    help=log_level_help
)

def extra_parse_logic(args):
    # do extra parsing/validation on arguments here
    try:
        level = str2LogLevel(args.log_level)
    except ValueError:
        raise BLFInvalidArgument('Log level "{}" is invalid. Please use one of the following values: {}' .format(args.log_level, log_level_help))
    args.log_level = level

    return args

class BLFInvalidArgument(Exception):
    pass