#!/usr/bin/env python3
# coding: utf-8

import threading

class WebsiteGraph:
    def __init__(self):
        self._nodes = {}
        self._outbound = {}
        self._inbound = {}

        # thread safe
        self.lock = threading.RLock()

    def add_node(self, url):
        self._nodes[url] = WebsiteNode(url)

    def add_neighbor(self, _from, _to):
        # If we don't have an entry for inbound or outbound links, initiate empty list
        if _from not in self._outbound:
            self._outbound[_from] = []

        if _to not in self._inbound:
            self._inbound[_to] = []

        # add urls from/to to list to track neighbors
        self._outbound[_from].append(_to)
        self._inbound[_to].append(_from)

    @property
    def parents(self, url):
        return self._inbound.get(url, [])

    def __getitem__(self, url):
        return self._nodes.get(url)


    def __contains__(self, url):
        self.lock.acquire()
        for node in self._nodes:
            if node == url:
                self.lock.release()
                return True
        self.lock.release()
        return False

class WebsiteNode:
    def __init__(self, url):
        self.url = url
        self.request_type = None
        self.status = None
        self.status_code = None
        self.contents = None
        self.error = None

    def __repr__(self):
        return "<WebsiteNode {} {} | {}, {}>".format(self.request_type, self.url, self.status, self.status_code)

    def __get__(self):
        return self.url