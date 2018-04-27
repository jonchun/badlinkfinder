#!/usr/bin/env python3
# coding: utf-8

from lxml import etree
import lxml.html
import re
from urllib.parse import urlparse

def neighbors(body, url):
    out_urls = []    
    errors = []
    
    try:    
        body_string = etree.tostring(etree.HTML(body), method="html")
        html = lxml.html.fromstring(body_string)
    except Exception as e:
        import traceback
        traceback.print_exc()
        #traceback.print_tb(e.__traceback__)
        errors.append("Unable to parse HTML on {}".format(url))
    else:
        html.make_links_absolute(url, resolve_base_href=True)
        for link in html.iterlinks():
            current_url = link[2]

            # ignore mailto
            if current_url.startswith('mailto:'):
                continue

            # ignore tel
            if current_url.startswith('tel:'):
                continue

            # ignore data
            if current_url.startswith('data:'):
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
