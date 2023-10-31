import socketserver
import sys
from util.request import Request
import pymongo
import bcrypt
from pymongo import MongoClient
from random import randint
mongo_client = MongoClient("mongo")
db = mongo_client["cse312"]
chat = db["chat-history"]
logins = db["user-info"]
import json
import html
import secrets
import hashlib
import io

guid = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

class Handle(Request):

    def sendIndex(request):
        retrieveFilename = None
        filename = None
        index = None
        
        if "auth" in request.cookies:
            retrieveFilename = logins.find_one({"auth":hashlib.sha256(request.cookies["auth"].encode()).digest()})
        
        if retrieveFilename != None and len(retrieveFilename["profile"]):
            print("cookie exists")
            filename = retrieveFilename["profile"]
            print("profile pic")
        else:
            filename = "/public/image/eagle.jpg"
            print("eagle")
        
        with open("public/index copy.html", 'r') as file:
            index = file.read()
            print("retrieve read index")
            index = index.replace("{{image_filename}}", filename)
                
            with open("public/index.html", 'w') as file:
                file.write(index)
                print("retrieve written")

            print("display profile")
                
        response = request.http_version + " 200 OK" + "\r\n"
        response += "Content-Type: text/html; charset=utf-8" + "\r\n"
        response += "Content-Length: "
        index = open("public/index.html", 'r')
        index = index.read().encode()
        response += str(len(index))
        response += "\r\nX-Content-Type-Options: nosniff\r\n\r\n"
        response = response.encode('utf-8')
        response += index
        return response

    def serveStyle(request):
        response = request.http_version + " 200 OK" + "\r\n"
        response += "Content-Type: text/css; charset=utf-8" + "\r\n"
        response += "Content-Length: "
        css = open("public/style.css", 'r')
        css = css.read().encode('utf-8')
        response += str(len(css))
        response += "\r\nX-Content-Type-Options: nosniff\r\n\r\n"
        response = response.encode('utf-8')
        response += css
        return response
        
    def serveJS(request):
        response = request.http_version + " 200 OK" + "\r\n"
        response += "Content-Type: text/javascript; charset=utf-8" + "\r\n"
        response += "Content-Length: "
        js = open(request.path[1:len(request.path)], 'r')
        js = js.read().encode('utf-8')
        response += str(len(js))
        response += "\r\nX-Content-Type-Options: nosniff\r\n\r\n"
        response = response.encode('utf-8')
        response += js
        return response

    def serveImage(request):
        response = request.http_version + " 200 OK" + "\r\n"
        
        if ".png" in request.path:
            response += "Content-Type: image/png" + "\r\n"
        elif ".jpg" in request.path or ".jpeg" in request.path:
            response += "Content-Type: image/jpeg" + "\r\n"
        
        response += "Content-Length: "
        img = open(request.path[1:len(request.path)], 'rb')
        img = img.read()
        response += (str(len(img)))
        response += ("\r\nX-Content-Type-Options: nosniff\r\n\r\n")
        response = response.encode('utf-8')
        response += img
        return response
        
    def visitCounter(request):
        response = request.http_version + " 200 OK" + "\r\n"
        response += "Content-Type: text/html; charset=utf-8" + "\r\n"
                
        if "visits" in request.cookies:
            request.cookies["visits"] = int(request.cookies["visits"]) + 1
            response += "Set-Cookie: " + "visits=" + str(request.cookies["visits"]) + "; Max-Age=3600" + "\r\n"
        else:
            response += "Set-Cookie: " + "visits=" + str(1) + "; Max-Age=3600" + "\r\n"
                    
        visit = open("public/visits.html", 'r')
        visit = visit.read().encode()
        response += "Content-Length: "
        response += str(len(visit)) + "\r\n"
        response += "X-Content-Type-Options: nosniff\r\n\r\n"
                
        response = response.encode('utf-8')
        response += visit
        # print("headers: " + str(request.headers))
        
        return response
        
    def chatMessage(request):
        mes = request.body.decode().split(":", 1)[1]
        mes = mes[::-1]
        mes = mes.replace("}", "", 1)
        mes = mes[::-1]
        mes = html.escape(mes)
                
        if "auth" in request.cookies and logins.find_one({"auth":hashlib.sha256(request.cookies["auth"].encode()).digest()}) != None:
            username = logins.find_one({"auth":hashlib.sha256(request.cookies["auth"].encode()).digest()})["username"]
            # print("username is ", username)
            chat.insert_one({"username": username, "message": mes, "id": str(randint(1000000, 9999999))})
        elif "auth" not in request.cookies:
            chat.insert_one({"username": "guest", "message": mes, "id": str(randint(1000000, 9999999))})
                
        response = request.http_version + " 200 OK" + "\r\n"
        response += "Content-Type: text/plain; charset=utf-8" + "\r\n"
                    
        txt = "received"
        txt = txt.encode()
        response += "Content-Length: "
        response += str(len(txt)) + "\r\n"
        response += "X-Content-Type-Options: nosniff\r\n\r\n"
                
        response = response.encode('utf-8')
        response += txt
                
        # print("headers: " + str(request.headers))
        
        return response
        
    def chatHistory(request):
        messages = list(chat.find({}))
        for i in messages:
            del i["_id"]
                
        messages = json.dumps(messages).encode()
                
        response = request.http_version + " 200 OK" + "\r\n"
        response += "Content-Type: text/plain; charset=utf-8" + "\r\n"

        response += "Content-Length: "
        response += str(len(messages)) + "\r\n"
        response += "X-Content-Type-Options: nosniff\r\n\r\n"
                
        response = response.encode('utf-8')
                
        response += messages
                
        # print("headers: " + str(request.headers))
        
        return response
        
    def register(request):
        #username_reg=username&password_reg=password
        body = (request.body).decode().split("&", 1)
        username = body[0].split("=", 1)[1]
                
        password = body[1].split("=", 1)[1]
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)
                
        logins.insert_one({"username": username, "salt":salt, "password": hashed, "auth": "", "profile": ""})
                
        response = request.http_version + " 301 Moved Permanently" + "\r\n"

        response += "Content-Length: "
        response += str(0) + "\r\n"
        response += "Location: /\r\n"
        response += "X-Content-Type-Options: nosniff\r\n\r\n"
                
        response = response.encode('utf-8')
                
        # print("logins: ", list(logins.find({})))
        
        return response
        
    def login(request):
        response = request.http_version + " 301 Moved Permanently" + "\r\n"
                
        # When a user sends a login request, authenticate the request based on the data stored 
        # in your database. If the [salted hash of the] password matches what you have stored in
        # the database, the user is authenticated.

        # When a user successfully logs in, set an authentication token as a cookie for that user
        # with the HttpOnly directive set. These tokens should be random values that are associated
        # with the user. You must store a hash (no salt) of each token in your database so you can
        # verify them on subsequent requests.

        # The auth token cookie must have an expiration time of 1 hour or longer. 
        # It cannot be a session cookie.

        # Whenever a chat message is sent by an authenticated user, the message should contain their 
        # username instead of "Guest".
                
        # username_login=username&password_login=password
        body = (request.body).decode().split("&", 1)
        username = body[0].split("=", 1)[1]
        password = body[1].split("=", 1)[1]
                
        auth = secrets.token_hex(10)
        
        
                
        for i in list(logins.find({})):
            if i["username"] == username and i["password"] == bcrypt.hashpw(password.encode(), i["salt"]):
                hashedAuth = hashlib.sha256(auth.encode()).digest()
                # print("auth: ", auth)
                # print("hashed auth: ", hashedAuth)
                logins.update_one({"username": username}, {"$set": {"auth": hashedAuth}})
                        
                request.cookies["auth"] = hashedAuth
                response += "Set-Cookie: " + "auth=" + auth + "; Max-Age=3600; HttpOnly" + "\r\n"
                
        response += "Content-Length: "
        response += str(0) + "\r\n"
        response += "Location: / \r\n"
        response += "X-Content-Type-Options: nosniff\r\n\r\n"
                
        response = response.encode('utf-8')
                
        # print("logins: ", list(logins.find({})))
        
        return response
    
    def verifyAuth(mesID, request):
        checkID = None
        checkUser = None
        checkAuth = None
        auth = None
        
        if chat.find_one({"id":mesID}) != None:
            checkID = chat.find_one({"id":mesID})
            checkUser = checkID["username"]
            # print("checkDelete: ", checkDelete)
            # print("checkUser: ", checkUser)
            if logins.find_one({"username": checkUser}) != None and "auth" in request.cookies:
                auth = hashlib.sha256(request.cookies["auth"].encode()).digest()
                checkAuth = logins.find_one({"username": checkUser})
                # print("checkAuth: ", checkAuth)
                
        return checkAuth, auth
        
    def deleteMessage(request):
        mesID = request.path.split("/")[2]
        # print("mesID: ", mesID)
                
        checkAuth = None
        auth = None
        
        checkAuth, auth = Handle.verifyAuth(mesID, request)
                
        if auth != None and checkAuth != None and auth == checkAuth["auth"]:
            chat.delete_one({"id": mesID})
            # print("deleted")
            response = request.http_version + " 200 OK" + "\r\n"
        else:
            response = request.http_version + " 403 Forbidden" + "\r\n"
                    
        response += "X-Content-Type-Options: nosniff\r\n\r\n"
        response = response.encode('utf-8')
        
        return response
        
    def sendFavicon(request):
        response = request.http_version + " 200 OK" + "\r\n"
        response += "Content-Type: image/png" + "\r\n"
        response += "Content-Length: "
        img = open("public/image/flame.png", 'rb')
        img = img.read()
        response += (str(len(img)))
        response += ("\r\nX-Content-Type-Options: nosniff\r\n\r\n")
        response = response.encode('utf-8')
        response += img
        
        return response
    
    def verifyLoggedIn(request):
        if "auth" in request.cookies and logins.find_one({"auth":hashlib.sha256(request.cookies["auth"].encode()).digest()}) != None:
            return True
        elif "auth" not in request.cookies:
            return False
        
    def extractFilename(request):
        values = request.multiHeaders[b'Content-Disposition'].split(b';')
        for i in values:
            if b'filename=' in i:
                return i.split(b'=')[1]
        return ""
    
    def extractFormat(request):
        values = request.multiHeaders[b'Content-Type'].split(b'/')
        return b'.' + values[1]
    
    def profile(request):
        
        if Handle.verifyLoggedIn(request) == True:
            img = io.BytesIO(request.imageBytes).read()
            filename = (Handle.extractFilename(request)).decode().replace("/", "")
            filename = "/public/image/" + filename[1:len(filename)-1]
            filename = filename[1:len(filename)]
            print("writing file: ", filename)
            with open(filename, "wb") as img_file:
                img_file.write(img)
            
            storeFilename = logins.find_one({"auth":hashlib.sha256(request.cookies["auth"].encode()).digest()})
            logins.update_one({"auth": storeFilename["auth"]}, {"$set": {"profile": filename}})
        
        response = request.http_version + " 302 Redirect" + "\r\n"
        response += "Content-Length: "
        response += str(0) + "\r\n"
        response += "Location: / \r\n"
        response += "X-Content-Type-Options: nosniff\r\n\r\n"
        response = response.encode()
        
        # print("logins: ", logins.find_one({"auth":hashlib.sha256(request.cookies["auth"].encode()).digest()}))
        
        return response
    
    def websocket(request):
        
        key = request.headers['Sec-WebSocket-Key'] + guid
        hashed = hashlib.sha256(key.encode()).digest()
        
        response = request.http_version + " 101 Switching Protocols" + "\r\n"
        response += "Connection: Upgrade" + "\r\n"
        response += "Upgrade: websocket" + "\r\n"
        response += "Sec-WebSocket-Accept: "
        response = response.encode()
        response += hashed + b'\r\n\r\n'
        
        if Handle.verifyLoggedIn(request) == True:
            print("authenticated")
        
        print("response: ", response)
        
        return response

    def handleResponse(request):
        
        response = request.http_version + "404 Not Found" + "\r\n"
        response += "Content-Type: text/html; charset=utf-8" + "\r\n"
        response += "Content-Length: "
        error = open("public/404.html", 'r')
        error = error.read().encode()
        response += str(len(error))
        response += "\r\nX-Content-Type-Options: nosniff\r\n\r\n"
        response = response.encode('utf-8')
        response += error
            
        if request.path == "/":
            response = Handle.sendIndex(request)
        elif ".css" in request.path:
            response = Handle.serveStyle(request)
        elif ".js" in request.path:
            response = Handle.serveJS(request)
        elif ".png" in request.path or ".jpg" in request.path or ".jpeg" in request.path:
            response = Handle.serveImage(request)
        elif ".ico" in request.path:
            response = Handle.sendFavicon(request)
        elif "/visit-counter" in request.path:
            response = Handle.visitCounter(request)
        elif "/chat-message" in request.path and request.method == "POST":
            response = Handle.chatMessage(request)
        elif "/chat-history" in request.path and request.method == "GET":
            response = Handle.chatHistory(request)
        elif "/register" in request.path and request.method == "POST":
            response = Handle.register(request)
        elif "/login" in request.path and request.method == "POST":
            response = Handle.login(request)
        elif "DELETE" in request.method:
            response = Handle.deleteMessage(request)
        elif "/profile-pic" in request.path and request.method == "POST":
            response = Handle.profile(request)
        elif "/websocket" in request.path:
            response = Handle.websocket(request)

        return response