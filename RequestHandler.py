from HTTPResponse import HTTPResponse
from HTTPRequest import HTTPRequest
from os import getcwd, path


class RequestHandler:

    def generate_response(self, request):
        # call appropriate method
        return self.METHODS[request.method](self, request)

    def _add_header_to_html(self, body):
        with open("root/base.html", "r") as base_file:
            html = base_file.read().format(body)
        return html

    def _handle_html(self, full_path, extension):
        with open(full_path, 'r') as html_file:
            html = html_file.read()
        content = self._add_header_to_html(html)
        return HTTPResponse(200, content)

    def _handle_image(self, full_path, extension):
        with open(full_path, "rb") as image_file:
            image_data = image_file.read()
        return HTTPResponse(200, image_data, "image/"+extension[1:])

    def _find_content_path(self, uri):
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
        # attempt to find path to requested content
        full_path = self._find_content_path(request.request_uri)

        # if no content found
        if full_path is None:
            return HTTPResponse(404,
                                "Failed to find {}".format(request.request_uri)
                                )

        # check if appropriate file handler exists
        file_extension = path.splitext(full_path)[1]
        if file_extension not in self.FILE_HANDLERS:
            response = "No appropriate file handler for {}"
            return HTTPResponse(501, response.format(file_extension))

        return self.FILE_HANDLERS[file_extension](self,
                                                  full_path,
                                                  file_extension)

    def _do_HEAD(self, request):
        return self._NOT_IMPLEMENTED()

    def _do_POST(self, request):
        return self._NOT_IMPLEMENTED()

    def _do_PUT(self, request):
        return self._NOT_IMPLEMENTED()

    def _do_DELETE(self, request):
        return self._NOT_IMPLEMENTED()

    def _do_CONNECT(self, request):
        return self._NOT_IMPLEMENTED()

    def _do_OPTIONS(self, request):
        return self._NOT_IMPLEMENTED()

    def _do_TRACE(self, request):
        return self._NOT_IMPLEMENTED()

    def _do_PATCH(self, request):
        return self._NOT_IMPLEMENTED()

    def _NOT_IMPLEMENTED(self):
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

    FILE_HANDLERS = {
        ".html": _handle_html,
        ".png": _handle_image,
        ".ico": _handle_image
    }
