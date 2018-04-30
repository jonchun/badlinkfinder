#!/usr/bin/env python3
# coding: utf-8

from badlinkfinder.utilities import normalize_url
from collections import defaultdict, namedtuple
import threading

def threadsafe(func):
    def _threadsafe(self, *args, **kwargs):
        with self._lock:
            return func(self, *args, **kwargs)
    return _threadsafe

class SiteGraph:
    def __init__(self):
        Graph = namedtuple('Graph', ['inbound', 'outbound'])
        self._graph = Graph(defaultdict(set), defaultdict(set))
        self._nodes = {}
        self._lock = threading.Lock()

    def add_neighbor(self, from_url, to_url):
        from_url = normalize_url(from_url)
        to_url = normalize_url(to_url)
        self._graph.inbound[to_url].add(from_url)
        self._graph.outbound[from_url].add(to_url)

    def get_inbound(self, url):
        return self._graph.inbound[normalize_url(url)]

    @threadsafe
    def __setitem__(self, url, value):
        url = normalize_url(url)
        self._nodes[url] = value

    def __getitem__(self, url):
        return self._nodes[normalize_url(url)]

    @threadsafe
    def __contains__(self, url):
        url = normalize_url(url)
        for key in self._nodes:
            if key == url:
                return True
        return False
