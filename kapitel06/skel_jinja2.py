"""
Simple webapp to demonstrate jinja2 templating.

:author: Tobias Thelen
:date: 2016-2018
:licence: public domain
"""

from server.webserver import Webserver, App, Cookie
from server.apps.static import StaticApp


class SkelApp(App):
    """Skeleton app that demonstrates some basic features for templating."""

    def register_routes(self):
        self.add_route("", self.index)
        self.add_route("page2/", self.page2)
        self.add_route("page3/", self.page3)

    @staticmethod
    def index(request, response, pathmatch):
        """The index page."""
        response.send_template('index.tmpl', {
            'current_user': {'id': 815, 'icon': '&#9752;', 'name': 'Tobias Findeisen'}
        })

    @staticmethod
    def page2(request, response, pathmatch):
        """The second page."""
        response.send_template('page2.tmpl', {
            'magic_number': 42,
            'author': {'id': 42, 'icon': '&#9730;', 'name': 'Walter Sparbier'},
            'current_user': {'id': 815, 'icon': '&#9752;', 'name': 'Tobias Findeisen'}
        })

    @staticmethod
    def page3(request, response, pathmatch):
        """The third page."""
        response.send_template('page3.tmpl', {
            'magic_numbers': [7, 13, 23, 27, 42],
            'current_user': {'id': 815, 'icon': '&#9752;', 'name': 'Tobias Findeisen'},
            'message': "<i>HTML-Content  &#x2603;</i>"
        })


if __name__ == '__main__':
    s = Webserver()
    s.set_templating("jinja2")
    s.set_templating_path("templates.jinja2/skel")
    s.add_app(SkelApp())
    s.add_app(StaticApp(prefix='static', path='static'))

    s.serve()
