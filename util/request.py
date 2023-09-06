class Request:

    def __init__(self, request: bytes):
        # TODO: parse the bytes of the request and populate the following instance variables
        self.string = request.decode('utf-8')
        self.body = b""
        self.method = ""
        self.path = ""
        self.http_version = ""
        self.headers = {}
