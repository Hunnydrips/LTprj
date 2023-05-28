from collections import deque
from dataclasses import dataclass
from typing import Deque, TypedDict
import logging
import time
import socket


class JSONStr(TypedDict):
    pos: list
    angle: float
    status: str
    username: str
    current_sprite: int


class Point:
    def __init__(self, x: int, y: int):
        """
        Basic constructor for server point class
        :param x: x coordinate, integer
        :param y: y coordinate, integer
        """
        self.x, self.y = x, y

    def __eq__(self, other):
        """
        Equating function to the other point
        :param other: another point
        :return: if they are the same
        """
        return self.x == other.x and self.y == other.y

    def to_tuple(self) -> tuple:
        """
        Conversion to type tuple
        :return: x and y as a tuple
        """
        return self.x, self.y


class ServerPlayer:
    def __init__(self, username: str, address: tuple, sock: socket.socket):
        """
        Basic constructor for a server object player, used to make needed attributes clearer
        :param username: player's username
        :param address: player's address in local subnet
        """
        self.personal_game_sock: socket.socket = sock
        self.x_dir: int = 0
        self.y_dir: int = 0
        self.username: str = username
        self.address: tuple = address
        self.time_last_moved: float = time.time()
        self.collision_center: Point = Point(0, 0)
        self.update_queue: Deque[dict] = deque()
        self.online = True
        self.pkt_counter: int = 0           # resets after every n packets
        self.pos_before_counter_reset: Point = Point(0, 0)

    def check_validity(self, position: tuple) -> bool:
        self.pkt_counter += 1
        if not (self.pkt_counter >= 25):
            return True
        self.pkt_counter %= 25
        client_x, client_y = position
        return not abs(client_x - self.pos_before_counter_reset.x) >= 16000 or abs(client_y - self.pos_before_counter_reset.y) >= 9000


@dataclass
class ServerLaser:
    x: float
    y: float
    target_x: int
    target_y: int
