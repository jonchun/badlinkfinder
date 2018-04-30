#!/usr/bin/env python3
# coding: utf-8

import logging
import mimetypes
import sys
from urllib.parse import urlparse

import lxml.html
import requests

logger = logging.getLogger('blf.fetcher')

def fetch_url(url, request_type='GET', headers=None, timeout=10, ignore_schemes=[]):
    logger.info('{}: {}'.format(request_type, url))
    parsed_url = urlparse(url)
    neighbors = []

    request_parameters = {
        'headers': headers,
        'timeout': timeout,
        'allow_redirects': True,
    }
    try:
        if request_type == 'HEAD':
            response = requests.head(url, **request_parameters)
        elif request_type == 'GET':
            response = requests.get(url, **request_parameters)
        else:
            raise Exception('Unknown request type: {}'.format(request_type))
    except Exception as e:
        logger.warning('Failed to load {}: {}'.format(url, e))
        site_node = SiteNode(url, request_type, status_code=-1, error=e)
    else:
        site_node = SiteNode(url, request_type, final_url=response.url, status_code=response.status_code)

        if site_node.status_code == 200:
            # Everything's good if 200, so parse for links if it was a GET request
            if request_type == 'GET' and 'text/html' in response.headers["Content-Type"].lower():
                # Check to see if we have an HTML response. If so, we need to search for neighboring URLs.
                neighbors = get_neighbors(response.content, response.url, ignore_schemes=ignore_schemes)
    
    return (site_node, neighbors)

def get_neighbors(html, base_url, ignore_schemes=[]):
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
    def __init__(self, url, request_type, final_url=None, status_code=None, contents=None, error=None):
        """
        Construct a new 'SiteNode' object.

        :param url: The URL of the node
        :param final_url: The final URL of the node (possibly different if a redirect was followed)
        :param status_code: Status Code of site
        :param contents: optionally store content of site
        :param error: optional error message
        """
        self.url = url
        self.request_type = request_type
        if final_url:
            self.final_url = final_url
        else:
            self.final_url = url
        self.status_code = status_code
        self.contents = contents
        self.error = error

    def __repr__(self):
        error_msg = ''
        if self.error:
            error_msg = ' ' + self.error 
        return "<SiteNode {} {} [{}]{}>".format(self.request_type, self.url, self.status_code, error_msg)

if __name__ == "__main__":
    url = sys.argv[1]
    print(fetch_url(url))
