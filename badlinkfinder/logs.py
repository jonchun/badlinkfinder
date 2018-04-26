#!/usr/bin/env python3
# coding: utf-8

class Logger:
    def __init__(self, crawler, verbose):
        self.crawler = crawler
        self.verbose = verbose

    def crawl(self, url):
        if self.verbose:
            pass
            #print('queueing url: {}'.format(url))

    def asset_crawl(self, url):
        if self.verbose:
            print('crawling HEAD: {}'.format(url))

    def full_crawl(self, url):
        if self.verbose:
            print('crawling GET: {}'.format(url))

    def complete_crawl(self, url):

        if self.verbose:
            print('.', end='', flush=True)
        else:
            print('completed {}'.format(url))


    def log(self, message):
        if self.verbose:
            print(message)

    def error(self, error_message):
        if self.verbose:
            print(error_message)
