"""crawler.py

Web crawler using Requests library. Backend is in store.py.

@author: Tobias Thelen
@contact: tobias.thelen@uni-osnabrueck.de
@licence: public domain
@status: completed
@version: 1 (10/2018)
"""

import urllib.parse  # parse urls
import posixpath  # path related functions
import re  # regular expressions

import requests  # the requests library for reliable http client code


class Crawler:
    """Fetches pages, extracts links and feeds the search index."""

    def __init__(self, store):
        self.store = store
        self.queue = ['/']
        self.visited = []

    def get_links(self, html, path):
        """Extract links to other pages (same domain only) from html and adds to quere. Normalizes links.

        :param html string The cleaned html content of a page.
        :param path string The current page's absolute path.
        :return None
        """
        anchors = re.findall(r'<a .*href=["\']([^"]*)["\'].*>(.*)</a>', html)  # result: list of tuples (link and text)
        for a in anchors:
            url = urllib.parse.urlparse(a[0])
            # we want to follow all relative get_links (empty netloc) and all absolute link to same domain
            if (not url.netloc and not url.scheme) or \
                    (url.scheme in ['http', 'https'] and url.netloc and url.netloc == self.store.netloc):
                # not been there yet, not queued yet
                new_path = url.path
                if not new_path.startswith('/'):
                    # handle relative paths
                    # 1. get path except filename from current url path: os.path.dirname(path)
                    # 2. append new, relative url path
                    # 3. normalize path, i.e. resolve ../, ./ etc.
                    # CAVE: path construction is not 100% correct, i.e. removing trailing slashes
                    new_path = posixpath.normpath(posixpath.dirname(path)+'/'+url.path)
                if url.query:
                    new_path += "?"+url.query
                if new_path not in self.store.pages and new_path not in self.visited and new_path not in self.queue:
                    self.queue.append(new_path)

    @staticmethod
    def get_title(html):
        """Extract title from raw html.

        :param html string The raw page content.
        :return string The title.
        """
        title = re.search(r'<title>(.*?)</title>', html, flags=re.S)
        return title[1]

    @staticmethod
    def clean(raw_html):
        """Remove unwanted content from html file.
           Steps are:
           1. Remove script, style and head tags and their content
           2. Remove html comments
           3. Remove all HTML tags
           4. Collapse all white space to single spaces

        :param raw_html string The raw page content.
        :return string The cleaned html.
        """
        html = raw_html
        remove = ['head', 'script', 'style']  # remove script, style and head sections
        for r in remove:
            html = re.sub(r'<{}.*?>.*?</{}>'.format(r, r), ' ', html, flags=re.S)
        html = re.sub(r'<!--.*?-->', ' ', html, flags=re.S)  # remove all html comments
        html = re.sub(r'<.*?>', ' ', html)  # remove all html tags
        html = re.sub(r'\W+', ' ', html)  # collapse all white space to single spaces
        return html

    def fetch(self, path):
        """Fetch a url and store page.

        :param path string the (absolute) url to fetch.
        :return None
        """
        url = self.store.netloc + path
        print("FETCHING {}".format(url))
        r = requests.get(url)
        if r.status_code == 200 and r.headers['Content-Type'].startswith('text/html'):  # only html content
            self.get_links(r.text, path)  # extract links and add them to the queue
            title = self.get_title(r.text)  # page title
            html = self.clean(r.text)  # cleaned page text
            self.store.add(url, html, title)

    def crawl(self):
        """Fetch pages and follow links. Build search database."""
        count = 0
        while self.queue:
            print("{} pages fetched. Queue length is {}.".format(count, len(self.queue)))
            path = self.queue.pop()
            self.visited.append(path)
            self.fetch(path)
            count += 1
        self.store.save()
