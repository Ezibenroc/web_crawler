import requests
import re
from urllib.parse import urlparse, urljoin, urldefrag

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

    def print_stats(self):
        print('len(visited)  = %d' % len(self.visited))
        print('len(to_visit) = %d\n' % len(self.to_visit))

    @staticmethod
    def process_url(url):
        if url.startswith('http'):
            return url
        if url.startswith('//'):
            url = url[2:]
        return 'http://%s' % url

    def find_urls(self, target, req):
        for url in self.href_regexp.findall(req.text):
            url = urlparse(self.process_url(urldefrag(url)[0]))
            if url.netloc != '': # absolute url
                self.to_visit.append((target, self.process_url(url.netloc)))
                self.to_visit.append((target, self.process_url(url.geturl())))
            else: # relative url
                self.to_visit.append((target, self.process_url(urljoin(target, url.path))))

    def __crawl__(self, function):
        while len(self.to_visit) > 0:
            self.print_stats()
            origin, target = self.to_visit.pop(0)
            if target in self.visited:
                self.graph.add(origin, target)
            else:
                try:
                    req=requests.get(target)
                except requests.exceptions.RequestException as e:
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
        if url is not None:
            self.to_visit.append(('/', url))
        try:
            self.__crawl__(function)
        except KeyboardInterrupt:
            return
