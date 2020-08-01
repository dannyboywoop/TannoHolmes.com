"""Module containing a class used to generate a valid HTTP response."""
from .HTTP_STATUS_CODES import HTTP_STATUS_CODES


class HTTPResponse:
    """Class to generate a valid HTTP response."""

    HTTP_VERSION = "HTTP/1.1"

    def __init__(self, status_code, content, content_type="text/html"):
        """Initialise a HTTPResponse object.

        Args:
            status_code (int): The HTTP status code of the response.
            content (string or byte string): The body of the HTTP response.
            content_type (string): The MIME type of the content.
                Default is "text/html".
        """
        if status_code not in HTTP_STATUS_CODES:
            raise Exception("Unknown status code.")

        self.status_code = status_code

        # encode content to bytes, if it is a string.
        if isinstance(content, str):
            self.content = content.encode("utf-8")
        else:
            self.content = content

        # populate default headers.
        self.headers = {
            "Content-Type": content_type,
            "Content-Length": str(len(content))
        }

    def add_header(self, field, value):
        """Add a header field to the header of the HTTPResponse.

        Args:
            field (string): The field name.
            value (string): The value of the field.
        """
        self.headers[field] = value

    def create_http_response(self):
        """Generate a valid HTTP response from a HTTPResponse object.

        Returns:
            byte string: A valid HTTP response.
        """
        # create response line
        response = "{0} {1} {2}\r\n"
        response = response.format(self.HTTP_VERSION,
                                   self.status_code,
                                   HTTP_STATUS_CODES[self.status_code])

        # add headers
        for header_field, header_value in self.headers.items():
            response += "{0}: {1}\r\n".format(header_field, header_value)

        # add end-of-header line and encode to utf-8
        response += "\r\n"
        response = response.encode("utf-8")

        # add content, if there is any
        if self.content is not None:
            response += self.content

        # encode and return
        return response
