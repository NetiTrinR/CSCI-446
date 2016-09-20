#!/usr/bin/python3

import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from jinja2 import Template
import urllib
import re

class Handler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()

    def do_GET(self):
        # Set response code
        self.send_response(200)
        # Headers
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        # Create template from html
        htmlFile = open("index.html", "r")
        template = Template(htmlFile.read())
        htmlFile.close()

        # Render Html from template
        html = template.render(board=self.server.board)

        # Format html string to utf8
        self.wfile.write(bytes(html, "utf8"))
        return


    def do_POST(self):
        content_length = int(self.headers.get_all('content-length')[0])
        content = self.rfile.read(content_length)
        content = content.decode("utf-8")
        print("post: "+str(content))
        # parse x and y
        string = content.split("&")
        coor = {}
        try:
            for each in string:
                each = each.split("=")
                coor[each[0]] = int(each[1])
        except:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            return         
        
        x = coor["x"]
        y = coor["y"]
        # return # Remove this

        # Spot is not on the board
        if(x < 0 or x > 10 or y < 0 or y > 10):
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            return

        value = self.server.board[y][x]
        hit_flag = False
        html = ""
        if(value == "X" or value == "H"):
            print("Already guessed this spot")
            self.send_response(410)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            return
        elif(value == "_"):
            print("Miss!")
            html = html + "hit=0"
        else:
            hit_flag = True
            print("Hit!")
            html = html + "hit=1"
            if(value == "C"):
                self.server.C -= 1
                if self.server.C == 0:
                    html = html + "&sink=C"
            elif(value == "B"):
                self.server.B -= 1
                if self.server.B == 0:
                    html = html + "&sink=B"
            elif(value == "D"):
                self.server.D -= 1
                if self.server.D == 0:
                    html = html + "&sink=D"
            elif(value == "R"):
                self.server.R -= 1
                if self.server.R == 0:
                    html = html + "&sink=R"
            elif(value == "S"):
                self.server.S -= 1
                if self.server.S == 0:
                    html = html + "&sink=S"
        if hit_flag == True:
            self.server.board[y][x] = "H"
        else:
            self.server.board[y][x] = "X"

        # Set response code
        self.send_response(200)
        # Headers
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        # Format html string to utf8
        self.wfile.write(bytes(html, "utf8"))
        return
        # If miss, reply miss
        # If hit, check if sunk, reply sunk with ship
        # Else if hit, reply hit



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
