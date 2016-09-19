#!/usr/bin/python3

import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from jinja2 import Template


class Handler (BaseHTTPRequestHandler):

    protocol_version = "HTTP/1.1"

    def do_GET(self):
        # Response Code
        self.send_response(200)

        # Headers
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        # Create template from html
        # htmlFile = open("index.html", "r")
        # template = Template(htmlFile.read())
        # htmlFile.close()

        # Render Html from template
        # html = template.render(self.board="board")
        html = "Hello world!"

        # Format html string to utf8 and send
        self.wfile.write(bytes(html, "utf8"))
        return

    def do_POST(self):
        content_length = int(self.headers.getHeader('content-length', 0))
        content = self.rfile.read(content_length)
        print(content)

        return # Remove this

        # Spot is not on the board
        if(x < 0 or x > 10 or y < 0 or y > 10):
            SimpleHTTPRequestHandler.http_error(404)
            return

        value = self.server.board[y][x]
        hit_flag = false
        if(value == "X"):
            print("Already guessed this spot")
            SimpleHTTPRequestHandler.http_error(410)
            return
        elif(value == "~"):
            print("Miss!")
        else:
            hit_flag = true
            print("Hit!")
            if(value == "C"):
                self.server.C -= 1
            elif(value == "B"):
                self.server.B -= 1
            elif(value == "D"):
                self.server.D -= 1
            elif(value == "R"):
                self.server.R -= 1
            elif(value == "S"):
                self.server.S -= 1
            elif(value == "R"):
                self.server.R -= 1
        self.server.board[y][x] = "X"


class Server (HTTPServer):
    def __init__(self, file, server_address):
        self.C = 5
        self.B = 4
        self.R = 3
        self.S = 3
        self.D = 2
        self.board = [[c for c in line[0:10]] for line in file]
        HTTPServer.__init__(self, server_address=server_address, RequestHandlerClass=Handler)


if __name__ == '__main__':

    if(sys.argv[1:]):
        filename = sys.argv[2]
    else:
        filename = "board.txt"

    # Create server address tuple
    # address = ("128.111.52.245", 5000)
    address = ("127.0.0.1", 5000)

    # Open the file
    file = open(filename, "r")

    # Instanciate server
    httpd = Server(file, address)

    # Close the file
    file.close()

    # Lets say something
    sa = httpd.socket.getsockname()
    print("Serving HTTP on", sa[0], "port", sa[1], "...")

    # Serve it forever
    httpd.serve_forever()
