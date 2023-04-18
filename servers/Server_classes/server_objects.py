import time


class Point:
    def __init__(self, x: int, y: int):
        self.x, self.y = x, y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def to_tuple(self) -> tuple:
        return self.x, self.y


class ServerPlayer:
    def __init__(self, username: str, address: tuple):
        self.x_dir: int = 0
        self.y_dir: int = 0
        self.username: str = username
        self.address: tuple = address
        self.time_last_moved = time.time()
        self.collision_center: Point = Point(0, 0)
        self.json_str = None

    def move(self) -> bool:
        if time.time() - self.time_last_moved >= 0.05:
            self.time_last_moved = time.time()
            self.collision_center.x += self.x_dir * 8
            self.collision_center.y += self.y_dir * 8
            return True
        return False


class Laser:
    def __init__(self, start_x: float, start_y: float, angle: float):
        self.x: float = start_x
        self.y: float = start_y
        self.angle: float = angle
        self.creation_time = time.time()
        self.time_last_moved = time.time()
        self.frames_at_curr_state: int = 0

    def move(self):
        pass
