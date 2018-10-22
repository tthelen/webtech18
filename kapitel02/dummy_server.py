import socket
c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket vorbereiten
c.bind(('localhost', 8080))  # an Port 8080 binden
c.listen(1)  # auf hereinkommende Verbindungen lauschen

while 1:
    csock, caddr = c.accept()
    conn = csock.makefile(mode='rw', buffering=1, errors='ignore')

    # Read request
    request_line = conn.readline().strip()
    method, resource, protocol = request_line.split(" ")
    print("Request: %s %s %s" % (method, resource, protocol))
    while True:
        header_line = conn.readline().strip()
        if not header_line:
            break
        (headerfield, headervalue) = header_line.split(":", 1)
        print("Header: %s: %s" % (headerfield.strip(), headervalue.strip()))

    # Write response
    conn.write("HTTP/1.1 200 OK\n")
    import datetime
    conn.write("Date: %s\n" % datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"))
    conn.write("Content-Type: text/html\n")
    conn.write("Connection: close\n")
    conn.write("\n")  # extra leerzeile schliesst header ab

    conn.write("""
        <html>
            <head>
            <title>Dummy Webserver Info</title>
            </head>
        <body>
            <h1>Dummy Webserver Info</h1>
            <p>Der Webserver l&auml;uft auf Host %s und Port %s.</p>
        </body>
    """ % ('localhost', 8080))

    conn.close()
    csock.close()




