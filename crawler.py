#! /usr/bin/env python3

import requests
import re
import sys
from urllib.parse import urlparse, urljoin, urldefrag
import time

class Graph:
    def __init__(self):
        self.in_arcs = dict()
        self.out_arcs = dict()

    @staticmethod
    def add_arc(arcs, origin, target):
        try:
            arcs[origin].add(target)
        except KeyError:
            arcs[origin] = set([target])

    def add(self, origin, target):
        self.add_arc(self.out_arcs, origin, target)
        self.add_arc(self.in_arcs, target, origin)

class Crawler:
    href_regexp = re.compile(r'href=[\'"]?([^\'" >]+)')
    url_regexp = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

    def __init__(self):
        self.graph = Graph()
        self.visited = set()
        self.to_visit = []
        self.errors = []
        self.crawl_time = 0

    def print_stats(self):
        print('len(visited)  = %d' % len(self.visited))
        print('len(to_visit) = %d\n' % len(self.to_visit))

    @staticmethod
    def process_url(url):
        if url.endswith('/'):
            url = url[:-1]
        if url.startswith('http'):
            return url
        if url.startswith('//'):
            url = url[2:]
        return 'http://%s' % url

    def find_urls(self, target, req):
        for url in self.href_regexp.findall(req.text):
            try:
                url = urlparse(self.process_url(urldefrag(url)[0]))
            except ValueError:
                self.errors.append(url)
                continue
            if url.netloc != '': # absolute url
                self.to_visit.append((target, self.process_url(url.netloc)))
                self.to_visit.append((target, self.process_url(url.geturl())))
            else: # relative url
                self.to_visit.append((target, self.process_url(urljoin(target, url.path))))

    def __crawl__(self, function):
        while len(self.to_visit) > 0 and len(self.visited) < 1000:
            # self.print_stats()
            origin, target = self.to_visit.pop(0)
            if target in self.visited:
                self.graph.add(origin, target)
            else:
                try:
                    req=requests.get(target, timeout=5)
                except Exception as e:
                    if isinstance(e, KeyboardInterrupt):
                        raise e
                    self.errors.append(target)
                    continue
                if req.status_code != 200:
                    self.errors.append(target)
                else:
                    function(req)
                    self.find_urls(target, req)
                    self.visited.add(target)
                    self.graph.add(origin, target)

    def crawl(self, url=None, function=lambda req: req):
        begin = time.time()
        if url is not None:
            self.to_visit.append(('/', url))
        try:
            self.__crawl__(function)
        except KeyboardInterrupt:
            pass
        t = time.time()-begin
        self.crawl_time += t
        print('')
        print('Last crawl time:  %0.2fs' % t)
        print('Total crawl time: %0.2fs' % self.crawl_time)
        self.print_stats()

def doWork(url):
    crawler = Crawler()
    crawler.crawl(url)
    print('Thread for url %s finished.' % url)

if __name__ == '__main__':
    if(len(sys.argv) != 2):
        print('Syntax: %s <url>' % sys.argv[0])
        sys.exit(1)
    doWork(sys.argv[1])
