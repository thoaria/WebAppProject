import socketserver
import sys
from util.request import Request
from util.handle import Handle
from util.websocket import HandleWebsocket
import pymongo
import bcrypt
from pymongo import MongoClient
from random import randint
# mongo_client = MongoClient("mongo")
# db = mongo_client["cse312"]
# chat = db["chat-history"]
# logins = db["user-info"]
import json, html, secrets, hashlib, base64

class MyTCPHandler(socketserver.BaseRequestHandler):
    
    thread_count = 0
    websocket_connections = set()
    guid = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    
    contentLength = None
    stored_data = bytearray()

    def handle(self):
        
        received_data = self.request.recv(2048)
        request = Request(received_data)
        self.index = 0
        response = Handle.handleResponse(request)
        
        # print(self.client_address)
        # print("--- received data ---")
        # print(received_data)
        # print("--- end of data ---\n\n")
        
        #check if path was for websocket upgrade, if so keep connecton
        
        if request.path == "/websocket":

            username = Handle.retrieveUsername(request)
                
            key = request.headers['Sec-WebSocket-Key'] + MyTCPHandler.guid
            hashed = hashlib.sha1(key.encode()).digest()
            accept = base64.b64encode(hashed)
            
            response = request.http_version + " 101 Switching Protocols" + "\r\n"
            response += "Connection: Upgrade" + "\r\n"
            response += "Upgrade: websocket" + "\r\n"
            response += "Sec-WebSocket-Accept: "
            response = response.encode()
            response += accept + b'\r\n\r\n'
            
            # print("response: ", response)
            # print("body: ", request.body)
            
            self.request.sendall(response)
            response = Handle.handleResponse(request)
            
            MyTCPHandler.websocket_connections.add(self)
            
            while True:
                # r = None
                # opcode = None
                # received_data = self.request.recv(1)
                # if len(received_data) > 0:
                #     opcode = received_data[0] & 0b00001111
                #     print("received data: ", received_data)
                #     print("opcode: ", opcode)

                # # parse data as websocket
                # # build response as websocket
                # # print("websocket_connections:", MyTCPHandler.websocket_connections)
                # if opcode == 8:
                #     MyTCPHandler.websocket_connections.remove(self)
                #     break
                r = HandleWebsocket.handleResponse(username, self)
                if r != None:
                    # print('Sending: frame: ', r)
                    self.send_message_to_all_WS_connections(r)
        
        
        # print("header:", request.headers)
        if "Content-Length" in request.headers and request.path == "/profile-pic":
            MyTCPHandler.contentLength = int(request.headers["Content-Length"])
            
            while len(MyTCPHandler.stored_data) < MyTCPHandler.contentLength:
                MyTCPHandler.stored_data += received_data
                received_data = self.request.recv(2048)
                print("data length:", len(MyTCPHandler.stored_data))
                
            print("data:", MyTCPHandler.stored_data)
            
            request = Request(bytes(MyTCPHandler.stored_data))
            MyTCPHandler.stored_data = bytearray()
            response = Handle.handleResponse(request)
            
        self.request.sendall(response)
    
    def send_message_to_all_WS_connections(self, ws_frame):
        for socket in MyTCPHandler.websocket_connections:
            socket.request.sendall(ws_frame)
        return



def main():
    host = "0.0.0.0"
    port = 8080

    socketserver.TCPServer.allow_reuse_address = True

    server = socketserver.ThreadingTCPServer((host, port), MyTCPHandler)

    print("Listening on port " + str(port))
    sys.stdout.flush()
    sys.stderr.flush()
    
    server.serve_forever()


if __name__ == "__main__":
    main()
