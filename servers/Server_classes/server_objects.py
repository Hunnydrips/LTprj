import time


class point:
    def __init__(self, x: int, y: int):
        self.x, self.y = x, y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def to_tuple(self) -> tuple:
        return self.x, self.y


class player:
    def __init__(self, username: str, address: tuple):
        self.username: str = username
        self.address: tuple = address
        self.time_last_moved = time.time()
        self.collision_center: point = point(0, 0)
        self.x_dir, self.y_dir = 0, 0

    def move(self) -> bool:
        if time.time() - self.time_last_moved >= 0.05:
            self.time_last_moved = time.time()
            self.collision_center.x += self.x_dir * 5
            self.collision_center.y += self.y_dir * 5
            return True
        return False
