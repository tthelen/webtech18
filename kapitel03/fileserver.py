__author__ = 'Tobias Thelen'

from server.webserver import Webserver
from server.apps.static import StaticApp

if __name__ == '__main__':
    s = Webserver()
    s.add_app(StaticApp(prefix='', path='static'))
    s.serve()
