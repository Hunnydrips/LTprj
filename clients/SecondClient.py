from threading import Thread
from typing import Tuple
from Client_classes.graphic_functions import *
from Client_classes.client_objects import *
from pygame.locals import *
import pygame
import socket
import logging
import json
import sys
import login_gui

event_to_packet: dict = {
    pygame.K_d: ["right", 1],
    pygame.K_a: ["left", -1],
    pygame.K_w: ["up", -1],
    pygame.K_s: ["down", 1],
    pygame.K_r: "reload"
}

players_to_display: list = []
CENTRAL_ADDR: tuple = ("127.0.0.1", 8100)
screen: pygame.Surface = pygame.display.set_mode((600, 600), RESIZABLE)
logging.basicConfig(level=logging.DEBUG)


def init_settings():
    """
    Initialise settings, sole purpose of this func is to show what's happening inside the DB
    :return: Nothing
    """
    with open("settings.txt", 'a'):
        pass  # ensuring the file's existence
    with open("settings.txt", 'r') as f:
        if len(f.readlines()) < 3:
            with open("settings.txt", 'w') as file:
                file.write("auto_sign_up\nname\npassword\n")


def log_in() -> Tuple[socket.socket, Tuple[str, int]]:  # connection to central so to have the ip of login server
    """
    Log-in function, separates duality and accepts players
    :return: Player socket and game server address
    """
    client_x_everything = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_x_everything.sendto(b"log_requested", CENTRAL_ADDR)
    data = client_x_everything.recvfrom(1024)[0].decode()[1:-1].split(", ")
    login_server_ip = (data[0][1:-1], int(data[1]))
    while not log_in_or_sign_up(client_x_everything, login_server_ip):
        logging.info("Waiting for somebody to connect")
    logging.info("Logged in successfully")
    data = client_x_everything.recvfrom(1024)[0].decode()[1:-1].split(", ")
    game_server_ip = (data[0][1:-1], int(data[1]))
    client_x_everything.sendto(json.dumps({"cmd": "begin"}).encode(), game_server_ip)
    logging.info("Connection to game server has been established :D")
    return client_x_everything, game_server_ip


def log_in_or_sign_up(client_x_everything: socket.socket, login_server_ip: tuple) -> bool:
    """
    Check player's need at beginning
    :param client_x_everything: player socket
    :param login_server_ip: log-in socket and ip
    :return: logged in or not
    """
    name_hash, password_hash, flag = "", "", ""
    with open("settings.txt", 'r') as f:
        data = f.read().split("\n")
    if data[0] == "true":
        name_hash, password_hash, flag = data[1], data[2], "log_in"
        client_x_everything.sendto(f"{name_hash}${password_hash}${flag}".encode(), login_server_ip)
        resp = client_x_everything.recvfrom(1024)[0].decode()
        positive_answer = ["log_in successful", "Created username successfully"]
        if resp not in positive_answer:
            data[0] = "false"
            with open("settings.txt", 'w') as f:
                f.write("\n".join(data))
        return resp in positive_answer
    else:
        login_gui.login_screen(client_x_everything, login_server_ip)
        return True


def handle_packet_from_game_server(client_x_everything: socket.socket(), P: ClientPlayer):
    """
    Handle packets coming from game server
    :param client_x_everything: player socket
    :param P: player object
    :return: Nothing
    """
    while True:
        data, ip = client_x_everything.recvfrom(1024)
        msg = json.loads(data.decode())
        print(msg)
        if msg["cmd"] == 'move':
            x, y = msg["pos"][0], msg["pos"][1]
            P.collision_center = Point(x, y)
        if msg["cmd"] == "load":
            for json_str in msg["json_strs"]:
                attr_dict: dict = json.loads(json_str)
                player_to_display: ClientPlayer = ClientPlayer(
                    username=attr_dict["name"],
                    pos=Point(*attr_dict["pos"]),
                    status=attr_dict["status"],
                    angle=attr_dict["angle"] / -180 * math.pi
                )
                player_to_display.animations[player_to_display.status].current_sprite = attr_dict["current_sprite"]
                flag = False
                for i, player in enumerate(players_to_display):
                    if player.username == player_to_display.username:
                        flag = True
                        players_to_display[i] = player_to_display
                if not flag:
                    print(enumerate(players_to_display))
                    players_to_display.append(player_to_display)


def display_players():
    """
    Minor shortening so to explain work and endeavour, consider errors in this funcs that may happen and how to handle them
    :return: Nothing
    """
    for player in players_to_display:
        try:
            animate_player(player)
            tmp_angle = player.angle
            blit_player(screen, player, player.angle)
            player.angle = tmp_angle
            move_all_lasers(player)
        except pygame.error as e:
            print(e)


def send_json_str_to_server(client_x_everything: socket.socket(), game_server_ip: tuple, P: ClientPlayer):
    """
    Send player details to server so to have a connected game with all players available
    :param client_x_everything: player socket
    :param game_server_ip: game server socket and ip
    :param P: player object
    :return: Nothing
    """
    prev_angle = P.angle
    while True:
        if prev_angle != P.angle:
            player_attr = {
                "pos": P.collision_center.to_tuple(),
                "angle": P.angle,
                "status": P.status,
                "name": "Alice",
                "current_sprite": P.animations[P.status].current_sprite
            }
            packet_data = json.dumps(player_attr)
            msg: dict = {
                "cmd": "add",
                "player_to_add": packet_data
            }
            client_x_everything.sendto(json.dumps(msg).encode(), game_server_ip)
            prev_angle = P.angle
            time.sleep(.3)


def move_all_lasers(P: ClientPlayer):
    """
    Move each player's lasers on their screens
    :param P: player object
    :return: Nothing
    """
    c_x, c_y = get_camera_coordinates()
    for P_laser in P.lasers:
        if P_laser.move():
            P.lasers.remove(P_laser)
        else:
            tmp_rect = P_laser.rect.copy()
            tmp_rect.center = tmp_rect.center[0] - c_x, tmp_rect.center[1] - c_y
            screen.blit(P_laser.to_blit, tmp_rect)
            distance = -52
            if P_laser.state == 0:
                distance = 0
            x, y = pos_by_distance_and_angle(P_laser.angle, 0, distance, Point(*tmp_rect.center))
            laser_collide_rect = pygame.Rect((x, y), (30, 30))
            laser_collide_rect.center = x, y
            pygame.draw.rect(screen, BLUE, laser_collide_rect, 4)


def main():
    init_settings()
    client_x_everything, game_server_ip = log_in()
    pygame.init()
    clock = pygame.time.Clock()
    P = ClientPlayer("Bob")
    Thread(target=handle_packet_from_game_server, args=(client_x_everything, P)).start()
    Thread(target=send_json_str_to_server, args=(client_x_everything, game_server_ip, P)).start()
    running = True
    while running:
        update_camera_cords(screen, P.collision_center)
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    pygame.quit()
                    client_x_everything.close()
                    sys.exit()
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_r:
                            P.reload()
                    if event.key in event_to_packet:
                        msg: dict = {
                            "cmd": "press",
                            "key_stroke": event_to_packet[event.key][0]
                        }
                        if event.key in list(event_to_packet.keys())[:2]:
                            P.x_dir = event_to_packet[event.key][1]
                        else:
                            P.y_dir = event_to_packet[event.key][1]
                        client_x_everything.sendto(json.dumps(msg).encode(), game_server_ip)
                        logging.debug("A key has been pressed and sent to the server")
                case pygame.KEYUP:
                    if event.key in event_to_packet:
                        msg: dict = {
                            "cmd": "release",
                            "key_stroke": event_to_packet[event.key][0]
                        }
                        if event.key in list(event_to_packet.keys())[:2]:
                            P.x_dir = 0
                        else:
                            P.y_dir = 0
                        client_x_everything.sendto(json.dumps(msg).encode(), game_server_ip)
                        logging.debug("A key has been released and sent to the server")
                case pygame.MOUSEBUTTONDOWN:
                    # client-sided
                    if event.button == pygame.BUTTON_LEFT:
                        c_x, c_y = get_camera_coordinates()
                        P.shoot(pygame.mouse.get_pos()[0] + c_x, pygame.mouse.get_pos()[1] + c_y)
        c_x, c_y = get_camera_coordinates()
        paint_map(screen)
        animate_player(P)
        display_players()  # This function is not fully operational, but it does the minimal job for the time being
        mouse_x, mouse_y = pygame.mouse.get_pos()
        blit_player(screen, P, math.atan2(mouse_y - P.collision_center.y + c_y, mouse_x - P.collision_center.x + c_x))
        move_all_lasers(P)
        clock.tick(60)
        pygame.display.update()


if __name__ == '__main__':
    main()
