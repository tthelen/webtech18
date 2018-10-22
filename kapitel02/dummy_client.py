import socket

host = "www.informatik.uni-osnabrueck.de"
port = 80
path = "/institut_fuer_informatik.html"

c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create TCP socket

c.connect((host, port))  # try to connect to remote host/port
f = c.makefile(mode='rw', buffering=1)  # create file-like access to connection

f.write("GET {} HTTP/1.1\n".format(path))  # send request line
f.write("Host: {}\n".format(host))  # send request headers
f.write("Connection: Close\n")
f.write("\n")

while 1:  # read entire response and print it line for line
    resp = f.readline()  # readline will return empty string on end of file
    if resp == "":
        break
    print(resp[:-1])  # omit \n (print adds own \n)

c.close()  # done
print("\nDone.")
