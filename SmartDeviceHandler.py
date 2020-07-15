from threading import Lock
from HTTPResponse import HTTPResponse


class SmartDeviceHandler():

    SMART_HOME_KEY = "/smarthome/"

    def __init__(self):
        self.lock = Lock()

    def handle_request(self, request):
        self.command = request.request_uri[len(self.SMART_HOME_KEY):]
        print(self.command)
        return HTTPResponse(501, "Not Implemented")
