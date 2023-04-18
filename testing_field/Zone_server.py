import socket
from clients.Client_classes.client_objects import Point


class zone_server:
    def __init__(self, port: int, top_left_x, top_left_y, bottom_right_x, bottom_right_y):
        self.zone_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.zone_server_socket.bind(("0.0.0.0", port))
        self.top_left_pos = Point(top_left_x, top_left_y)
        self.bottom_right_pos = Point(bottom_right_x, bottom_right_y)
        self.players = []

    def get_amount_of_players_in_zone(self) -> int:
        return len(self.players)

    def add_player(self, player):
        self.players.append(player)
