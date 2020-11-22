"""Module containing a simple web server for communication via a TCP Socket.

Handling of requests is delegated to a "request handler" class.
"""
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from ssl import create_default_context, SSLError, Purpose
from logging import getLogger, handlers, DEBUG
from os import path, mkdir
from queue import Queue
from select import select
from threading import Thread
from HTTPTools.RequestHandler import RequestHandler
from HTTPTools.HTTPResponse import HTTPResponse
from HTTPTools.HTTPRequest import HTTPRequest


class WebServer:
    """Web server class.

    Communicates through a TCP socket, handling client requests.
    """

    HOST, PORT = '', 8080  # localhost port 8080
    ADDRESS_FAMILY = AF_INET  # ipv4 addresses
    SOCKET_TYPE = SOCK_STREAM  # TCP socket
    REQUEST_QUEUE_SIZE = 10  # will queue up to 10 requests

    def __init__(self):
        """Create a TCP socket."""
        security_path = root_path + "/security"
        print(security_path)
        self.context = create_default_context(Purpose.CLIENT_AUTH)
        self.context.load_cert_chain(certfile=security_path+"/public.crt",
                                     keyfile=security_path+"/private.key")

        listen_socket = socket(self.ADDRESS_FAMILY, self.SOCKET_TYPE)
        listen_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        listen_socket.bind((self.HOST, self.PORT))
        listen_socket.listen(self.REQUEST_QUEUE_SIZE)
        self.listen_socket = listen_socket

    def serve_forever(self):
        """Continually accept and respond to client requests."""
        root_logger.info("Serving on port {} ...".format(self.PORT))
        while True:
            # accept an incoming connection
            client_socket, client_address = self.listen_socket.accept()
            root_logger.info("Request made from {}".format(client_address))

            # attempt to establish a https connection
            try:
                ssl_socket = self.context.wrap_socket(client_socket,
                                                      server_side=True)
            except SSLError as e:
                root_logger.error(e)

            # if https handshake was successful
            if ssl_socket:
                ct = WebServer.ClientThread(ssl_socket, client_address)
                ct.start()

    class ClientThread(Thread):
        """Class to handle a client request on a single thread."""

        BUFFER_SIZE = 4096  # somewhat arbitrary
        READ_TIMEOUT = 2  # 2 seconds

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
                ready = select([self.client], [], [], self.READ_TIMEOUT)
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
            root_logger.info("Data recieved from {}".format(self.address))

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
            root_logger.info("Response sent to {}".format(self.address))
            self.client.close()


if __name__ == "__main__":
    root_path = path.dirname(__file__)

    # setup logging
    logs_path = path.join(root_path, "logs")
    print(logs_path)
    if not path.exists(logs_path):
        mkdir(logs_path)
    log_queue = Queue(-1)
    queue_handler = handlers.QueueHandler(log_queue)
    handler = handlers.TimedRotatingFileHandler(logs_path+"/Server.log",
                                                when="h",
                                                interval=4,
                                                backupCount=5)
    listener = handlers.QueueListener(log_queue, handler)
    root_logger = getLogger()
    root_logger.addHandler(queue_handler)
    root_logger.setLevel(DEBUG)
    listener.start()

    # setup and run server
    server = WebServer()
    server.serve_forever()
