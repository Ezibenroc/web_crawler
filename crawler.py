import requests
import re
import urllib.parse

class Crawler:
    href_regexp = re.compile(r'href=[\'"]?([^\'" >]+)')
    url_regexp = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

    def __init__(self):
        self.graph = dict()
        self.visited = set()
        self.to_visit = []

    def print_stats(self):
        print('len(graph)    = %d' % len(self.graph))
        print('len(visited)  = %d' % len(self.visited))
        print('len(to_visit) = %d\n' % len(self.to_visit))


    def __crawl__(self):
        while len(self.to_visit) > 0:
            self.print_stats()
            origin, target = self.to_visit[0]
            self.to_visit = self.to_visit[1:]
            req=requests.get(target)
            if target not in self.visited:
                self.visited.add(target)
                for url in self.url_regexp.findall(req.text):
                    url = urllib.parse.urlparse(url)
                    self.to_visit.append((target, '%s://%s' % (url.scheme, url.hostname)))
                    self.to_visit.append((target, url.geturl()))
                try:
                    self.graph[origin].append(target)
                except KeyError:
                    self.graph[origin] = [target]

    def crawl(self, url=None):
        if url is not None:
            self.to_visit.append(('/', url))
        try:
            self.__crawl__()
        except KeyboardInterrupt:
            return
