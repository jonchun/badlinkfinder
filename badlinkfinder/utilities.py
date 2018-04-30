#!/usr/bin/env python3
# coding: utf-8

import logging

from url_normalize import url_normalize

def normalize_url(url):
    normalized_url = url_normalize(url).split('#')[0]
    return normalized_url

"""
Convert string to log level. Borrowed from Fail2Ban.
https://github.com/fail2ban/fail2ban/blob/1b4ba602bac38a067b5abb9a941feab53c36c915/fail2ban/helpers.py#L136
"""
def str2LogLevel(value):
    value = str(value)
    try:
        ll = getattr(logging, value.upper())
    except AttributeError:
        raise ValueError("Invalid log level %r" % value)
    return ll
