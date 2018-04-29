

# The `Engine` does all of the heavy lifting and orchistration of the `Crawler`.


import logging
from urllib.parse import urlparse

import badlinkfinder.sitegraph as sg
from badlinkfinder.taskqueue import TaskQueue

log = logging.getLogger('Engine')


class Engine:

    def __init__(self, crawler, url, sitegraph=None, crawler_threads=8):
        self.crawler = crawler
        self.sitegraph = sitegraph
        self.url = url

        if not sitegraph:
            self.sitegraph = sg.SiteGraph()

        self.queue = TaskQueue(crawler_threads)

        # Hack these in for now
        self.crawler.queue = self.queue
        self.crawler.sitegraph = self.sitegraph

        self.crawler.domain = urlparse(self.url).netloc

    def main(self):
        response = self.crawler.retrieve(self.url)

        log.debug('Adding crawler object to queue for url: ' + response.url)
        self.queue.add_task(self.crawler.crawl, response.url)
        self.queue.join()

    def get_errors(self):
        return self.crawler.errors
