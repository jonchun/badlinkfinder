#!/usr/bin/env python3
# coding: utf-8

from badlinkfinder.error import SiteError
import badlinkfinder.url_finder as url_finder
import badlinkfinder.sitegraph as sitegraph
import badlinkfinder.logger as logger

from badlinkfinder.taskqueue import TaskQueue

from urllib.parse import urlparse, urlunparse
import mimetypes
import time
import requests

class Crawler:    
    def __init__(self, args):
        self.queue = TaskQueue(num_workers=args.threads)

        self.graph = sitegraph.SiteGraph()

        self.errors = []
        self.include_inbound = args.include_inbound

        self.ignore_prefixes = ['mailto:', 'tel:', 'data:']
        if args.ignore_prefixes:
            self.ignore_prefixes.extend(args.ignore_prefixes)
            self.ignore_prefixes = list(dict.fromkeys(self.ignore_prefixes))

        # verbosity must be set before logger since logger references it.
        self.verbosity = args.verbosity
        self.logger = logger.Logger(self)

        # Timeout setting for loading a page
        self.timeout = args.timeout

        self.domain = None

    def run(self, seed_url, silent=False):
        if not seed_url.startswith('http://') and not seed_url.startswith('https://'):
            seed_url = 'http://' + seed_url

        try:
            response = requests.head(seed_url, timeout=self.timeout, allow_redirects=True)
        except Exception as e:
            print('Unable to load seed URL. Exiting...')
            exit()
        else:
            parsed_seed = urlparse(response.url)
            self.domain = parsed_seed.netloc

        self.queue.add_task(self.crawl, response.url)
        self.queue.join()

        return self.errors

    def crawl(self, url):
        # No need to crawl if we've already crawled it.
        if url in self.graph:
            self.logger.duplicate_crawl(url)
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
        asset_types = ['image', 'application', 'audio']

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
            response = requests.head(url, timeout=self.timeout, allow_redirects=True)
        except Exception as e:
            node.status = 'error'
            node.error = e
            self.site_error(url)
            self._complete_crawl(url)
        else:
            node.status = 'done'
            node.status_code = response.status_code

            if node.status_code >= 300:
                self.site_error(url)

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
            self.site_error(url)
            self._complete_crawl(url)
        else:
            node.status = 'done'
            node.status_code = response.status_code

            if node.status_code >= 300:
                self.site_error(url)
            elif response.text and response.headers["Content-Type"].startswith('text'):
                neighbor_urls, errors = url_finder.neighbors(response.content, response.url, self.ignore_prefixes)

                for error_msg in errors:
                    self.site_error(url, error_msg=error_msg, include_inbound=False, type='html')

                for neighbor_url in neighbor_urls:
                    self.graph.add_neighbor(url, neighbor_url)
                    self.queue.add_task(self.crawl, neighbor_url)

            self._complete_crawl(url)

    def _complete_crawl(self, url):
        self.logger.complete_crawl(url)

    def site_error(self, url, **kwargs):
        if 'include_inbound' not in kwargs:
            kwargs['include_inbound'] = self.include_inbound

        se = SiteError(self.graph, url, **kwargs)
        self.errors.append(se)
        self.logger.error(se)
