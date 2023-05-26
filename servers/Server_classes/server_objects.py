import time


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
    def __init__(self, username: str, address: tuple):
        """
        Basic constructor for a server object player, used to make needed attributes clearer
        :param username: player's username
        :param address: player's address in local subnet
        """
        self.x_dir: int = 0
        self.y_dir: int = 0
        self.username: str = username
        self.address: tuple = address
        self.time_last_moved: float = time.time()
        self.collision_center: Point = Point(0, 0)
        self.json_str: dict = {}

    def move(self) -> bool:
        """
        move function for player, calcs coordinates
        :return: if the player has moved longer than .05 seconds
        """
        self.collision_center.x += self.x_dir // 2 ** 3
        self.collision_center.y += self.y_dir // 2 ** 3              # an estimation for the difference in time complexity
        if time.time() - self.time_last_moved >= 60 * 5:             # in each five minutes, check the position in game server
            self.time_last_moved = time.time()
            return True
        return False

