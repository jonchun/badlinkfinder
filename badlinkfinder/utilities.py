#!/usr/bin/env python3
# coding: utf-8

from url_normalize import url_normalize

def normalize_url(url):
    normalized_url = url_normalize(url).split('#')[0]
    return normalized_url
