"""Module used to handle and respond to HTTP requests."""
from HTTPResponse import HTTPResponse
from HTTPRequest import HTTPRequest
from os import getcwd, path


class RequestHandler:
    """Class used to create a HTTPResponse for a HTTPRequest object."""

    def generate_response(self, request):
        """Generate a HTTPResponse object in response to a HTTPRequest.

        Args:
            request (HTTPRequest): The HTTPRequest object for which a
                response is to be generated.

        Returns:
            HTTPResponse: A valid response to the request.
        """
        # call appropriate method
        return self.METHODS[request.method](self, request)

    def _handle_file(self, full_path, content_type, extension):
        """Create a response from a file.

        Args:
            full_path (string): The full path to the file.
            extension (string): The extension of the file.

        Returns:
            HTTPResponse: A HTTP response containing the file contents.
        """
        with open(full_path, "rb") as input_file:
            data = input_file.read()
        return HTTPResponse(200, data, content_type+"/"+extension[1:])

    def _find_content_path(self, uri):
        """Attempt to find a relevant file for a given URI.

        Args:
            uri (string): The URI of the file to search for.

        Returns:
            string: A path to the file, if one was found.
                Otherwise, returns None.
        """
        full_path = getcwd() + "/root/" + uri

        # check if it is a folder containing index.html
        index_path = path.join(full_path, 'index.html')
        if path.isdir(full_path) and path.isfile(index_path):
            return index_path

        # check if it is a file
        if path.isfile(full_path):
            return full_path

        # otherwise, return None
        return None

    def _do_GET(self, request):
        """Attempt to respond to a HTTP GET request.

        Args:
            request (HTTPRequest): The request to respond to.

        Returns:
            HTTPResponse: A valid HTTP response to the request.
        """
        # attempt to find path to requested content
        full_path = self._find_content_path(request.request_uri)

        # if no content found
        if full_path is None:
            return HTTPResponse(404,
                                "Failed to find {}".format(request.request_uri)
                                )

        # check if content-type is known
        file_extension = path.splitext(full_path)[1]
        if file_extension not in self.FILE_TYPES:
            response = "Unknown content-type: {}".format(file_extension)
            return HTTPResponse(501, response)

        return self._handle_file(full_path,
                                 self.FILE_TYPES[file_extension],
                                 file_extension
                                 )

    def _do_HEAD(self, request):
        """Attempt to respond to a HTTP GET request.

        Args:
            request (HTTPRequest): The request to respond to.

        Returns:
            HTTPResponse: A valid HTTP response to the request.
        """
        return self._NOT_IMPLEMENTED()

    def _do_POST(self, request):
        """Attempt to respond to a HTTP POST request.

        Args:
            request (HTTPRequest): The request to respond to.

        Returns:
            HTTPResponse: A valid HTTP response to the request.
        """
        return self._NOT_IMPLEMENTED()

    def _do_PUT(self, request):
        """Attempt to respond to a HTTP PUT request.

        Args:
            request (HTTPRequest): The request to respond to.

        Returns:
            HTTPResponse: A valid HTTP response to the request.
        """
        return self._NOT_IMPLEMENTED()

    def _do_DELETE(self, request):
        """Attempt to respond to a HTTP DELETE request.

        Args:
            request (HTTPRequest): The request to respond to.

        Returns:
            HTTPResponse: A valid HTTP response to the request.
        """
        return self._NOT_IMPLEMENTED()

    def _do_CONNECT(self, request):
        """Attempt to respond to a HTTP CONNECT request.

        Args:
            request (HTTPRequest): The request to respond to.

        Returns:
            HTTPResponse: A valid HTTP response to the request.
        """
        return self._NOT_IMPLEMENTED()

    def _do_OPTIONS(self, request):
        """Attempt to respond to a HTTP OPTIONS request.

        Args:
            request (HTTPRequest): The request to respond to.

        Returns:
            HTTPResponse: A valid HTTP response to the request.
        """
        return self._NOT_IMPLEMENTED()

    def _do_TRACE(self, request):
        """Attempt to respond to a HTTP TRACE request.

        Args:
            request (HTTPRequest): The request to respond to.

        Returns:
            HTTPResponse: A valid HTTP response to the request.
        """
        return self._NOT_IMPLEMENTED()

    def _do_PATCH(self, request):
        """Attempt to respond to a HTTP PATCH request.

        Args:
            request (HTTPRequest): The request to respond to.

        Returns:
            HTTPResponse: A valid HTTP response to the request.
        """
        return self._NOT_IMPLEMENTED()

    def _NOT_IMPLEMENTED(self):
        """Generate a "not implemented" response.

        Returns:
            HTTPResponse: A "not implemented" HTTP response.
        """
        return HTTPResponse(501, "Not implemented.")

    METHODS = {
        HTTPRequest.HTTPMethod.GET: _do_GET,
        HTTPRequest.HTTPMethod.HEAD: _do_HEAD,
        HTTPRequest.HTTPMethod.POST: _do_POST,
        HTTPRequest.HTTPMethod.PUT: _do_PUT,
        HTTPRequest.HTTPMethod.DELETE: _do_DELETE,
        HTTPRequest.HTTPMethod.CONNECT: _do_CONNECT,
        HTTPRequest.HTTPMethod.OPTIONS: _do_OPTIONS,
        HTTPRequest.HTTPMethod.TRACE: _do_TRACE,
        HTTPRequest.HTTPMethod.PATCH: _do_PATCH
    }

    FILE_TYPES = {
        ".html": "text",
        ".css": "text",
        ".png": "image",
        ".ico": "image"
    }
