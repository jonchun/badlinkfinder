#!/usr/bin/env python3
# coding: utf-8

from enum import IntEnum

class Logger:
    def __init__(self, crawler, verbosity):
        self.crawler = crawler
        self.verbosity = verbosity

    def duplicate_crawl(self, url):
        if self.verbosity >= E.INFO:
            print('already crawled: {}'.format(url))
        else:
            print('.', end='', flush=True)
            
    def crawl(self, url):
        if self.verbosity >= E.INFO:
            pass
            #print('queueing url: {}'.format(url))
        else:
            print('.', end='', flush=True)

    def asset_crawl(self, url):
        if self.verbosity >= E.INFO:
            print('crawling HEAD: {}'.format(url))

    def full_crawl(self, url):
        if self.verbosity >= E.INFO:
            print('crawling GET: {}'.format(url))

    def complete_crawl(self, url):
        if self.verbosity >= E.INFO:
            print('completed {}'.format(url))
        else:
            pass


    def log(self, message):
        if self.verbose:
            print(message)

    def error(self, error_message):
        if self.verbosity >= E.INFO:
            print(error_message)

class E(IntEnum):
    NONE = 0
    ERROR = 1
    WARNING = 2
    INFO = 3
    ALL = 4