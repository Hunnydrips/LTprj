import pygame
import socket
import time
import math


class Point:
    def __init__(self, x: int, y: int):
        """
        Basic constructor for point object
        :param x: x coordinate
        :param y: y coordinate
        """
        self.x, self.y = x, y

    def __eq__(self, other):
        """
        Equator function, other terms for me
        :param other: other point for comparison
        :return: if it is the exact same point value wise
        """
        return self.x == other.x and self.y == other.y

    def to_tuple(self) -> tuple:
        """
        conversion to tuple
        :return: coordinates in tuple
        """
        return self.x, self.y


class Animation:
    def __init__(self, path: str, amount: int, time_per_sprite: float):
        """
        Basic constructor for an animation type object
        :param path: path in files, string
        :param amount: the amount of sprites between frames, an integer
        :param time_per_sprite: a float indicating the time between sprites
        """
        self.path: str = path
        self.sprite_list: list = []
        self.amount_of_sprites: int = amount
        self.current_sprite: int = 0
        self.time_per_sprite: float = time_per_sprite
        self.start_frame: float = time.time()
        self.load()

    def load(self):
        """
        Loading sprites
        :return: Nothing
        """
        for i in range(self.amount_of_sprites):
            self.sprite_list.append(pygame.image.load(f"{self.path}{i}.png"))

    def reset(self):
        """
        Basic reset for last resort
        :return: Nothing
        """
        self.current_sprite, self.start_frame = 0, time.time()

    def animate(self) -> bool:
        """
        Animate function, main function for animating screen objects
        :return: if the animation had finished or not
        """
        if self.start_frame + self.time_per_sprite <= time.time():
            self.start_frame = time.time()
            self.current_sprite += 1
            if self.current_sprite == self.amount_of_sprites:
                self.current_sprite %= self.amount_of_sprites
                return True
        return False


class ClientPlayer:
    def __init__(self, username: str, sock: socket.socket = None, pos: Point = Point(250, 250), status: str = "idle", angle: float = 0):
        """
        My main class that is implemented with the animation class as included down here
        :param username: the player's username, string
        :param pos: the player's start position, Point object
        :param status: the player's current status of animation, string
        :param angle: angle of player to mouse, float
        """
        self.animations: dict = {
            "idle": Animation("Client_classes/shotgun/idle/survivor-idle_shotgun_", 20, .05),
            "move": Animation("Client_classes/shotgun/move/survivor-move_shotgun_", 20, .075),
            "reload": Animation("Client_classes/shotgun/reload/survivor-reload_shotgun_", 20, .075),
            "shoot": Animation("Client_classes/shotgun/shoot/survivor-shoot_shotgun_", 3, .0833)
        }

        self.client_sock: socket.socket = sock
        self.collision_center: Point = pos
        self.angle: float = angle
        self.username = username
        self.status = status
        self.next_status: str = "idle"
        self.x_dir: int = 0
        self.y_dir: int = 0
        self.last_shot: int = 0
        self.left_in_magazine: int = 6
        self.lasers: list = []
        self.to_blit = None
        self.hit_box = None

    def create_image(self, angle: float):
        """
        Function that creates my image for pygame, error is here for stuttering
        :param angle: angle of character and mouse, float that is in radians
        :return: Nothing
        """
        self.angle = angle
        self.angle *= -180 / math.pi
        self.angle += 4.5
        self.to_blit = pygame.transform.rotate(self.animations[self.status].sprite_list[self.animations[self.status].current_sprite], self.angle)               # IN DEGREES
        self.hit_box = self.to_blit.get_rect()
        self.hit_box.center = pos_by_distance_and_angle(self.angle, -18.08, -52, self.collision_center)

    def shoot(self, mouse_x: int, mouse_y: int):
        """
        Shooting feature, player is able to project laser into game
        :param mouse_x: x coordinate of mouse
        :param mouse_y: y coordinate of mouse
        :return: Nothing
        """
        if self.status != "reload" and self.last_shot + 0.25 <= time.time() and self.left_in_magazine:
            self.last_shot = time.time()
            self.left_in_magazine -= 1
            self.lasers.append(ClientLaser(*pos_by_distance_and_angle(self.angle, 11.188, -186, self.collision_center), mouse_x, mouse_y))
            # print(*pos_by_distance_and_angle(self.angle, 11.188, -186, self.collision_center))
            self.status = "shoot"
            self.animations[self.status].reset()

    def reload(self):
        """
        Two lines that assist function in the Client python file in reloading animation
        :return: Nothing
        """
        self.status = "reload"
        self.left_in_magazine = 6

    def move(self):
        """
        move function for player, updates coordinates
        :return: Nothing
        """
        self.collision_center.x += self.x_dir * 10
        self.collision_center.y += self.y_dir * 10


class ClientLaser:
    def __init__(self, x: float, y: float, target_x: int, target_y: int):
        """
        Basic constructor for creating a laser object on the screen
        :param x: x coordinate of laser, float
        :param y: y coordinate of laser, float
        :param target_x: x coordinate of target, int
        :param target_y: y coordinate of target, int
        """
        self.x: float = x
        self.y: float = y
        self.last_move: float = time.time()
        self.creation_time: float = time.time()
        self.angle = math.atan2(float(target_y - self.y), float(target_x - self.x))
        self.frames_per_state: int = 20
        self.frames_at_curr_state: int = 0
        self.v_x: float = float(18 * math.cos(self.angle))
        self.v_y: float = float(18 * math.sin(self.angle))
        self.angle *= -180 / math.pi
        self.state: int = 0
        self.frames_R: list = []
        self.rect = None
        self.to_blit = None
        self.load()

    def load(self):
        """
        Loading some sprites needed for laser
        :return: Nothing
        """
        for i in range(2):
            self.frames_R.append(pygame.image.load(f"Client_classes/Lasers/R{i}.png"))

    def move(self) -> bool:
        """
        Function for moving projectile on the screen via pygame
        :return: if the laser is more than 2 seconds old
        """
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


def pos_by_distance_and_angle(player_angle: float, angle_const: float, distance: float, collision_center: Point) -> tuple:
    """
    A more complex function involving mathematical operations and analytical geometry, converts polar coordinates to cartesian ones
    :param player_angle: current angle of player
    :param angle_const: some angle constant for making the better looks
    :param distance: the radius of an inscribed circle
    :param collision_center: the player's collision centre, basically his centre
    :return: cartesian coordinates of some object for calculations of some sort
    """
    angle = (angle_const - player_angle) * math.pi / 180
    grad = math.tan(angle)
    x = distance / math.sqrt(1 + grad ** 2) + collision_center.x
    y = grad * (x - collision_center.x) + collision_center.y
    if -90 < player_angle - angle_const < 90:
        x = 2 * collision_center.x - x
        y = 2 * collision_center.y - y
    return int(x), int(y)
