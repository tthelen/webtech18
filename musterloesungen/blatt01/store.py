"""store.py

Search index Backend for web crawler (crawler.py) and search page (search.py).

@author: Tobias Thelen
@contact: tobias.thelen@uni-osnabrueck.de
@licence: public domain
@status: completed
@version: 1 (10/2018)
"""

import os.path  # path related functions
import re  # regular expressions
import pickle


def load_store(netloc):
    """Tries to load the store from pickled file.

    :param netloc string The server to crawl.
    :return store Unpickled store object or None.
    """
    fn = slug(netloc)+".pickle"
    if os.path.isfile(fn):
        with open(fn, 'rb') as f:
            store = pickle.load(f)
            return store
    return None


def slug(netloc):
    """Create a filename from a url by removing all non-word characters.

    :param netloc string The server to crawl.
    """
    return re.sub(r'[^\w]', '', netloc)


class Store:
    """The search index."""

    def __init__(self, netloc):
        """Constructor.

        :param netloc string The server to crawl.
        """
        self.netloc = netloc

        # Terms is a dictionary:
        #    key = term
        #    value = dictionary with key=url, value=number of occurences
        self.terms = {}

        # Pages is a dictionary:
        #    key = url
        #    value = dictionary with keys:
        #               words: the cleaned content
        #               title: the title
        self.pages = {}

    def save(self):
        """Save store to pickle file."""
        fn = slug(self.netloc)+".pickle"
        with open(fn, 'wb') as f:
            pickle.dump(self, f)

    def add(self, url, html, title):
        """Add a page to the store.

        :param url string The pages full url.
        :param html string The cleaned page content (just words).
        :param title string The page's title.
        """
        words = html.split()
        for w in words:  # add each word to terms dictionary
            wl = w.lower()
            if wl not in self.terms:  # new term: add new dict with current url and counter
                self.terms[wl] = {url: 1}
            else:
                if url in self.terms[wl]:  # term and url known: add 1
                    self.terms[wl][url] += 1
                else:  # term known and url new: set to 1
                    self.terms[wl][url] = 1
        self.pages[url] = {'words': html, 'title': title}

    def get_teaser(self, page, q):
        """Get a short teaser text for a term on a page.

        :param page string The page URL
        :param q string The search string
        :return A short teaser text from page including term.
        """
        terms = q.split()
        if terms:
            words = self.pages[page]['words'].split()
            for t in terms:
                try:
                    idx = words.index(t)
                except ValueError:
                    continue
                teaser = ' '.join(words[max(0, idx-5):idx+5])
                for term in terms:  # make all search terms yellow
                    teaser = re.sub(term, "<span style='background-color:yellow'>{}</span>".format(term),
                                teaser, flags=re.IGNORECASE)
                break
        return teaser

    def search(self, q):
        """Search for query string.

        :param q string The full query string.
        """

        terms = q.split()  # we may have several search terms

        # Collect list of pages that contain the terms.
        # Format:
        #   key = url
        #   value =  { count: number of terms included
        #              occurrences: list of number of occurences
        #            }
        hits = {}

        # find all pages that contain some of the search terms
        for t in terms:
            try:
                for (url, urlcount) in self.terms[t.lower()].items():
                    if url in hits:
                        hits[url]['count'] += 1
                        hits[url]['occurrences'] += urlcount
                    else:
                        hits[url] = {'count': 1, 'occurrences': urlcount}
            except KeyError:
                # search term not found
                continue

        # create a sorted list
        # Sort criteria:
        #   1. Number of terms included
        #   2. Total number of occurences of these terms
        # (both criteria are used to for a number by taking 100*number of terms + occurences)
        result = sorted(hits.items(), key=lambda i: i[1]['count']*100+i[1]['occurrences'], reverse=True)

        return result
