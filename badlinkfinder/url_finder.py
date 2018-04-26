#!/usr/bin/env python3
# coding: utf-8

import lxml.html
import re
from urllib.parse import urlparse

def neighbors(html_body, url):
    out_urls = []    
    errors = []


    html = lxml.html.fromstring(html_body)
    html.make_links_absolute(url, resolve_base_href=True)
    for link in html.iterlinks():
        current_url = link[2]

        # ignore mailto
        if current_url.startswith('mailto'):
            continue

        try:
            parsed_url = urlparse(current_url)
            min_attributes = ('scheme', 'netloc')
            if not all([getattr(parsed_url, attr) for attr in min_attributes]):
                raise Exception
        except Exception as e:
            errors.append("Found invalid URL {} on {}".format(current_url, url))

        out_urls.append(current_url)

    return (out_urls, errors)
