import webbrowser

from server.webserver import Webserver, App
from store import Store, load_store
from crawler import Crawler

class SearchApp(App):
    """
    Webanwendung zum Konvertieren von Celisus-Grad in Fahrenheit-Grad.

    Diese sehr einfache Anwendung demonstriert die Verwendung des Server-Frameworks.
    Die Klasse Celsius-App benötigt zwei Methoden:
    1. Registrierung der Routen
    2. Definition eines Request-Handlers
    """

    def __init__(self, s, **kwargs):
        self.store = s
        App.__init__(self, **kwargs)  # super init

    def register_routes(self):
        self.add_route('', self.search)  # there is only one route for everything

    def search(self, request, response, pathmatch=None):
        msg = ''
        q = ''
        if 'q' in request.params:  # check if parameter is given
            q = request.params['q']
            hitlist = self.store.search(q)
            msg = "<h2>Ergebnis für <i>'{}'</i></h2>".format(q)
            for (url, values) in hitlist:
                msg += """<h3><a href="{link}">{title}</a></h3>
                         <p><a href="{link}">{link}</a></p>
                         <p>{teaser}<p>""".format(
                    link=url,
                    title=self.store.pages[url]['title'],
                    teaser=self.store.get_teaser(url, q))
        response.send_template('templates/search/search.tmpl', {'q': q, 'netloc': self.store.netloc, 'msg': msg})


if __name__ == '__main__':
    # entry = 'https://www.informatik.uni-osnabrueck.de'
    # entry = 'https://www.uni-osnabrueck.de'
    # entry = 'https://www.virtuos.uni-osnabrueck.de'
    entry = 'http://vm009.rz.uos.de'

    s = load_store(entry)
    if not s:
        s = Store(entry)
        c = Crawler(s)
        c.crawl()
        s.save()

    w = Webserver()
    w.add_app(SearchApp(s, prefix=''))
    w.serve()
    webbrowser.open_new_tab("http://localhost:8080/")