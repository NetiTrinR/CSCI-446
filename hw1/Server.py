#!/usr/bin/python3

import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from jinja2 import Template


class Server (BaseHTTPRequestHandler):

    def __init__(self, file):
        self.board = [[c for c in line[0:10]] for line in file]
        self.C = 5
        self.B = 4
        self.R = 3
        self.S = 3
        self.D = 2
        self.protocol_version = "HTTP/1.1"

    def do_GET(self):
        # Response Code
        self.send_response(200)

        # Headers
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        # Create template from html
        htmlFile = open("index.html", "r")
        template = Template(htmlFile.read())
        htmlFile.close()

        # Render Html from template
        html = template.render(board="Board Data")

        # Format html string to utf8 and send
        self.wfile.write(bytes(html, "utf8"))
        return

    def do_POST(x_cord, y_cord):
        spot = check(x_cord, y_cord);
        if(spot = "~"):
            spot.set("X");
            print("Miss!");
        else if(spot = "C"):
            C -= 1;
            spot.set("X");
            print("Hit!");
        else if(spot = "B"):
            B -= 1;
            spot.set("X");
            print("Hit!");
        else if(spot = "R"):
            R -= 1;
            spot.set("X");
            print("Hit!")
        else if(spot = "B"):
            S -= 1;
            spot.set("X");
            print("Hit!");
        else if(spot = "R"):
            D -= 1;
            spot.set("X");
            print("Hit!")
        # If spot is already been guessed
        else if(spot = "X"):
            SimpleHTTPRequestHandler.http_error_410();
            print("Already guessed this spot")
        # Spot is not on the board
        else:
            SimpleHTTPRequestHandler.http_error_404();
            print("Out of Bounds")

    def check(self, x, y):
        return self.board[x][y]

    def print_board(self):
        str
        return str


if __name__ == '__main__':

    if(sys.argv[1:]):
        port = sys.argv[1]
    else:
        port = 5000

    if(sys.argv[2:]):
        filename = sys.argv[2]
    else:
        filename = "board.txt"

    # Open the file
    file = open(filename, "r")

    # Instanciate our server
    server = Server(file)

    # Close the file
    file.close()

    # Create server address tuple
    address = ('', port)

    # Pass in the server handler and the address
    httpd = HTTPServer(address, server)

    # Lets say something
    sa = httpd.socket.getsockname()
    print("Serving HTTP on", sa[0], "port", sa[1], "...")

    # Serve it forever
    httpd.serve_forever()
