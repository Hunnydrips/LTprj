import socket


class load_balancer:
    def __init__(self):
        self.balancing_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
