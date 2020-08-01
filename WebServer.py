"""Module containing a simple web server for communication via a TCP Socket.

Handling of requests is delegated to a "request handler" class.
"""
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import select
from threading import Thread
from RequestHandler import RequestHandler
from HTTPResponse import HTTPResponse
from HTTPRequest import HTTPRequest


class WebServer:
    """Web server class.

    Communicates through a TCP socket, handling client requests.
    """

    HOST, PORT = '', 8080  # localhost port 8080
    ADDRESS_FAMILY = AF_INET  # ipv4 addresses
    SOCKET_TYPE = SOCK_STREAM  # TCP socket
    REQUEST_QUEUE_SIZE = 5  # only 1 connection handled at a time

    def __init__(self):
        """Create a TCP socket."""
        listen_socket = socket(self.ADDRESS_FAMILY, self.SOCKET_TYPE)
        listen_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        listen_socket.bind((self.HOST, self.PORT))
        listen_socket.listen(self.REQUEST_QUEUE_SIZE)
        self.listen_socket = listen_socket

    def serve_forever(self):
        """Continually accept and respond to client requests."""
        print("Serving on port {} ...".format(self.PORT))
        while True:
            client_connection, client_address = self.listen_socket.accept()
            print("Request made from {}".format(client_address))
            ct = WebServer.ClientThread(client_connection, client_address)
            ct.start()

    class ClientThread(Thread):
        """Class to handle a client request on a single thread."""

        BUFFER_SIZE = 4096  # somewhat arbitrary
        READ_TIMEOUT = 2  # 1 seconds

        def __init__(self, client, address):
            """Initialise a thread to handle a client request.

            Args:
                client (socket): A socket object, currently accepting a
                    connection from the client.
                address (tuple): A tuple containing the IP and port of the
                    connected client.
            """
            Thread.__init__(self, daemon=True)
            self.client = client
            self.address = address
            self.request_handler = RequestHandler()

        def _recieve_data(self):
            """Read all available bytes from the buffer."""
            self.client.setblocking(0)

            request_data = b""
            while True:
                # check if there is data to be read
                ready = select.select([self.client], [], [], self.READ_TIMEOUT)
                if ready[0]:
                    # read new data
                    new_data = self.client.recv(self.BUFFER_SIZE)
                    request_data += new_data

                    if len(new_data) < self.BUFFER_SIZE:
                        break

                # if no new data in the timeout, but some data already
                # recieved, then exit assuming full message has been recieved
                elif request_data:
                    break
            self.request_data = request_data
            self.client.setblocking(1)
            print("Data recieved from {}".format(self.address))

        def _generate_response(self):
            """Generate a response to the client request."""
            # attempt to parse the request as a HTTPRequest
            try:
                request = HTTPRequest(self.request_data)
            except Exception as msg:
                # generate response to invalid request
                response = HTTPResponse(400, str(msg))
            else:
                # generate response to valid request
                response = self.request_handler.generate_response(request)
            self.response = response.create_http_response()

        def run(self):
            """Handle a single request from the client.

            Recieve data from the client, generate an appropriate response,
            send the response and close the connection.

            """
            self._recieve_data()
            self._generate_response()

            # send response and close the connection
            self.client.sendall(self.response)
            print("Response sent to {}".format(self.address))
            self.client.close()


if __name__ == "__main__":
    server = WebServer()
    server.serve_forever()
