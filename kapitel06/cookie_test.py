"""
Created on May 16, 2011

:author: tobias thelen
:date: 2011-2018
:licence: public domain
"""

from server import webserver


class CookieTesterApp(webserver.App):
    """Test app for cookie handling."""

    def register_routes(self):
        self.server.add_route(r"", self.cookie_tester)

    def cookie_tester(self, request, response, pathmatch):
        """Action handler, render page with value of 'name' cookie."""
        try:
            n = request.cookies['name']
        except KeyError:
            n = "[kein Cookie gesetzt]"
        c = webserver.Cookie("name", "tobias")
        response.add_cookie(c)
        response.send(body="Alter Zustand: %s" % n)


if __name__ == '__main__':
    print("Server running.")
    server = webserver.Webserver()
    server.add_app(CookieTesterApp())
    server.serve()
