#!/usr/bin/env python3
# coding: utf-8

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

    @threadsafe
    def add_node(self, url):
        self._nodes[url] = SiteNode(url)

    def add_neighbor(self, _from, _to):
        self._graph.inbound[_to].add(_from)
        self._graph.outbound[_from].add(_to)

    def get_inbound(self, url):
        return self._graph.inbound[url]

    def __getitem__(self, url):
        return self._nodes[url]

    @threadsafe
    def __contains__(self, url):
        for key in self._nodes:
            if key == url:
                return True
        return False

class SiteNode:
    def __init__(self, url):
        self.url = url
        self.request_type = None
        self.status = None
        self.status_code = None
        self.contents = None
        self.error = None

    def __repr__(self):
        return "<SiteNode {} {} | {}, {}>".format(self.request_type, self.url, self.status, self.status_code)
