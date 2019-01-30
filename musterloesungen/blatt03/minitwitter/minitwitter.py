'''
Created 2013-2019

@author: Tobias Thelen
'''

from server.webserver import Webserver, App, StopProcessing
from server.apps.static import StaticApp
from server.apps.usermanagement import UsermanagementApp
from server.apps.static import StaticApp
from server.middlewares.session import SessionMiddleware
from server.middlewares.csrf import CsrfMiddleware
from server.log import log
import server.usermodel
from tweetsmodel import Tweets, TweetError

import sqlite3 as sqlite
from urllib.parse import quote, unquote


class MiniTwitterApp(App):
    """Create and display status messages"""

    def __init__(self, datadir='data', db_connection=None):
        self.datadir = datadir
        self.db_connection = db_connection
        super().__init__()

    def register_routes(self):
        self.server.add_route(r"/?$", self.show)
        self.server.add_route(r"/logout$", self.logout)
        self.server.add_route(r"/login$", self.login)

    def show(self, request, response, pathmatch):
        """Process all requests. Dispatch POST to save method. Show tweets on GET requests."""

        if request.method.lower() == 'post':
            return self.save(request, response, pathmatch)

        try:
            message = request.params['message']
        except KeyError:
            message = ""

        t=Tweets(self.db_connection)
        m = t.findTweets()
        m.reverse()

        try:
            user = request.session['user']
        except (AttributeError, KeyError):
            user = server.usermodel.AnonymousUser()
        d = {'tweets': m, 'message': message, 'user': user }

        # ajax responses will send a minimal template, other requests a full html page
        if 'ajax' in request.params:
            response.send_template('tweets.tmpl', d)
        else:
            response.send_template('minitwitter.tmpl', d)


    def save(self, request, response, pathmatch):
        """Process post request to save new tweet."""

        if 'user' not in request.session:
            raise StopProcessing(400, "You need to be logged in.")

        import datetime
        now = datetime.datetime.utcnow().strftime("%d.%m.%Y %H:%M:%S")
        try:
            status = request.params['status']
        except KeyError:
            raise StopProcessing(500, "No status given.")
        try:
            t=Tweets(self.db_connection)
            t.createTweet(status, request.session['user'])
        except TweetError:
            raise StopProcessing(500, "Database error. Try again later.")

        redir = "/?message={}".format(quote("Great! Now the world knows."))
        if 'ajax' in request.params:
            redir += "&ajax=1"
        response.send_redirect(redir)

    def logout(self, request, response, pathmatch):
        """Logout user and show a success message."""
        if request.session:
            request.session.destroy()
        response.send_redirect("/?message=Successfully logged out.")

    def login(self, request, response, pathmatch):
        """Shoow login form if necessary or check provided credentials."""
        if 'user' in request.session:  # already logged in
            return response.send_redirect("/")
        if '_username' in request.params and '_password' in request.params:
            users = server.usermodel.Users(self.db_connection)
            user = users.login(request.params['_username'], request.params['_password'])
            if user:
                request.session['user'] = user  # save user to session
                return response.send_redirect("/?message=Successfully logged in as {}.".format(request.params['_username']))
            else:
                return response.send_template('login.tmpl', {'message': 'Wrong username or password. Try again.'})
        # send login form
        return response.send_template('login.tmpl',{'user': server.usermodel.AnonymousUser()})


if __name__ == '__main__':

    db = sqlite.connect('minitwitter.sqlite')  # use sqlite db
    db.row_factory = sqlite.Row  # fetch rows as Row objects (easier to access)

    s = Webserver()
    s.set_templating("jinja2")
    s.set_templating_path("templates.jinja2")

    s.add_middleware(SessionMiddleware())
    s.add_middleware(CsrfMiddleware())

    s.add_app(UsermanagementApp(db_connection=db))   # Sub-App: create, change, delete users. (code in server/apps)
    s.add_app(StaticApp(prefix='static', path='static'))  # deliver static files

    s.add_app(MiniTwitterApp('data', db_connection=db))  # the twitter app

    log(0, "Server running.")
    s.serve()
