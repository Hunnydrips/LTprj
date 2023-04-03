import time
import pygame
from clients.Client_classes.client_objects import point
import math


class animation:
    def __init__(self, path: str, amount: int, time_per_sprite: float):
        self.path: str = path
        self.sprite_list: list = []
        self.amount_of_sprites: int = amount
        self.current_sprite: int = 0
        self.time_per_sprite: float = time_per_sprite
        self.start_frame: float = time.time()
        self.load()

    def load(self):
        for i in range(self.amount_of_sprites):
            self.sprite_list.append(pygame.image.load(f"{self.path}{i}.png"))

    def reset(self):
        self.current_sprite, self.start_frame = 0, time.time()

    def animate(self) -> bool:
        if self.start_frame + self.time_per_sprite <= time.time():
            self.start_frame = time.time()
            self.current_sprite += 1
            if self.current_sprite == self.amount_of_sprites:
                self.current_sprite %= self.amount_of_sprites
                return True
        return False


class player:
    def __init__(self, dot: point = point(0, 0)):
        self.animations: dict = {
            "idle": animation("shotgun/idle/survivor-idle_shotgun_", 20, .05),
            "move": animation("shotgun/move/survivor-move_shotgun_", 20, .075),
            "reload": animation("shotgun/reload/survivor-reload_shotgun_", 20, .075),
            "shoot": animation("shotgun/shoot/survivor-shoot_shotgun_", 3, .0833)
        }
        self.status: str = "idle"
        self.collision_center: point = dot
        self.x_dir: int = 0
        self.y_dir: int = 0
        self.angle: int = 0
        self.last_shot: int = 0
        self.next_status: str = "idle"
        self.left_in_magazine: int = 6
        self.lasers: list = []
        self.to_blit = None
        self.hit_box = None

    def move(self):
        self.collision_center.x += self.x_dir * 2
        self.collision_center.y += self.y_dir * 2

    def create_image(self, mouse_x: int, mouse_y: int):
        self.angle = math.atan2(float(mouse_y - self.collision_center.y), float(mouse_x - self.collision_center.x))
        self.angle *= -180 / math.pi
        self.angle += 4.5
        self.to_blit = pygame.transform.rotate(
            self.animations[self.status].sprite_list[self.animations[self.status].current_sprite], self.angle)
        self.hit_box = self.to_blit.get_rect()
        self.hit_box.center = pos_by_distance_and_angle(self.angle, -18.08, -51, self.collision_center)

    def shoot(self, mouse_x: int, mouse_y: int):
        if self.status != "reload" and self.last_shot + 0.25 <= time.time() and self.left_in_magazine:
            self.last_shot = time.time()
            self.left_in_magazine -= 1
            self.lasers.append(laser(*pos_by_distance_and_angle(self.angle, 11.188, -186, self.collision_center), mouse_x, mouse_y))
            self.status = "shoot"
            self.animations[self.status].reset()

    def reload(self):
        self.status = "reload"
        self.left_in_magazine = 6


class laser:
    def __init__(self, x: float, y: float, target_x: int, target_y: int):
        self.x: float = x
        self.y: float = y
        self.last_move = time.time()
        self.creation_time = time.time()
        self.angle = math.atan2(float(target_y - self.y), float(target_x - self.x))
        self.frames_per_state: int = 20
        self.frames_at_curr_state: int = 0
        self.v_x: float = float(10 * math.cos(self.angle))
        self.v_y: float = float(10 * math.sin(self.angle))
        self.angle *= -180 / math.pi
        self.state: int = 0
        self.frames_R: list = []
        self.frames_P: list = []
        self.rect = None
        self.to_blit = None
        self.load()

    def load(self):
        for i in range(2):
            self.frames_R.append(pygame.image.load(f"Lasers/R{i}.png"))
            self.frames_P.append(pygame.image.load(f"Lasers/P{i}.png"))

    def move(self) -> bool:
        if self.creation_time + 2 <= time.time():
            return True
        if self.last_move + 0.01 <= time.time():
            self.last_move = time.time()
            self.x += self.v_x
            self.y += self.v_y
            self.frames_at_curr_state += 1
        if self.frames_at_curr_state == self.frames_per_state:
            self.state += 1
            if self.state == 2:
                self.state = 1
            self.frames_at_curr_state = 0
        self.to_blit = pygame.transform.rotate(self.frames_R[self.state], self.angle)
        self.rect = self.to_blit.get_rect()
        self.rect.center = round(self.x), round(self.y)
        return False


def pos_by_distance_and_angle(player_angle: float, angle_const: float, distance: float, collision_center: point) -> tuple:
    angle = (angle_const - player_angle) * math.pi / 180
    m = math.tan(angle)
    x = distance / math.sqrt(1 + m ** 2) + collision_center.x
    y = m * (x - collision_center.x) + collision_center.y
    if -90 < player_angle - angle_const < 90:
        x = 2 * collision_center.x - x
        y = 2 * collision_center.y - y
    return int(x), int(y)
