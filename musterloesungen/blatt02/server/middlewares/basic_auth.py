from server.log import log
from server.webserver import Middleware, AlreadyProcessed
import base64


class BasicAuthMiddleware(Middleware):
    """Apply http basic auth."""

    def __init__(self, credentials, realm=None):
        """Init middleware.

        :param credentials dictionay kay=username, value=password, {'user':'pass', 'marvin':'42'}
        :param realm string Message displayed by browser.
        """
        self.credentials = credentials  # list of tuples (username, password)
        self.realm = realm or "Please provide username and password."
        super().__init__()

    def process_request(self, request, response):
        """Get session ID from request cookies and load session."""
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization'].split()
            # Authorization header value is <Type> <Credentials>
            # We only support type "Basic"
            if len(auth_header) == 2 and auth_header[0] == 'Basic':
                cred = base64.b64decode(auth_header[1]).decode('utf-8').split(":")
                # base64 decoded string is username:password. Check form and proper credentials.
                if len(cred) == 2 and cred[0] in self.credentials and self.credentials[cred[0]] == cred[1]:
                        return  # everything is ok, just go on

        # no valid credentials given
        response.add_header('WWW-Authenticate', 'Basic realm="{}"'.format(self.realm))
        response.send(code=401, body="Not authorized.")
        raise AlreadyProcessed()
