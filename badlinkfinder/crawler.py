#!/usr/bin/env python3
# coding: utf-8

import logging
import mimetypes
from urllib.parse import urlparse

import requests

from badlinkfinder.fetcher import fetch_url_head, fetch_url_get
from badlinkfinder.sitegraph import SiteGraph
from badlinkfinder.taskqueue import TaskQueue

logger = logging.getLogger('blf.crawler')

class BreakLoop(Exception): pass

class Crawler:    
    """The Crawler class orchestrates different modules to crawl a website.

    Attributes:
        queue (TaskQueue): 
        graph (SiteGraph): 
        errors (list of (url (str), error_type str, error_msg str)): contains a list of tuples of URLs where errors were found, custom error types, and custom error messages
        domain (str): Contains the original domain of the seed URL
    """
    def __init__(self, workers=5, timeout=10, ignore_schemes=[], ignore_domains=[]):
        """
        Construct a new Crawler

        Args:
            workers (int): How many workers to use when crawling site.
            timeout (int): Timeout when fetching URLs.
            ignore_schemes (list): URL schemes to ignore when crawling.
            ignore_domains (list): external domains to ignore when crawling.
        """
        self.queue = TaskQueue(num_workers=workers)
        self.graph = SiteGraph()
        self.errors = []

        self.ignore_schemes = ['mailto', 'tel', 'data', 'about']
        if ignore_schemes:
            self.ignore_schemes.extend(ignore_schemes)
            self.ignore_schemes = list(dict.fromkeys(self.ignore_schemes))
        self.ignore_domains = ignore_domains

        # Timeout setting for loading a page
        self.timeout = timeout
        self.domain = None

    def run(self, seed_url):
        if not seed_url.startswith('http://') and not seed_url.startswith('https://'):
            seed_url = 'http://' + seed_url

        seed_node = fetch_url_head(seed_url)

        if not (seed_node.is_ok and seed_node.is_html):
            raise Exception('Unable to load seed URL. Exiting...')

        parsed_seed = urlparse(seed_node.final_url)
        self.domain = parsed_seed.netloc
        if self.domain in self.ignore_domains:
            logger.critical('The seed domain was found in the ignore list')

        self.queue.add_task(self.crawl, seed_node.final_url)
        self.queue.join()

        return self.errors

    def crawl(self, url):
        # No need to crawl if we've already crawled it.
        if url in self.graph:
            logger.info('Cache: {}'.format(url))
            return

        try:
            # Set this first so that we have the key in place and prevent future crawling of the URL.
            self.graph[url] = None
            
            request_type = smart_request_type(url, self.domain)

            if request_type == 'GET':
                site_node = fetch_url_get(url, timeout=self.timeout)
            elif request_type == 'HEAD':
                site_node = fetch_url_head(url, timeout=self.timeout)
            else:
                logger.error('Invalid Request Type {} when crawling {}'.format(request_type, url))
                return

            possible_neighbors = []

            if site_node.final_domain == self.domain:
                # We only want to search for neighbors on the same domain
                possible_neighbors = site_node.neighbors

            filtered_neighbors = self.filter_neighbors(possible_neighbors)
            self.graph[url] = site_node

            if not site_node.is_ok:
                self.site_error(site_node)

            for neighbor_url in filtered_neighbors:
                self.queue.add_task(self.crawl, neighbor_url)
                self.graph.add_neighbor(url, neighbor_url)
        except Exception:
            logger.error('ERROR:', exc_info=True)

    def filter_neighbors(self, possible_neighbors):
        neighbors = []

        for current_link in possible_neighbors:
            parsed_link = urlparse(current_link)

            try:
                for scheme in self.ignore_schemes:
                    if parsed_link.scheme == scheme:
                        raise BreakLoop
            except BreakLoop:
                continue

            min_attributes = ('scheme', 'netloc')
            if not all([getattr(parsed_link, attr) for attr in min_attributes]):
                logger.warning('invalid link: {}'.format(current_link))
                continue
            neighbors.append(current_link)

        return neighbors

    def site_error(self, site_node, error_type=None, error_msg=None):
        se = SiteError(self.graph, site_node.url, error_type=error_type, error_msg=error_msg)
        logger.warning(se)
        self.errors.append(se)

# Logic to figure out how to crawl the page. We don't want to search for links on assets or external sites
def smart_request_type(url, domain=None):
        parsed_url = urlparse(url)

        if parsed_url.scheme not in ['http', 'https']:
            logger.warning('URL not HTTP: {}'.format(url))
            return False

        request_type = 'GET'

        """
        Don't go crawling the entire internet. Let's stay within the original domain (if provided). However, we still want to crawl w/ HEAD request
        just to see if the resource is even available or if there's some type of status code problem. 
        """
        if domain and parsed_url.netloc != domain:
            request_type = 'HEAD'
        else:
            # Guess the MIME type based on extension. If it is an asset, then no need for a full crawl.
            mime_guess, _ = mimetypes.guess_type(parsed_url.path)
            asset_types = ['image', 'application', 'audio', 'css', 'js']

            if mime_guess:
                for asset_type in asset_types:
                    if asset_type in mime_guess:
                        request_type = 'HEAD'
                        break

        logger.debug('smart_request_type: {} ({})'.format(url, request_type))
        return request_type

class SiteError:
    def __init__(self, graph, url, error_type=None, error_msg=None):
        self.url = url

        self.graph = graph
        self.node = graph[url]

        self.error_type = error_type
        self.error_msg = error_msg
        self.include_inbound = False


    def __repr__(self):
        repr_str = '<SiteError '
        try:
            if self.error_type:
                repr_str += '{} ({})'.format(self.error_type, self.url)
            elif self.node.status_code == -1:
                # Error loading the page
                repr_str += 'load_fail ({})'.format(self.url)
                self.error_msg = self.node.error
            elif self.node.status_code:
                # make sure status_code is set
                repr_str += '{} ({})'.format(self.node.status_code, self.url)
            else:
                # Shouldn't ever get here
                repr_str += 'unknown ({})'.format(self.url)

            if self.error_msg:
                repr_str += ': {}>'.format(self.error_msg)
            else:
                # Empty error message
                repr_str += '>'

            if self.include_inbound:
                # Find parent nodes
                repr_str += '\n  Referenced From:\n'
                for inbound_url in self.graph.get_inbound(self.url):
                    repr_str += '    - {}\n'.format(inbound_url)

            return repr_str.rstrip()
        except Exception as e:
            print(e)
            return 'Error displaying SiteError'
