"""Module containing a simple web server for communication via a TCP Socket.

Handling of requests is delegated to a "request handler" class that is passed
in on initialisation.
"""
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR


class WebServer:
    """Web server class.

    Communicates through a TCP socket, handling client requests.
    """

    HOST, PORT = '', 8080  # localhost port 8080
    ADDRESS_FAMILY = AF_INET  # ipv4 addresses
    SOCKET_TYPE = SOCK_STREAM  # TCP socket
    REQUEST_QUEUE_SIZE = 1  # only 1 connection handled at a time
    BUFFER_SIZE = 1024  # somewhat arbitrary

    def __init__(self, request_handler_type):
        """Create a TCP socket and a request handler.

        Args:
            request_handler_type (class): A class type that can parse client
            requests and generate an appropriate repsonse.
        """
        if request_handler_type is None:
            raise Exception("Error: Must pass a request_handler_type")

        # instantiate the request_handler_type
        self.request_handler = request_handler_type()

        # Setup the socket
        self.listen_socket = socket(self.ADDRESS_FAMILY, self.SOCKET_TYPE)
        self.listen_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.listen_socket.bind((self.HOST, self.PORT))
        self.listen_socket.listen(1)

    def _handle_request(self, client):
        """Handle a single request from the client.

        Recieve data from the client, generate an appropriate response,
        send the response and close the connection.

        Args:
            client (socket): A socket object, currently accepting a connection
                from the client.
        """
        request_data = client.recv(self.BUFFER_SIZE)
        response = self.request_handler.generate_response(request_data)
        client.sendall(response)
        print("Response sent.")
        client.close()

    def serve_forever(self):
        """Continually accept and respond to client requests."""
        print("Serving on port {} ...".format(self.PORT))
        while True:
            client_connection, client_address = self.listen_socket.accept()
            print("Request made from {}".format(client_address))
            self._handle_request(client_connection)
