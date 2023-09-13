import socketserver
import sys
from util.request import Request

class MyTCPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        received_data = self.request.recv(2048)
        print(self.client_address)
        print("--- received data ---")
        print(received_data)
        print("--- end of data ---\n\n")
        request = Request(received_data)
        headers = {}
        values = []
        path = "/visit-counter"
        visits = 0
            
        
        # TODO: Parse the HTTP request and use self.request.sendall(response) to send your response
        
        # check the path to determine what is sent in the response
        # if .contains .html, send index
        # if .contains .css, send css
        # if .png or .jpg, send img
        # anything else, error 404
        # ex: HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 5\r\n\r\nhello
        
        print("request.path: " + request.path)
        
        response = request.http_version + "404 Not Found" + "\r\n"
        response += "Content-Type: text/plain; charset=utf-8" + "\r\n"
        response += "Content-Length: "
        txt = "The requested content does not exist"
        txt = txt.encode('utf-8')
        response += str(len(txt))
        response += "\r\nX-Content-Type-Options: nosniff\r\n\r\n"
        response = response.encode('utf-8')
        response += txt
        
        if request.path == "/":
            response = request.http_version + " 200 OK" + "\r\n"
            response += "Content-Type: text/html; charset=utf-8" + "\r\n"
            response += "Content-Length: "
            index = open("public/index.html", 'r')
            index = index.read().encode()
            response += str(len(index))
            response += "\r\nX-Content-Type-Options: nosniff\r\n\r\n"
            response = response.encode('utf-8')
            response += index
        elif ".css" in request.path:
            response = request.http_version + " 200 OK" + "\r\n"
            response += "Content-Type: text/css; charset=utf-8" + "\r\n"
            response += "Content-Length: "
            css = open("public/style.css", 'r')
            css = css.read().encode('utf-8')
            response += str(len(css))
            response += "\r\nX-Content-Type-Options: nosniff\r\n\r\n"
            response = response.encode('utf-8')
            response += css
        elif ".js" in request.path:
            response = request.http_version + " 200 OK" + "\r\n"
            response += "Content-Type: text/javascript; charset=utf-8" + "\r\n"
            response += "Content-Length: "
            js = open(request.path[1:len(request.path)], 'r')
            js = js.read().encode('utf-8')
            response += str(len(js))
            response += "\r\nX-Content-Type-Options: nosniff\r\n\r\n"
            response = response.encode('utf-8')
            response += js
        elif ".png" in request.path:
            response = request.http_version + " 200 OK" + "\r\n"
            response += "Content-Type: image/png" + "\r\n"
            response += "Content-Length: "
            img = open(request.path[1:len(request.path)], 'rb')
            img = img.read()
            response += (str(len(img)))
            response += ("\r\nX-Content-Type-Options: nosniff\r\n\r\n")
            response = response.encode('utf-8')
            response += img
        elif ".jpg" in request.path or ".jpeg" in request.path:
            response = request.http_version + " 200 OK" + "\r\n"
            response += "Content-Type: image/jpeg" + "\r\n"
            response += "Content-Length: "
            img = open(request.path[1:len(request.path)],'rb')
            img = img.read()
            response += (str(len(img)))
            response += ("\r\nX-Content-Type-Options: nosniff\r\n\r\n")
            response = response.encode('utf-8')
            response += img
        elif path in request.path:
            response = request.http_version + " 200 OK" + "\r\n"
            response += "Content-Type: text/plain; charset=utf-8" + "\r\n"
            
            # iterate through keys in the headers, looking for "Set-Cookie"
            # break up client Set-Cookie values
            for key in request.headers:
                if key == "Cookie":
                    values = request.headers[key].split(";")
        
            # if this cookie deals with visits && path == request.path, increment by 1
            for i in values:
                if "visits=" in i:
                    temp = i.split("=")
                    visits = int(temp[1]) + 1
                    headers["Set-Cookie"] = "visits=" + str(visits)
                    response += "Set-Cookie: " + "visits=" + str(visits) + "; Max-Age: 3600" + "\r\n"
                else:
                    headers["Set-Cookie"] = i
                    response += "Set-Cookie: " + str(i) + "; Max-Age: 3600" + "\r\n\r\n"
                        
        
            if "Cookie" not in request.headers and request.path == path:
                headers["Set-Cookie"] = "visits=" + str(1)
                response += "Set-Cookie: " + "visits=" + str(visits) + "; Max-Age: 3600" + "\r\n"
                
            txt = "Times visited: " + str(visits)
            response += "Content-Length: "
            response += str(len(txt)) + "\r\n"
            response += "X-Content-Type-Options: nosniff\r\n\r\n"
            
            response = response.encode('utf-8')
            response += txt.encode('utf-8')
            print("headers: " + str(request.headers))
        
        elif ".ico" in request.path:
            response = request.http_version + " 200 OK" + "\r\n"
            response += "Content-Type: image/png" + "\r\n"
            response += "Content-Length: "
            img = open("public/image/tv.png", 'rb')
            img = img.read()
            response += (str(len(img)))
            response += ("\r\nX-Content-Type-Options: nosniff\r\n\r\n")
            response = response.encode('utf-8')
            response += img
        
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
