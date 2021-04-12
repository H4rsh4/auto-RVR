import socket      # Import socket module
import socketserver
from pickle import loads
import threading

class SensorDataHandler(socketserver.BaseRequestHandler):

    data = " "

    def handle(self):
        global sensor_data
        while self.data:
            self.data = self.request.recv(1024)
            sensor_data = loads(self.data)
            # print "{} sent:".format(self.client_address[0])
            print(sensor_data)


_host = '192.168.1.74'
_port = 6666

class ultrasonic_server(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
    def sonic_stream(self, host, port):
        server = socketserver.TCPServer((self.host, self.port), SensorDataHandler)
        server.serve_forever()
    def start(self):
        sensor_thread = threading.Thread(target=self.sensor_stream, args=(self.host, self.port2))
        sensor_thread.daemon = True
        sensor_thread.start()
