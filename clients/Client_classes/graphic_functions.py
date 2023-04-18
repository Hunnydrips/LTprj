from .client_objects import *

ENABLE = True
TILE_SIZE = 120
HIT_BOX_SIZE = 144
TILED_MAP_WIDTH = 319
TILED_MAP_HEIGHT = 179
camera_x, camera_y = 0, 0
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
TILES = []
COLLIDE_LIST = [Point(2, 8), Point(5, 9)]


def paint_map(screen: pygame.Surface):
    for i in range(9):                                                  # Load the tile images
        TILES.append(pygame.image.load(f"Client_classes/map_tiles/tile_{i}.png"))
    to_add_x, to_add_y = camera_x % TILE_SIZE, camera_y % TILE_SIZE
    top_left_tile_x = camera_x // TILE_SIZE
    top_left_tile_y = camera_y // TILE_SIZE
    for i in range(screen.get_width() // TILE_SIZE + 2):
        for j in range(screen.get_height() // TILE_SIZE + 2):
            top_left_tile = Point(top_left_tile_x + i, top_left_tile_y + j)
            if top_left_tile in COLLIDE_LIST or (
                    (top_left_tile_x + i) % TILED_MAP_WIDTH == 0 and 0 <= top_left_tile_y + j <= TILED_MAP_HEIGHT) or (
                    (top_left_tile_y + j) % TILED_MAP_HEIGHT == 0 and 0 <= top_left_tile_x + i <= TILED_MAP_WIDTH):
                tile_pos = (i * TILE_SIZE - to_add_x, j * TILE_SIZE - to_add_y)
                if top_left_tile == Point(0, 0):
                    screen.blit(TILES[4], tile_pos)
                elif top_left_tile == Point(0, TILED_MAP_HEIGHT):
                    screen.blit(TILES[7], tile_pos)
                elif top_left_tile == Point(TILED_MAP_WIDTH, 0):
                    screen.blit(TILES[5], tile_pos)
                elif top_left_tile == Point(TILED_MAP_WIDTH, TILED_MAP_HEIGHT):
                    screen.blit(TILES[6], tile_pos)
                elif top_left_tile.y % TILED_MAP_HEIGHT == 0:
                    screen.blit(TILES[1], tile_pos)
                elif top_left_tile.x % TILED_MAP_WIDTH == 0:
                    screen.blit(TILES[2], tile_pos)
                else:
                    screen.blit(TILES[3], tile_pos)
            else:
                screen.blit(TILES[0], (i * TILE_SIZE - to_add_x, j * TILE_SIZE - to_add_y))


def update_camera_cords(screen: pygame.Surface, player_pos: Point):
    global camera_x
    global camera_y
    camera_x, camera_y = player_pos.to_tuple()
    camera_x -= screen.get_width() // 2
    camera_y -= screen.get_height() // 2
    if camera_x < 0:
        camera_x = 0
    if camera_y < 0:
        camera_y = 0
    if camera_x > 1920 * 20 - screen.get_width():
        camera_x = 1920 * 20 - screen.get_width()
    if camera_y > 1080 * 20 - screen.get_height():
        camera_y = 1080 * 20 - screen.get_height()
    # print(camera_x, camera_y)


def get_camera_coordinates() -> tuple:
    return camera_x, camera_y


def blit_player(screen: pygame.Surface, P: ClientPlayer, mouse_x: int, mouse_y: int):
    P.create_image(mouse_x + camera_x, mouse_y + camera_y)
    P.hit_box.center = P.collision_center.x - camera_x, P.collision_center.y - camera_y
    screen.blit(P.to_blit, P.hit_box)


def animate_player(P: ClientPlayer):
    if P.animations[P.status].animate() and P.status != "move":
        P.status = P.next_status
        P.next_status = "idle"
        if not P.left_in_magazine:
            P.reload()
        P.animations[P.status].reset()

