import socketserver
import sys
from util.request import Request
from util.handle import Handle
import pymongo
import bcrypt
from pymongo import MongoClient
from random import randint
# mongo_client = MongoClient("mongo")
# db = mongo_client["cse312"]
# chat = db["chat-history"]
# logins = db["user-info"]
import json
import html
import secrets
import hashlib

class MyTCPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        received_data = self.request.recv(2048)
        request = Request(received_data)
        if request.path == "/websocket":
            print(self.client_address)
            print("--- received data ---")
            print(received_data)
            print("--- end of data ---\n\n")
            
        headers = [{}]
        values = []
        path = "/visit-counter"
        visits = 0
        i = 0
        
        # TODO: Parse the HTTP request and use self.request.sendall(response) to send your response
        
        # check the path to determine what is sent in the response
        # if .contains .html, send index
        # if .contains .css, send css
        # if .png or .jpg, send img
        # anything else, error 404
        # ex: HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 5\r\n\r\nhello
        
        # print("request.path: " + request.path)
        
        response = Handle.handleResponse(request)
        
        # print("response: ", response)
        
        self.request.sendall(response)


def main():
    host = "0.0.0.0"
    port = 8080

    socketserver.TCPServer.allow_reuse_address = True

    server = socketserver.TCPServer((host, port), MyTCPHandler)

    print("Listening on port " + str(port))
    sys.stdout.flush()
    sys.stderr.flush()

    server.serve_forever()


if __name__ == "__main__":
    main()
