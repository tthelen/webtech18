import socket
c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket vorbereiten
c.bind(('localhost', 8080))  # an Port 8080 binden
c.listen(5)  # auf hereinkommende Verbindungen lauschen

while 1:
    csock, caddr = c.accept()
    conn = csock.makefile(mode='rwb', buffering=1)

    def w(txt):
        """Decode as UTF-8 and write to client connection"""
        conn.write(bytes(txt, 'UTF-8'))

    # Read request
    while 1:
        request_line = conn.readline().decode('utf-8').strip()
        if request_line.strip():
            break
    method, resource, protocol = request_line.split(" ")
    print("Request: %s %s %s" % (method, resource, protocol))
    while True:
        header_line = conn.readline().decode('utf-8').strip()
        if not header_line:
            break
        (headerfield, headervalue) = header_line.split(":", 1)

    from urllib.parse import unquote
    resource = unquote(resource)
    if ".." in resource: # some protection from directory traversal attacks
        w("HTTP/1.1 500 Internal Server Error\n\n")
        w("500 internal server error.\nDirectory traversal attack attempted.\n")
        conn.close()
        csock.close()
        continue

    try:
        f = open('static' + resource, 'rb')
    except IOError:
        w("HTTP/1.1 404 File not found\n\n")
        w("404 File not found: %s\n" % resource)
        print("Response: 404 File not Found")
    else:
        # Write response
        w("HTTP/1.1 200 OK\n")
        import datetime
        w("Date: %s\n" % datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"))

        # guess type from extension
        import mimetypes
        (content_type, encoding) = mimetypes.guess_type(resource)
        if not content_type:
            content_type = "text/plain"
        w("Connection: close\n")
        w("Content-Type: %s\n" % content_type)
        w("\n")
        print("Response: 200 OK, Content-Type: {}".format(content_type))
        conn.write(f.read())  # read and dump whole file
        f.close()

    conn.close()
    csock.close()

