import requests
import re

class Crawler:
    href_regexp = re.compile(r'href=[\'"]?([^\'" >]+)')
    url_regexp = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

    def __init__(self):
        self.graph = dict()
        self.visited = set()
        self.to_visit = []

    def crawl(self, url=None):
        try:
            if url is not None:
                self.to_visit.append((None, url))
            while len(self.to_visit) > 0:
                print('len(visited)  = %d' % len(self.visited))
                print('len(to_visit) = %d' % len(self.to_visit))
                print('')
                origin, target = self.to_visit[0]
                self.to_visit = self.to_visit[1:]
                try:
                    req=requests.get(target)
                except Exception:
                    continue
                if target not in self.visited:
                    self.visited.add(target)
                    for url in self.url_regexp.findall(req.text):
                        self.to_visit.append((target, url))
                    try:
                        self.graph[origin].append(target)
                    except KeyError:
                        self.graph[origin] = [target]
        except KeyboardInterrupt:
            return
