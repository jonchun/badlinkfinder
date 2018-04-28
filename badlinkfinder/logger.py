#!/usr/bin/env python3
# coding: utf-8

from enum import IntEnum

class Logger:
    def __init__(self, crawler):
        self.crawler = crawler
        self.verbosity = crawler.verbosity

    def duplicate_crawl(self, url):
        if self.verbosity >= E.INFO:
            print('Cached: {}'.format(url))
        elif self.verbosity >= E.ERROR:
            print('.', end='', flush=True)
            
    def crawl(self, url):
        if self.verbosity >= E.INFO:
            print('Queuing: {}'.format(url))

    def asset_crawl(self, url):
        if self.verbosity >= E.INFO:
            print('HEAD: {}'.format(url))

    def full_crawl(self, url):
        if self.verbosity >= E.INFO:
            print('GET: {}'.format(url))

    def complete_crawl(self, url):
        if self.verbosity >= E.INFO:
            print('Complete: {}'.format(url))
        elif self.verbosity >= E.ERROR:
            print('+', end='', flush=True)


    def log(self, message):
        if self.verbose:
            print(message)

    def error(self, _error):
        if self.verbosity >= E.INFO:
            print('\n')
            print(_error)
        elif self.verbosity >= E.ERROR:
            print('!', end='', flush=True)

class E(IntEnum):
    NONE = 0
    ERROR = 1
    WARNING = 2
    INFO = 3
    ALL = 4