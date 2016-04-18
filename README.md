## Example of use:

In an interactive Python terminal, run the following:

```python
    from crawler import Crawler
    crawler = Crawler()
    crawler.crawl('http://wikipedia.org')
```

At any time, you can suspend the crawling by pressing `Ctrl-C`. You can then
resume the crawling:
```python
    crawler.crawl()
```

You can pass a function to the crawler. This function will be applied on every
successful response to a request against a crawled url. Note that the response
is a result of the method `requests.get`.

For instance, the following will print the “Content-Type” part of the header when
it exists:
```python
    crawler.crawl('http://wikipedia.org', lambda r: print(r.headers['Content-Type']))
```
