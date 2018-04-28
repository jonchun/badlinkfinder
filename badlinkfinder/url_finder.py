#!/usr/bin/env python3
# coding: utf-8

from lxml import etree
import lxml.html
import re
from urllib.parse import urlparse
from badlinkfinder.error import SiteError

def neighbors(body, url, ignore_prefixes):
    out_urls = []    
    errors = []
    
    try:
        body_string = etree.tostring(etree.HTML(body), method="html")
        html = lxml.html.fromstring(body_string)
    except Exception as e:
        """
        import traceback
        traceback.print_exc()
        """
        errors.append("Unable to parse HTML")
    else:
        html.make_links_absolute(url, resolve_base_href=True)
        for link in html.iterlinks():
            current_link = link[2]

            try:
                for ignore_prefix in ignore_prefixes:
                    if current_link.startswith(ignore_prefix):
                        raise Exception
            except Exception:
                continue

            try:
                parsed_url = urlparse(current_link)
                min_attributes = ('scheme', 'netloc')
                if not all([getattr(parsed_url, attr) for attr in min_attributes]):
                    raise Exception
            except Exception as e:
                errors.append('Invalid URL Found: {}'.format(current_link))

            out_urls.append(current_link)
    return (out_urls, errors)
