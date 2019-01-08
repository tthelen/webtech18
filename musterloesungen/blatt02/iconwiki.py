"""
iconwiki.py
A very very simple Wiki with icon editor

@author: Tobias Thelen
@contact: tobias.thelen@uni-osnabrueck.de
@licence: public domain
@status: completed
@version: 1 (10/2018)
"""
import re
import os

from server import webserver
from server.apps.static import StaticApp
from server.middlewares.session import SessionMiddleware
from server.middlewares.basic_auth import BasicAuthMiddleware
from server.webserver import StopProcessing


class NoSuchPageError(Exception):
    """Raise if try to access non existant wiki page."""
    pass


class WikiApp(webserver.App):
    """
    Webanwendung zum kollaborativen Schreiben (wiki).

    Diese sehr einfache Anwendung demonstriert ein simples Wiki.
    """

    def register_routes(self):
        self.add_route("", self.show)
        self.add_route("show(/(?P<pagename>\w+))?", self.show)
        self.add_route("edit/(?P<pagename>\w+)", self.edit)
        self.add_route("save/(?P<pagename>\w+)", self.save)

    def pagelist(self):
        print([x for x in os.listdir("data/wikipages")])
        return [self.get_page_icon(x) for x in os.listdir("data/wikipages")]

    def read_page(self, pagename):
        """Read wiki page from data directory or raise NoSuchPageError."""

        try:
            with open("data/wikipages/"+pagename, "r", encoding="utf-8", newline='') as f:
                x = f.read()
                return x
        except IOError:
            raise NoSuchPageError

    def get_page_icon(self, pagename):
        icon = {'data': '', 'title': '', 'pagename': pagename}
        try:
            with open("data/wikipage_icons/"+pagename, "r", encoding="utf-8", newline='') as f:
                icon_name = f.read()
        except FileNotFoundError:
            return icon
        try:
            with open("data/icons/" + icon_name, "r", encoding="utf-8", newline='') as f:
                data = f.read()
            return {'data': data, 'title': icon_name, 'pagename': pagename}
        except FileNotFoundError:
            return {'data': '', 'title': icon_name, 'pagename': pagename}

    def save_page_icon(self, pagename, icon_name):
        f = open("data/wikipage_icons/" + pagename, "w", encoding='utf-8', newline='')
        f.write(icon_name)
        f.close()

    def markup(self, text):
        """Substitute wiki markup in text with html."""

        text = re.sub(r"<",
                      r"&lt;",
                      text)

        # substitute links: [[pagename]] -> <a href="/show/pagename">pagename</a>
        text = re.sub(r"\[\[([a-zA-Z0-9]+?)\]\]",
                      r"<a href='/show/\1'>\1</a>",
                      text)

        # substitute headlines: !bang -> <h1>bang</h1>
        text = re.sub(r"^!(.*)$", r"<h1>\1</h1>", text, 0, re.MULTILINE)

        # replace two ends of line with <p>
        text = re.sub(r"\r?\n\r?\n", r"<p>", text)

        # replace one end of line with <br>
        text = re.sub(r"\r?\n\r?\n", r"<br>", text)

        return text

    def show(self, request, response, pathmatch=None):
        """Evaluate request and construct response."""

        try:
            pagename = pathmatch.group('pagename') or "main"
        except IndexError:
            pagename = "main"  # default pagename

        try:
            text = self.read_page(pagename)
            icon = self.get_page_icon(pagename)
        except NoSuchPageError:
            # redirect to edit view if page does not exist
            response.send_redirect("/edit/" + pagename)
            return

        # page history in session:
        # - history is stored in session under key 'page_history'

        # if key is not present, init with empty list
        try:
            page_history = request.session['page_history']
        except KeyError:
            request.session['page_history'] = page_history = []
        # show page
        response.send_template('wiki/show.tmpl', {'text': self.markup(text),
                                                  'pagename': pagename,
                                                  'icon': icon,
                                                  'pagelist':self.pagelist(),
                                                  'page_history': page_history})

        # add current page after generating page
        # put current page in front of page history and limit length to 3
        request.session['page_history'] = [pagename] + request.session['page_history'][:2]


    def edit(self, request, response, pathmatch=None):
        """Display wiki page for editing."""

        try:
            pagename = pathmatch.group('pagename') or "main"
        except IndexError:
            pagename = "main"

        try:
            text = self.read_page(pagename)
        except NoSuchPageError:
            # use default text if page does not yet exist
            text = "This page is still empty. Fill it."

        icon_list = os.listdir("data/icons")
        icons = []
        for icon_title in icon_list:
            with open("data/icons/"+icon_title, "r") as f:
                icons.append({'data': f.read(), 'title': icon_title})

        page_icon = self.get_page_icon(pagename)

        # fill template and show
        response.send_template('wiki/edit.tmpl', {'text': text,
                                                  'pagename': pagename,
                                                  'pagelist': self.pagelist(),
                                                  'page_icon': page_icon,
                                                  'icons': icons})

    def save(self, request, response, pathmatch=None):
        """Evaluate request and construct response."""

        try:
            pagename = pathmatch.group('pagename')
        except IndexError:
            # no pagename given: error
            response.send_template("wiki/wikierror.html",
                                   {'error': 'No pagename given.', 'text': 'save action needs pagename'},
                                   code=500)
            return

        try:
            wikitext = request.params['wikitext']
        except KeyError:
            # no text given: error
            response.send_template("wiki/wikierror.html",
                                   {'error': 'No wikitext given.', 'text': 'save action needs wikitext'},
                                   code=500)
            return

        # ok, save text
        f = open("data/wikipages/" + pagename, "w", encoding='utf-8', newline='')
        f.write(wikitext)
        f.close()

        # if we have an icon parameter and it's properly formed, save it
        if 'icon' in request.params and re.match(r'^[a-zA-Z0-9]+$', request.params['icon']):
            self.save_page_icon(pagename, request.params['icon'])

        response.send_redirect("/show/"+pagename)


class IconEditorApp(webserver.App):

    def register_routes(self):
        self.add_route("$", self.show)
        self.add_route("save$", self.save)

    def show(self, request, response, pathmatch):
        """Show the editor. Provide list of saved icons."""

        icon_list = os.listdir("data/icons")
        icons = []
        for icon_title in icon_list:
            with open("data/icons/"+icon_title, "r") as f:
                icons.append({'data': f.read(), 'title': icon_title})
        response.send_template("iconeditor.tmpl", {'icons': icons})

    def save(self, request, response, pathmatch):
        """Save base64-encoded representation of icon pixels to a file."""

        if 'title' not in request.params or \
                not re.match(r"^[a-zA-Z0-9]+$", request.params['title']) or \
                'icon' not in request.params or \
                not request.params['icon'].startswith('data:'):
            raise StopProcessing(500, "Invalid parameters")
        else:
            with open("data/icons/"+request.params['title'], "w") as f:
                f.write(request.params['icon'])
        response.send_redirect('/'+self.prefix+'/')


class HelpApp(webserver.App):

    def register_routes(self):
        self.add_route("/", self.help)

    def help(self, request, response, pathmatch):
        response.send_template('help.tmpl')


if __name__ == '__main__':
    s = webserver.Webserver()
    s.set_templating("jinja2")
    s.add_app(HelpApp(prefix='help'))
    s.add_app(IconEditorApp(prefix='iconeditor'))
    s.add_app(StaticApp(prefix='static', path='static'))
    s.add_app(WikiApp(prefix=''))
    s.add_middleware(SessionMiddleware())
    s.add_middleware(BasicAuthMiddleware({'user': 'pass'}))
    s.serve()
