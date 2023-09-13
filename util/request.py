class Request:

    def __init__(self, request: bytes):
        # TODO: parse the bytes of the request and populate the following instance variables
        self.value = request.decode('utf-8')
        self.value = self.value.split("\r\n")
        self.body = b""
        self.method = ""
        self.path = ""
        self.http_version = ""
        self.headers = {}
        self.temp = ""
        
        self.temp = self.value[0].split()
        # print("self method")
        if self.temp[0]:
            self.method = self.temp[0]
        # print(self.method)
        self.path = self.temp[1]
        self.http_version = self.temp[2]
        
        for i in range(1, len(self.value)-2):
            # self.temp = self.value[i].replace(":", "")
            self.temp = self.value[i].split(":")
            # print("here is self.temp: ")
            # print(self.temp)
            self.headers[self.temp[0].strip()] = self.temp[1].strip()
            # print("here are the headers: ")
            # print(self.headers)

        # print("end.")
