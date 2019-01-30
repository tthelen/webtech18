from server.webserver import Middleware, StopProcessing, Cookie
from uuid import uuid4


class CsrfMiddleware(Middleware):
    """Add a session attribute to request."""

    def process_request(self, request, response):
        """Every POST request must present a valid CSRF token."""

        if not hasattr(request, 'session'):
            raise Exception("CSRF middleware needs sessions and must be registered after session middleware.")

        if 'csrf_token' not in request.session:
            # we do have a session but not csrf token yet
            request.session['csrf_token'] = uuid4().hex  # generate random token
            request.session['csrf_input'] = "<input type=hidden name='csrf_token' value='{}'>".format(request.session['csrf_token'])

        # add csrf token as cookie
        # we do this for javascript code that needs to access the token to construct ajax post requests
        # this is not insecure because we don't check if the cookie was delivered but a parameter
        # an attacker cannot access the cookie content
        response.add_cookie(Cookie('csrf_token', request.session['csrf_token']))

        # if we have a POST request, then a proper crsf token must be present
        # this also works for login because anonymous users get a session, too
        if request.method.upper() == "POST":
            if 'csrf_token' not in request.params or request.params['csrf_token'] != request.session['csrf_token']:
                raise StopProcessing(403, "Invalid or missing CSRF token.")


