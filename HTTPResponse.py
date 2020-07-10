class HTTPResponse:

    HTTP_VERSION = "HTTP/1.1"

    STATUS_PHRASES = {
        200: "OK",
        400: "Bad Request",
        404: "Not Found",
        500: "Internal Server Error",
        501: "Not Implemented",
    }

    def __init__(self, status_code, content, content_type="text/html"):
        self.status_code = status_code
        self.content = content
        self.headers = {
            "Content-Type": content_type,
            "Content-Length": str(len(content))
        }

    def add_header(self, field, value):
        self.headers[field] = value

    def create_http_response(self):
        # create response line
        response = "{0} {1} {2}\r\n"
        response = response.format(self.HTTP_VERSION,
                                   self.status_code,
                                   self.STATUS_PHRASES[self.status_code])

        # add headers
        for header_field, header_value in self.headers.items():
            response += "{0}: {1}\r\n".format(header_field, header_value)

        # add end-of-header line
        response += "\r\n"

        # add content, if there is any
        if self.content is not None:
            response += self.content

        # encode and return
        return response.encode("utf-8")
