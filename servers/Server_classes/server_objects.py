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
        self.time_last_moved = time.time()
        self.collision_center: Point = Point(0, 0)
        self.json_str = None

    def move(self) -> bool:
        """
        move function for player, calcs coordinates
        :return: if the player has moved longer than .05 seconds
        """
        if time.time() - self.time_last_moved >= .05:
            self.time_last_moved = time.time()
            self.collision_center.x += self.x_dir * 8
            self.collision_center.y += self.y_dir * 8
            return True
        return False


# class ServerLaser:
#     def __init__(self, start_x: float, start_y: float, angle: float):
#         self.x: float = start_x
#         self.y: float = start_y
#         self.angle: float = angle
#         self.creation_time = time.time()
#         self.time_last_moved = time.time()
#         self.frames_at_curr_state: int = 0
#
#     def move(self):
#         pass
