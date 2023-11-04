import socketserver
import sys
from util.request import Request
from util.handle import Handle
import pymongo
import bcrypt
from pymongo import MongoClient
from random import randint
mongo_client = MongoClient("mongo")
db = mongo_client["cse312"]
chat = db["chat-history"]
logins = db["user-info"]
import json, html, secrets, hashlib, io, base64

class HandleWebsocket(Request):
    
    stored_frames = bytearray()
    leftover = bytes()
    
    def sendChatMessage(request, response, username):
        
        print("here")
        print("username:", username)
        
        payload = {'messageType':'chatMessage', 'username':username, 'message':html.escape(response['message']), 'id':str(randint(1000000, 9999999))}
        Handle.chat.insert_one({"username": username, "message": payload['message'], "id": payload['id']})
        
        payload = json.dumps(payload)
        # print("json.dumps(response):", payload)
        length = len(payload.encode())
        frame = bytearray(int.to_bytes(0b10000001, 1, 'big'))
        
        print("length:", length)
        # print("frame:", frame)
        
        if length >= 126 and length < 65536:
            print("126")
            # add maskbit (always 0) + 126 to frame
            frame += int.to_bytes(126, 1, 'big')
            
            #the next 2 bytes of the frame are set to payload length
            payloadLengthBytes = int.to_bytes(length, 2, 'big')
            print("payloadLengthBytes:", payloadLengthBytes, "is", int.from_bytes(payloadLengthBytes, 'big'))
            print("payloadLengthBytes[0]", payloadLengthBytes[1])
            print("payloadLengthBytes[1]", payloadLengthBytes[0])
            frame += payloadLengthBytes
            print("bytes:", bin(int.from_bytes(payloadLengthBytes, 'big')), "is", int.from_bytes(payloadLengthBytes, 'big'))
        elif length >= 65536:
            print("65536")
            # add maskbit (always 0) + 126 to frame
            
            #the next 2 bytes of the frame are set to payload length
            frame += int.to_bytes(127, 1, 'big')
            payloadLengthBytes = int.to_bytes(length, 8, 'big')
            frame += payloadLengthBytes
        else:
            frame += int.to_bytes(length, 1, 'big')
        
        # print("frame:", bin(int(frame.hex(), 16)))
        
        frame.extend(payload.encode())
        print("full frame:", frame)
        
        return frame
    
    def websocket(request, received_data, self):
        
        print("parse text")
        print("leftover: ", HandleWebsocket.leftover)
        
        received_data = HandleWebsocket.leftover + received_data
        payload = bytearray()
        first = received_data[0]
        fin = 0
        
        print("leftover + received_data", received_data)
        print("first:", bin(first))
        
        while fin == 0:
            fin = (first & 128) >> 7
            opcode = first & 0b00001111
            
            maskIndex = 2
            received_data += self.request.recv(1)
            second = received_data[1]
            mask = (second & 128) >> 7
            payloadLength = second & 127
            
            print("recieved_data:", received_data, ", second:", second, "mask:", mask, "payloadLength:", payloadLength)
        
            # length = received_data[1] & 127
            # maskIndex = 2
            payloadSize = payloadLength
            
            print("'length': ", payloadSize)
            
            # if length == 126:
            #     maskIndex = 4
            #     payloadSize = received_data[2:maskIndex]
            #     payloadSize = int.from_bytes(payloadSize, 'little')
            # elif length == 127: 
            #     maskIndex = 10
            #     payloadSize = received_data[2:maskIndex]
            #     payloadSize = int.from_bytes(payloadSize, 'little')
            
            if payloadLength == 126:
                maskIndex = 4
                received_data += self.request.recv(2)
                payloadLengthBytes = received_data[2:4]
                print("payloadLengthBytes:", payloadLengthBytes)
                payloadSize = int.from_bytes(payloadLengthBytes, 'big')
            elif payloadLength == 127:
                maskIndex = 10
                received_data += self.request.recv(8)
                payloadLengthBytes = received_data[2:10]
                payloadSize = int.from_bytes(payloadLengthBytes, 'big')
            
            maskEnd = maskIndex + 4
            
            received_data += self.request.recv(4)
            mask = (received_data[maskIndex:maskEnd])
            print("mask:", mask)
            
            print("payloadSize:", payloadSize)
            
            payload += received_data[maskEnd:]
            
            while len(payload) < payloadSize:
                payload += self.request.recv(2048)

            # print("payload int?", payload)

            # payload = received_data[maskEnd:]
            
            # print("stored:", HandleWebsocket.stored_frames)
            
            # while len(HandleWebsocket.stored_frames) < payloadSize:
            #     received_data = sender.request.recv(2048)
            #     HandleWebsocket.stored_frames.extend(received_data)
            #     print("stored_frames:", HandleWebsocket.stored_frames)
            #     payload = HandleWebsocket.stored_frames
            
            # first = self.request.recv(1)
            
            print("fin:", fin)
        
        HandleWebsocket.leftover = bytes(list(payload[payloadSize:]))
        
        # print("before mask: ", payload)
        payload = [payload[i] ^ mask[i % 4] for i in range(len(payload))]
        payload = bytes(payload)
        
        # print("payload:", payload)
        # print("len(payload)", len(payload))
        
        payload = payload[:payloadSize]
        
        # print("payload cut", payload)
        # print("leftover:", HandleWebsocket.leftover)
        # payload += b'"}'
        
        # print("stored_frames:", HandleWebsocket.stored_frames)
        
        response = payload.decode()
        response = json.loads(response)
        
        # print("response: ", response)
        return response
    
    def bufferFrames(request, received_data):
        
        
        
        return 

    def handleResponse(request, opcode, received_data, username, self):
        
        username = html.escape(username)
        
        # print("request.path: " + request.path)
        response = None
        payloadLength = None
        
        response = HandleWebsocket.websocket(request, received_data, self)
        
        if response != None and response['messageType'] == "chatMessage":
            response = HandleWebsocket.sendChatMessage(request, response, username)

        return response