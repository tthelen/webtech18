import requests

uri = 'http://www.informatik.uni-osnabrueck.de'

r = requests.get(uri)  # send the request

# note that the request library automatically follows redirection responses
# so to access the entire request history, use the history list
for h in r.history:
    print("Request to {} got redirect with code {} to {}".format(
        h.url, h.status_code, h.headers['Location']))

print("Request to {} got answerd with code {} and content:".format(r.url, r.status_code))

# The Requests library tries to determine the character encoding
# and provides the content as utf8 via the text property
print(r.text[:200])  # first 200 characters
