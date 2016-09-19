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
        html = template.render(self.board="board")

        # Format html string to utf8 and send
        self.wfile.write(bytes(html, "utf8"))
        return

    def do_POST(self):
        content_length = int(self.headers.getHeader('content-length', 0))
        content = self.rfile.read(content_length)
        print content

        return # Remove this

        # Spot is not on the board
        if(x < 0 || x > 10 || y < 0 || y > 10)
            SimpleHTTPRequestHandler.http_error(404)
            return

        value = check(x, y)
        hit_flag = false
        if(value = "X"):
            print("Already guessed this spot")
            SimpleHTTPRequestHandler.http_error(410)
            return
        else if(value = "~"):
            print("Miss!")
        else
            hit_flag = true
            print("Hit!")
            if(value = "C"):
                self.C -= 1
            if(value = "B"):
                self.B -= 1
            else if(value = "D")
                self.D -= 1
            else if(value = "R"):
                self.R -= 1
            else if(value = "S"):
                self.S -= 1
            else if(value = "R"):
                self.R -= 1
        self.board[y][x] = "X"

    def check(self, x, y):
        return self.board[x][y]


if __name__ == '__main__':

    if(sys.argv[1:]):
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
    address = ('128.111.52.245', 5000)

    # Pass in the server handler and the address
    httpd = HTTPServer(address, server)

    # Lets say something
    sa = httpd.socket.getsockname()
    print("Serving HTTP on", sa[0], "port", sa[1], "...")

    # Serve it forever
    httpd.serve_forever()
