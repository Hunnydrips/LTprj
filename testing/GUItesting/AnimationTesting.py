import pygame.draw
from pygame.locals import *
from GUIoop import *

pygame.init()
screen = pygame.display.set_mode((400, 400), RESIZABLE)
clock = pygame.time.Clock()
TILES = []
COLLIDE_LIST = [Point.point(2, 8), Point.point(5, 9)]


def load_tiles():
    for i in range(9):
        TILES.append(pygame.image.load(f"map_tiles/tile_{i}.png"))


def paint_map(camera_x: int, camera_y: int):
    to_add_x, to_add_y = camera_x % TILE_SIZE, camera_y % TILE_SIZE
    top_left_tile_x = camera_x // TILE_SIZE
    top_left_tile_y = camera_y // TILE_SIZE
    for i in range(screen.get_width() // TILE_SIZE + 2):
        for j in range(screen.get_height() // TILE_SIZE + 2):
            top_left_tile = Point.point(top_left_tile_x + i, top_left_tile_y + j)
            if top_left_tile in COLLIDE_LIST or (
                    (top_left_tile_x + i) % TILED_MAP_WIDTH == 0 and 0 <= top_left_tile_y + j <= TILED_MAP_HEIGHT) or (
                    (top_left_tile_y + j) % TILED_MAP_HEIGHT == 0 and 0 <= top_left_tile_x + i <= TILED_MAP_WIDTH):
                tile_pos = (i * TILE_SIZE - to_add_x, j * TILE_SIZE - to_add_y)
                if top_left_tile == Point.point(0, 0):
                    screen.blit(TILES[4], tile_pos)
                elif top_left_tile == Point.point(0, TILED_MAP_HEIGHT):
                    screen.blit(TILES[7], tile_pos)
                elif top_left_tile == Point.point(TILED_MAP_WIDTH, 0):
                    screen.blit(TILES[5], tile_pos)
                elif top_left_tile == Point.point(TILED_MAP_WIDTH, TILED_MAP_HEIGHT):
                    screen.blit(TILES[6], tile_pos)
                elif top_left_tile.y % TILED_MAP_HEIGHT == 0:
                    screen.blit(TILES[1], tile_pos)
                elif top_left_tile.x % TILED_MAP_WIDTH == 0:
                    screen.blit(TILES[2], tile_pos)
                else:
                    screen.blit(TILES[3], tile_pos)
            else:
                screen.blit(TILES[0], (i * TILE_SIZE - to_add_x, j * TILE_SIZE - to_add_y))


def move_and_collide(P: player, camera_x: int, camera_y: int, enable_hit_box: bool = False):
    P.collision_center.x += 2 * P.x_dir - camera_x
    P.collision_center.y += 2 * P.y_dir - camera_y

    tiles_to_check = []
    start_x, start_y = P.collision_center.x - HIT_BOX_SIZE // 2, P.collision_center.y - HIT_BOX_SIZE // 2
    mult_x, mult_y = -1, -1
    start_x += camera_x
    start_y += camera_y
    if enable_hit_box:
        collision_rect = pygame.Rect((0, 0), (HIT_BOX_SIZE, HIT_BOX_SIZE))
        collision_rect.center = P.collision_center.to_tuple()
        pygame.draw.rect(screen, BLUE, collision_rect, 1)
        pygame.draw.circle(screen, GREEN, P.collision_center.to_tuple(), 187, 1)
    if P.x_dir == 1:
        mult_x = 1
        start_x += HIT_BOX_SIZE
    if P.y_dir == 1:
        mult_y = 1
        start_y += HIT_BOX_SIZE
    if P.x_dir:
        for i in range(3):
            if enable_hit_box:
                pygame.draw.rect(screen, BLUE,
                                 ((start_x - camera_x, start_y - camera_y - HIT_BOX_SIZE // 2 * mult_y * i), (10, 10)))
                pygame.draw.rect(screen, GREEN, (
                    (start_x // TILE_SIZE * TILE_SIZE - camera_x,
                     (start_y - HIT_BOX_SIZE // 2 * mult_y * i) // TILE_SIZE * TILE_SIZE - camera_y),
                    (TILE_SIZE, TILE_SIZE)),
                                 4)
            tile = Point.point(start_x // TILE_SIZE, (start_y - HIT_BOX_SIZE // 2 * mult_y * i) // TILE_SIZE)
            if tile not in tiles_to_check:
                tiles_to_check.append(tile)
    if P.y_dir:
        for i in range(3):
            if enable_hit_box:
                pygame.draw.rect(screen, BLUE,
                                 ((start_x - camera_x - HIT_BOX_SIZE // 2 * mult_x * i, start_y - camera_y), (10, 10)))
                pygame.draw.rect(screen, GREEN, (
                    ((start_x - HIT_BOX_SIZE // 2 * mult_x * i) // TILE_SIZE * TILE_SIZE - camera_x,
                     start_y // TILE_SIZE * TILE_SIZE - camera_y), (TILE_SIZE, TILE_SIZE)),
                                 4)
            tile = Point.point((start_x - HIT_BOX_SIZE // 2 * mult_x * i) // TILE_SIZE, start_y // TILE_SIZE)
            if tile not in tiles_to_check:
                tiles_to_check.append(tile)
    flag = True
    for tile in tiles_to_check:
        if tile.x % TILED_MAP_WIDTH == 0 or tile.y % TILED_MAP_HEIGHT == 0 or tile in COLLIDE_LIST:
            flag = False

    P.collision_center.x -= 2 * P.x_dir - camera_x
    P.collision_center.y -= 2 * P.y_dir - camera_y
    if flag:
        P.move()


def main():
    running = True
    P = player(Point.point(120 * 2, 120 * 2))
    load_tiles()
    while running:
        camera_x, camera_y = P.collision_center.to_tuple()
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
        mouse_x, mouse_y = pygame.mouse.get_pos()
        screen.fill("black")
        paint_map(camera_x, camera_y)
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    pygame.quit()
                    running = False
                    break
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_d:
                            P.x_dir = 1
                        case pygame.K_a:
                            P.x_dir = -1
                        case pygame.K_w:
                            P.y_dir = -1
                        case pygame.K_s:
                            P.y_dir = 1
                        case pygame.K_r:
                            P.reload()
                    if P.x_dir or P.y_dir:
                        if P.status == "idle":
                            P.status = "move"
                            P.animations[P.status].reset()
                        else:
                            P.next_status = "move"
                case pygame.KEYUP:
                    if event.key in [pygame.K_d, pygame.K_a]:
                        P.x_dir = 0
                        if P.status == "move":
                            P.status = "idle"
                            P.animations[P.status].reset()
                    elif event.key in [pygame.K_w, pygame.K_s]:
                        P.y_dir = 0
                        if P.status == "move":
                            P.status = "idle"
                            P.animations[P.status].reset()
                case pygame.MOUSEBUTTONDOWN:
                    if event.button == pygame.BUTTON_LEFT:
                        P.shoot(mouse_x + camera_x, mouse_y + camera_y)
        if not running:
            break
        for Laser in P.lasers:
            if Laser.move():
                P.lasers.remove(Laser)
            else:
                Laser.rect.x -= camera_x
                Laser.rect.y -= camera_y
                screen.blit(Laser.to_blit, Laser.rect)
                distance = -54
                if Laser.state == 0:
                    distance = 0
                x, y = pos_by_distance_and_angle(Laser.angle, 0, distance, Point.point(*Laser.rect.center))
                laser_collide_rect = pygame.Rect((x, y), (30, 30))
                pygame.draw.rect(screen, BLUE, laser_collide_rect, 4)
                Laser.rect.x += camera_x
                Laser.rect.y += camera_y

        move_and_collide(P, camera_x, camera_y, ENABLE)

        P.collision_center.x -= camera_x
        P.collision_center.y -= camera_y
        P.create_image(mouse_x, mouse_y)
        screen.blit(P.to_blit, P.hit_box)
        P.collision_center.x += camera_x
        P.collision_center.y += camera_y
        if P.animations[P.status].animate() and P.status != "move":
            P.status = P.next_status
            P.next_status = "idle"
            if not P.left_in_magazine:
                P.reload()
            P.animations[P.status].reset()
        pygame.display.update()
        clock.tick(60)


if __name__ == '__main__':
    main()
