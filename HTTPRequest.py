from enum import Enum


class HTTPRequest:

    class HTTPMethod(Enum):
        GET = "GET"
        HEAD = "HEAD"
        POST = "POST"
        PUT = "PUT"
        DELETE = "DELETE"
        CONNECT = "CONNECT"
        OPTIONS = "OPTIONS"
        TRACE = "TRACE"
        PATCH = "PATCH"

    HTTP_METHOD_STRINGS = set(item.value for item in HTTPMethod)

    def _parse_request_line(self, request_line):
        # attempt to separate request line into 3 strings.
        request = request_line.strip().split(" ")
        if len(request) != 3:
            raise Exception("Invalid HTTP Request-Line!")
        method, self.request_uri, self.http_version = request

        # attempt to parse HTTP method.
        if method not in self.HTTP_METHOD_STRINGS:
            raise Exception("Unrecognised HTTP method!")
        self.method = self.HTTPMethod(method)

    def _parse_header(self, header_text):
        # attempt to slit header into a field-value pair.
        header = header_text.split(":", 1)
        if len(header) != 2:
            raise Exception("Invalid Header-Line!")

        # add header to headers
        field, value = header
        self.headers[field] = value.strip()

    def __init__(self, request_data):
        lines = [line.decode("utf-8") for line in request_data.splitlines()]
        self._parse_request_line(lines.pop(0))

        self.headers = {}
        self.body = ""
        end_of_headers = False
        for line in lines:
            if end_of_headers:
                self.body += line + "\n"
                continue
            if not line:
                end_of_headers = True
                continue
            self._parse_header(line)

        # check for correct header format
        if not end_of_headers:
            raise Exception("No end-of-header line found!")

    def __str__(self):
        # convert request-line
        string = "Method: {0}, URI: {1}, Version: {2}\n"
        string = string.format(self.method,
                               self.request_uri,
                               self.http_version)

        # convert headers
        for header_field, header_value in self.headers.items():
            string += "{0}: {1}\n".format(header_field, header_value)

        # convert body:
        if self.body is not None:
            string += "Body:\n{0}".format(self.body)

        return string

    def __repr__(self):
        return self.__str__()
