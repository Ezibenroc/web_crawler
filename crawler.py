import requests
import re
import urllib.parse

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

    def __crawl__(self, function):
        while len(self.to_visit) > 0:
            self.print_stats()
            origin, target = self.to_visit.pop(0)
            if target in self.visited:
                self.graph.add(origin, target)
            else:
                req=requests.get(target)
                if req.status_code != 200:
                    self.errors.append(req)
                    continue
                function(req)
                self.visited.add(target)
                for url in self.url_regexp.findall(req.text):
                    url = urllib.parse.urlparse(url)
                    self.to_visit.append((target, '%s://%s' % (url.scheme, url.hostname)))
                    self.to_visit.append((target, url.geturl()))
                self.graph.add(origin, target)

    def crawl(self, url=None, function=lambda req: req):
        if url is not None:
            self.to_visit.append(('/', url))
        try:
            self.__crawl__(function)
        except KeyboardInterrupt:
            return
