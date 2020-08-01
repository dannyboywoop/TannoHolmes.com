from threading import Lock
from json import loads, dumps
from HTTPResponse import HTTPResponse


class SmartDeviceHandler():

    SMART_HOME_KEY = "/smarthome/"
    DEVICES_FILE = "Smart_Devices/Smart_Devices.json"

    def __init__(self):
        self.device_file_lock = Lock()

    def handle_request(self, request):
        self.command = request.request_uri[len(self.SMART_HOME_KEY):]

        try:
            if self.command == "discover":
                return self._run_discovery()

            if self.command == "status":
                return self._run_status_check(request.body)

            if self.command == "directive":
                return self._run_directive(request.body)

        except Exception as msg:
            return HTTPResponse(500, str(msg))

        return HTTPResponse(501, "Not implemented.")

    def _run_discovery(self):
        device_data = self._load_devices()
        return HTTPResponse(200, dumps(device_data), "text/json")

    def _run_status_check(self, request_body):
        endpoint_id = request_body.strip()
        endpoint = self._find_endpoint(endpoint_id)

        if endpoint is None:
            return HTTPResponse(404, "endpoint not found!")

        return HTTPResponse(200, "endpoint found!")

    def _run_directive(self, request_body):
        directive_json = loads(request_body)["directive"]

        # check endpoint exists
        endpoint_id = directive_json["endpoint"]["endpointId"]
        endpoint = self._find_endpoint(endpoint_id)
        if endpoint is None:
            return HTTPResponse(404, "endpoint not found!")

        # check endpoint has given interface
        interface = directive_json["header"]["namespace"]
        if not self._device_has_interface(endpoint, interface):
            return HTTPResponse(405, "endpoint does not use this interface!")

        return HTTPResponse(200, "Directive")

    def _load_devices(self):
        self.device_file_lock.acquire()
        with open(self.DEVICES_FILE, "r") as input_file:
            devices = loads(input_file.read())
        self.device_file_lock.release()
        return devices

    def _find_endpoint(self, endpoint_id):
        device_data = self._load_devices()

        for endpoint in device_data["endpoints"]:
            if endpoint["endpointId"] == endpoint_id:
                return endpoint

        # otherwise, endpoint not found
        return None

    def _device_has_interface(self, endpoint, interface):
        for capability in endpoint["capabilities"]:
            if capability["interface"] == interface:
                return True
        return False
