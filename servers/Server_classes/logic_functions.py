from .server_objects import *
from clients.Client_classes.client_objects import *

TILE_SIZE: int = 120
HIT_BOX_SIZE: int = 144
TILED_MAP_WIDTH: int = 319
TILED_MAP_HEIGHT: int = 179

COLLIDE_LIST: list = [
    Point(2, 8),
    Point(5, 9)
]


def check_collision(P: ServerPlayer | ClientPlayer) -> bool:
    """
    Checks collision of player with other tiles in map
    :param P:
    :return: if player is colliding with nearby dud blocks
    """
    tiles_to_check = []
    start_x, start_y = P.collision_center.x + 2 * P.x_dir - HIT_BOX_SIZE // 2, P.collision_center.y + 2 * P.y_dir - HIT_BOX_SIZE // 2
    mult_x, mult_y = -1, -1
    if P.x_dir == 1:
        mult_x = 1
        start_x += HIT_BOX_SIZE
    if P.y_dir == 1:
        mult_y = 1
        start_y += HIT_BOX_SIZE
    if P.x_dir:
        for i in range(3):
            tile = Point(start_x // TILE_SIZE, (start_y - HIT_BOX_SIZE // 2 * mult_y * i) // TILE_SIZE)
            if tile not in tiles_to_check:
                tiles_to_check.append(tile)
    if P.y_dir:
        for i in range(3):
            tile = Point((start_x - HIT_BOX_SIZE // 2 * mult_x * i) // TILE_SIZE, start_y // TILE_SIZE)
            if tile not in tiles_to_check:
                tiles_to_check.append(tile)
    for tile in tiles_to_check:
        if not (tile.x % TILED_MAP_WIDTH) or not (tile.y % TILED_MAP_HEIGHT) or tile in COLLIDE_LIST:
            return False
    return True
