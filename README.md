# badlinkfinder

This is a Python 3 program that recursively searches your website to find issues. It was started as an afternoon project out of my desire to explore some web crawling and indexing methodologies, and aims to be an easy tool to scan your website and locate broken assets, links, etc.

You are required to supply a `seed URL` which is where the web crawler will begin its search. In order to prevent it from crawling the entire internet, it will only stay within the initial domain provided in the seed URL. Additionally, it is smart about crawling and tries to guess the MIME type of the URL before downloading it. If it is detected to be an asset (e.g. an image or audio file), it only performs a `HEAD` request in order to save on bandwidth and processing time. 

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Support](#support)
- [Contributing](#contributing)

## Installation

This can be deployed on any OS that has Python 3 available. Simply clone this repository into a directory of your choice.
```
git clone https://github.com/Jonchun/badlinkfinder.git
```

Install Python requirements
```
pip3 install -r requirements.txt
```

## Usage
Execute as a module.

```
python3 -m badlinkfinder URL
```
or
```
blf
```

Current `--help` output.
```
$ blf --help
usage: blf [--workers WORKERS] [--timeout TIMEOUT] [--include-inbound]
           [--output-file OUTPUT_FILE] [--ignore-schemes IGNORE_SCHEMES]
           [--ignore-domains IGNORE_DOMAINS] [--help] [--version]
           [--log_level LOG_LEVEL]
           URL

BadLinkFinder - a recursive bot that scrapes a domain and finds all bad assets/links.

Positional Arguments:
  These arguments come after any flags and in the order they are listed here.
      Only URL is required.

  URL
      The starting seed URL to begin crawling your website. This is required to begin searching for bad links.


Crawler Settings:
  --workers WORKERS
      By default, 5 workers are used for the crawler.

  --timeout TIMEOUT
      By default, requests time out after 10 seconds.

  --include-inbound
      Whether to include inbound URLs when reporting Site Errors (show where they were referenced from)

  --output-file OUTPUT_FILE
      File name for storing the errors found.


Parser Settings:
  --ignore-schemes IGNORE_SCHEMES
      Ignore scheme when parsing URLs so that it does not detect as invalid.
          --ignore-schemes custom
      will ignore any URL that looks like "custom:nonstandardurlhere.com"
      (You can declare this option multiple times)

  --ignore-domains IGNORE_DOMAINS
      Ignore external domain when crawling URLs.
          --ignore-domains example.com
      will not crawl any URL that is on "example.com".
      (You can declare this option multiple times)


Troubleshooting:
  --help
      Show this help message and exit.

  --version
      Show version and exit.

  --log_level LOG_LEVEL, --log-level LOG_LEVEL
      [CRITICAL | ERROR | WARNING | INFO | DEBUG | NOTSET]
```

## Support

Please [open an issue](https://github.com/Jonchun/badlinkfinder/issues/new) for support. This is very much a work in progress, so rapid-development will be happening.

## Contributing
[Open a pull request](https://github.com/Jonchun/badlinkfinder/compare).