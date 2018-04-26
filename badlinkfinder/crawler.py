#!/usr/bin/env python3
# coding: utf-8

import badlinkfinder.url_finder as url_finder
import badlinkfinder.graph as graph
import badlinkfinder.logs as logs
import badlinkfinder.workers as workers

from urllib.parse import urlparse, urlunparse
import mimetypes
import time
import requests

class Crawler:    
    def __init__(self, worker_count, verbose=False):
        self.wm = workers.WorkerManager(worker_count=worker_count)
        self.buffer = []

        self.graph = graph.WebsiteGraph()
        self.errors = []

        self.logger = logs.Logger(self, verbose)

        # Timeout setting for loading a page
        self.timeout = 5

        self.domain = None


    def run(self, seed_url, silent=False):
        if not seed_url.startswith('http'):
            seed_url = 'http://' + seed_url

        parsed_seed = urlparse(seed_url)
        self.domain = parsed_seed.netloc
        self.wm.add_task(self.crawl, seed_url)
        self.wm.wait_complete()

        return self.errors

    def crawl(self, url):
        # No need to crawl if we've already crawled it.
        if url in self.graph:
            return

        # Add a WebsiteNode to graph and log it.
        self.graph.add_node(url)
        self.logger.crawl(url)
        self._smart_crawl(url)

    # Logic to figure out how to crawl the page. We don't want to search for links on assets.
    def _smart_crawl(self, url):
        parsed_url = urlparse(url)

        # Don't go crawling the entire internet. Let's stay within the original domain
        if parsed_url.netloc != self.domain:
            self._complete_crawl(url)
            return

        # Only parse http.
        if parsed_url.scheme not in ['http', 'https']:
            self._complete_crawl(url)
            return

        # Guess the MIME type based on extension. If it is an asset, then no need for a full crawl.
        mime_guess, _ = mimetypes.guess_type(parsed_url.path)
        asset_types = ['image', 'application']

        if mime_guess:
            for asset_type in asset_types:
                if asset_type in mime_guess:
                    self._asset_crawl(url)
                    return

        self._full_crawl(url)


    def _asset_crawl(self, url):
        self.logger.asset_crawl(url)

        node = self.graph[url]
        node.request_type = "head"

        try:
            response = requests.head(url, timeout=self.timeout)
        except Exception as e:
            node.status = 'error'
            node.error = e

            self.save_error('Error crawling {} | {}'.format(url, e))
            self._complete_crawl(url)
        else:
            node.status = 'done'
            node.status_code = response.status_code

            if node.status_code >= 300:
                self.save_error('Error crawling {} | Status Code {}'.format(url, response.status_code))

            self._complete_crawl(url)

    def _full_crawl(self, url):
        self.logger.full_crawl(url)

        node = self.graph[url]
        node.request_type = "get"

        try:
            response = requests.get(url, timeout=self.timeout)
        except Exception as e:
            node.status = 'error'
            node.error = e

            self.save_error('Error crawling {} | {}'.format(url, e))
            self._complete_crawl(url)
        else:
            node.status = 'done'
            node.status_code = response.status_code

            if node.status_code >= 300:
                self.save_error('Error crawling {} | Status Code {}'.format(url, response.status_code))

            if response.text and response.headers["Content-Type"].startswith('text'):
                neighbor_urls, errors = url_finder.neighbors(response.text, response.url)

                self.errors.extend(errors)

                for neighbor_url in neighbor_urls:
                    self.graph.add_neighbor(url, neighbor_url)
                    self.wm.add_task(self.crawl, neighbor_url)

        self._complete_crawl(url)

    def _complete_crawl(self, url):
        # Finish up crawl of page. Printing a . for ever URL crawled.
        self.logger.complete_crawl(url)

    def save_error(self, error):
        self.errors.append(error)
        self.logger.error(error)