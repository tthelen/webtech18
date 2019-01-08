# server.py
#   Using Python's builtin simple http server
#
# Web-Technologien
# Tobias Thelen, 2017
# Public Domain
#
# Code from

import http.server, socketserver
import os

httpd = socketserver.TCPServer(("127.0.0.1", 8080), http.server.SimpleHTTPRequestHandler)
print("serving directory 'htdocs' at http://localhost:8080")
os.chdir('htdocs')
httpd.serve_forever()
