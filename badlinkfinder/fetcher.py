#!/usr/bin/env python3
# coding: utf-8

import logging
import mimetypes
import sys
from urllib.parse import urlparse

import lxml.html
import requests

logger = logging.getLogger('blf.fetcher')

def fetch_url_head(url, headers=None, timeout=10):
    logger.info('HEAD: {}'.format(url))

    request_parameters = {
        'headers': headers,
        'timeout': timeout,
        'allow_redirects': True,
    }

    site_node = None

    try:
        response = requests.head(url, **request_parameters)
    except Exception as e:
        logger.warning('Failed to load {}: {}'.format(url, e))
        site_node = SiteNode(url, 'HEAD', status_code=-1, error=e)
    else:
        site_node = SiteNode(url, 'HEAD', final_url=response.url, status_code=response.status_code, headers=response.headers, contents=response.content)

    return site_node

def fetch_url_get(url, headers=None, timeout=10):
    logger.info('GET: {}'.format(url))

    request_parameters = {
        'headers': headers,
        'timeout': timeout,
        'allow_redirects': True,
    }

    site_node = None

    try:
        response = requests.get(url, **request_parameters)
    except Exception as e:
        logger.warning('Failed to load {}: {}'.format(url, e))
        site_node = SiteNode(url, 'GET', status_code=-1, error=e)
    else:
        site_node = SiteNode(url, 'GET', final_url=response.url, status_code=response.status_code, headers=response.headers, contents=response.content)

    return site_node

def get_all_referenced_urls(html, base_url):
    logger.info('searching {} for neighbors'.format(base_url))
    try:
        dom = lxml.html.fromstring(html)
    except Exception as e:
        logger.error('Unable to parse {} | {}'.format(base_url, e))
        return []
    else:
        dom.make_links_absolute(base_url, resolve_base_href=True)
        return [i[2] for i in dom.iterlinks()]

class SiteNode:
    def __init__(self, url, request_type, final_url=None, status_code=None, headers=None, contents=None, error=None):
        """
        Construct a new 'SiteNode' object.

        Args:
            url (str): The URL of the node
            final_url (str): The final URL of the node (possibly different if a redirect was followed)
            status_code (int): Status code of Response
            headers (dict): Headers of Response
            contents (bytes): Contents of Response
            error (Exception): Optionally contains error/exceptions.
        """
        self.url = url
        self.request_type = request_type
        if final_url:
            self.final_url = final_url
        else:
            self.final_url = url
        self.status_code = status_code
        self.headers = headers
        self.contents = contents
        self.error = error


    @property
    def is_ok(self):
        # Returns whether the status_code is 200 OK
        return self.status_code == 200

    @property
    def is_html(self):
        # Returns whether the content type is 'text/html'
        return 'text/html' in self.headers["Content-Type"].lower()

    @property
    def loaded(self):
        # Returns whether the status_code exists and is not -1 (used to indicate that loading the page failed/timed out)
        if self.status_code == -1:
            return False

        if self.status_code:
            # only return True if status_code is not None
            return True

        return False

    @property
    def final_domain(self):
        parsed_url = urlparse(self.final_url)
        return parsed_url.netloc

    @property
    def neighbors(self):
        """
        Return a list of neighbors
        """
        neighbors = []
        if self.is_ok and self.is_html:
            neighbors = get_all_referenced_urls(self.contents, self.final_url)

        return neighbors

    def __repr__(self):
        error_msg = ''
        if self.error:
            error_msg = ' ' + self.error 
        return "<SiteNode {} {} [{}]{}>".format(self.request_type, self.url, self.status_code, error_msg)

if __name__ == "__main__":
    url = sys.argv[1]
    print(fetch_url(url))
