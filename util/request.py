class Request:

    def __init__(self, request: bytes):
        # TODO: parse the bytes of the request and populate the following instance variables
        self.body = request.split(b'\r\n\r\n', 1)
        self.value = self.body[0].decode().split('\r\n')
        self.method = ""
        self.path = ""
        self.http_version = ""
        self.headers = {}
        self.cookies = {}
        self.temp = ""
        self.length = 0
        self.boundary = b''
        self.multi = []
        self.multiBounds = []
        self.multiHeadersSplit = []
        self.multiHeaders = {}
        self.imageBytes = b''
        
        # print("here is the value")
        # print(self.value)
        
        self.temp = self.value[0].split()
        # print("self method")
        if len(self.temp) > 0:
            self.method = self.temp[0]
            # print(self.method)
            self.path = self.temp[1]
            self.http_version = self.temp[2]
        
        for i in range(1, len(self.value)):
            # self.temp = self.value[i].replace(":", "")
            self.temp = self.value[i].split(":", 1)
            # print("here is self.temp: ")
            # print(self.temp)
            self.headers[self.temp[0].strip()] = self.temp[1].strip()
            # print("here are the headers: ")
            # print(self.headers)
        
        if "Cookie" in self.headers:
            cookieValues = self.headers["Cookie"].split(";", 1)
            for i in cookieValues:
                temp = i.split("=", 1)
                self.cookies[temp[0].strip()] = temp[1]
        
        if "Content-Length" in self.headers:
            # print("there is a content length")
            self.length = int(self.headers["Content-Length"])
            if len(self.body) > 1:
                self.body = self.body[1]
                self.body = self.body[0:self.length]
                
        if "Content-Type" in self.headers and "multipart/form-data" in self.headers["Content-Type"]:
            self.boundary = self.headers["Content-Type"].encode().split(b';')[1]
            self.boundary = self.boundary.split(b'=')[1]
            self.multi = self.body.split(self.boundary)
            print("self.multi", self.multi)
            for i in self.multi:
                self.multiBounds += i.split(b'\r\n\r\n')
            print("self.multiBounds", self.multiBounds)
            self.imageBytes = self.multiBounds[2]
            
            for i in self.multiBounds:
                self.multiHeadersSplit += i.split(b'\r\n')
            print("self.multiHeadersSplit", self.multiHeadersSplit)
            
            for i in self.multiHeadersSplit:
                if b':' in i:
                    self.temp = i.split(b':')
                    self.multiHeaders[self.temp[0]] = self.temp[1]
            print("self.multiHeaders", self.multiHeaders)
        
            print("imageBytes: ", self.imageBytes)
            
            
        
        # print("length is: ", self.length)
        # print("self headers: ", self.headers)
        print("cookies: ", self.cookies)

        # print("end.")
