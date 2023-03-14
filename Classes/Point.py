class point:
    def __init__(self, x: int, y: int):
        self.x, self.y = x, y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def to_tuple(self) -> tuple:
        return self.x, self.y
