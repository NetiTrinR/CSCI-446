#!/usr/bin/python3

import sys;
import HTTPServer;

class Server (SimpleHTTPRequestHandler):

    def __init__(self, file):
        self.board = [[c for c in line[0:10]] for line in file];
        self.C = 5;
        self.B = 4;
        self.R = 3;
        self.S = 3;
        self.D = 2;
        self.protocol_version = "HTTP/1.1";

    def do_GET():
        print("totes html");

    def do_POST():
        print("Something else");

    def check(x, y):
        return board[x][y];

if __name__ == '__main__':

    if(sys.argv[1:]):
        port = argv[1]
    else:
        port = 5000;

    if(sys.argv[2:]):
        filename = argv[2];
    else:
        filename = "board.txt";

    # Open the file
    file = open(filename, "r");

    # Instanciate our server
    server = Server(file);

    # Close the file
    file.close();

    # Create server address tuple
    address = ('', port);

    # Pass in the server handler and the address
    httpd = HTTPServer(address, server);

    # Lets say something
    sa = httpd.socket.getsockname();
    print("Serving HTTP on", sa[0], "port", sa[1], "...");

    # Serve it forever
    httpd.serve_forever();
