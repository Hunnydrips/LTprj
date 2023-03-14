from random import randint
from Classes import Point


class player:
    def __init__(self, username: str, address: tuple):
        self.pos = Point.point(randint(0, 1920 * 20), randint(0, 1080 * 20))
        self.username = username
        self.address = address
        self.can_shoot_at = 0
        self.stunned = False
