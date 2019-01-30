__author__ = 'Tobias Thelen'

from server.log import log
from server.webserver import App, StopProcessing
import server.usermodel
from urllib.parse import quote


class UsermanagementApp(App):
    """Provide a very simple user management interface for admins."""

    def __init__(self, useradmin_template='usermanagement.tmpl', db_connection=None, **kwargs):
        """StaticApp constructor.

        :param:path File system path to server files from.
        :return: nothing
        """

        self.users = server.usermodel.Users(db_connection)
        self.useradmin_template = useradmin_template
        super().__init__(**kwargs)

    def register_routes(self):
        """Register the user admin routes on server."""
        self.add_route(r'useradmin', self.show)
        self.add_route(r'useradmin/create', self.create)
        self.add_route(r'useradmin/delete/(?P<username>.*)', self.delete)

    def show(self, request, response, pathmatch):
        """List users and creation form."""

        if 'user' not in request.session:
            raise StopProcessing(400, "You need to be logged in.")

        if not request.session['user'].is_admin:
            raise StopProcessing(400, "You are not an admin!")

        d = {
            'user': request.session['user'], # that's the current user
            'userlist': self.users.findUsers(),  # all users
            'message': request.params['msg'] if 'msg' in request.params else ''
        }
        response.send_template(self.useradmin_template, d)

    def delete(self, request, response, pathmatch):
        """Delete a user."""

        if 'user' not in request.session:
            raise StopProcessing(400, "You need to be logged in.")

        if not request.session['user'].is_admin:
            raise StopProcessing(400, "You are not an admin!")

        try:
            username = pathmatch.group('username')
        except IndexError:
            raise StopProcessing(400,"No username given.")

        if request.session['user'].username == username:
            response.send_redirect('/useradmin?msg={}'.format("No, no, can't delete yourself."))

        success = self.users.deleteUser(username)
        if 'ajax' in request.params:
            response.send()
        else:
            response.send_redirect('/useradmin?msg={}'.format("OK, Nutzer gelöscht." if success else "Uuups, Nutzer nicht gelöscht"))

    def create(self, request, response, pathmatch):
        """Create a new user."""

        if 'user' not in request.session:
            raise StopProcessing(400, "You need to be logged in.")

        if not request.session['user'].is_admin:
            raise StopProcessing(400, "You are not an admin!")

        try:
            username = request.params['username']
            password = request.params['password']
            role = request.params['role']
            fullname = request.params['fullname']
        except KeyError:
            response.send_redirect('/useradmin?msg={}'.format(quote('Es müssen alle Felder ausgefüllt werden!', encoding='utf-8')))
            return

        try:
            self.users.createUser(username, password, role, fullname)
        except server.usermodel.UserError as err:
            response.send_redirect('/useradmin?msg={}'.format(quote(err.msg, encoding='utf-8')))
            return

        response.send_redirect('/useradmin?msg={}'.format(quote("Ok! Nutzer %s angelegt." % (username),encoding='utf-8')))
