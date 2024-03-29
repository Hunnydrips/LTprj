from threading import Thread
from servers.Server_classes.logic_functions import check_collision
from Client_classes.graphic_functions import *
from Client_classes.client_objects import *
from pygame.locals import *
from typing import Dict
import pygame
import socket
import logging
import json
import sys
import login_gui

NAME = str

event_to_packet: dict = {
    pygame.K_d: ["right", 1],
    pygame.K_a: ["left", -1],
    pygame.K_w: ["up", -1],
    pygame.K_s: ["down", 1],
}

enemy_player_dict: Dict[NAME, ClientPlayer] = {}

CENTRAL_PORT: int = 8100
LOCAL_HOST: str = "127.0.0.1"
players_to_display: list = []
CENTRAL_ADDR: tuple = (LOCAL_HOST, CENTRAL_PORT)
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


def log_in() -> tuple[socket.socket, tuple[str, int]]:  # connection to central so to have the ip of login server
    """
    Log-in function, separates duality and accepts players
    :return: Player socket and game server address
    """
    client_x_everything: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_x_everything.bind(("0.0.0.0", int(sys.argv[2])))
    client_x_everything.sendto(b"log_requested", CENTRAL_ADDR)
    data = client_x_everything.recvfrom(1024)[0].decode()[1:-1].split(", ")
    login_server_ip: tuple = (data[0][1:-1], int(data[1]))
    while not log_in_or_sign_up(client_x_everything, login_server_ip):
        logging.info("Waiting for somebody to connect")
    logging.info("Logged in successfully")
    data: list = client_x_everything.recvfrom(1024)[0].decode()[1:-1].split(", ")
    game_server_ip: tuple = (data[0][1:-1], int(data[1]))
    msg: dict = {
        "cmd": "begin"
    }
    client_x_everything.sendto(json.dumps(msg).encode(), game_server_ip)
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
        print(name_hash)
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


def handle_packet_from_game_server(P: ClientPlayer):
    """
    Handle packets coming from game server
    :param P: player object
    :return: Nothing
    """
    while True:
        data, ip = P.client_sock.recvfrom(1024)
        msg = json.loads(data.decode())
        print(msg)
        match msg["cmd"]:
            case "load":
                attr_dict: dict = msg["json_str"]  # json_str is already in dictionary form
                name: str = attr_dict["name"]
                if name == P.username:
                    continue
                if name not in enemy_player_dict:
                    player_to_display: ClientPlayer = ClientPlayer(
                        username=attr_dict["name"],
                        pos=Point(*attr_dict["pos"]),
                        status=attr_dict["status"],
                        angle=attr_dict["angle"] / -180 * math.pi
                    )
                    player_to_display.animations[player_to_display.status].current_sprite = attr_dict["current_sprite"]
                    enemy_player_dict[name] = player_to_display
                    continue
                update_attributes(attrs=attr_dict)
            case "show_laser":
                laser_to_show = ClientLaser(*msg['start_coordinates'], *msg['target_coordinates'])
                P.lasers.append(laser_to_show)
                move_all_lasers(P)
            case "disconnect":
                logging.info("Player should now be disconnected")
                shutdown_client(client_x_everything=P.client_sock)


def update_attributes(attrs: dict):
    player = enemy_player_dict[attrs['name']]
    player.angle = attrs['angle'] / -180 * math.pi
    player.collision_center = Point(*attrs['pos'])
    player.status = attrs['status']


def display_players():
    """
    Minor shortening so to explain work and endeavour, consider errors in this funcs that may happen and how to handle them
    :return: Nothing
    """
    for player in enemy_player_dict.values():
        try:
            animate_player(P=player)
            tmp_angle = player.angle  # angle changes in the process, I've got to have a copy
            blit_player(screen=screen, P=player, angle=player.angle)
            player.angle = tmp_angle
            move_all_lasers(P=player)
        except pygame.error or Exception as e:
            print(e)


def send_json_str_to_server(game_server_ip: tuple, P: ClientPlayer):
    """
    Send player details to server so to have a connected game with all players available
    :param game_server_ip: game server socket and ip
    :param P: player object
    :return: Nothing
    """
    prev_angle: float = P.angle
    prev_pos: tuple = P.collision_center.to_tuple()
    while True:
        current_pos = P.collision_center.to_tuple()
        if not (prev_angle != P.angle or prev_pos != current_pos):
            time.sleep(0)
            continue

        player_attr: dict = {
            "pos": current_pos,
            "angle": P.angle,
            "status": P.status,
            "name": P.username,
            "current_sprite": P.animations[P.status].current_sprite
        }

        packet_data = json.dumps(player_attr)
        msg: dict = {
            "cmd": "add",
            "player_to_add": packet_data
        }

        P.client_sock.sendto(json.dumps(msg).encode(), game_server_ip)
        prev_angle = P.angle
        prev_pos = current_pos


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


def shutdown_client(client_x_everything: socket.socket):
    """
    A three liner consisting the end of the programme
    :param client_x_everything: a socket that connects the client with the necessary servers
    :return: Nothing
    """
    client_x_everything.close()
    pygame.quit()
    sys.exit()


def main():
    init_settings()
    pygame.init()
    client_x_everything, game_server_ip = log_in()
    clock = pygame.time.Clock()
    assert len(sys.argv) > 2
    P: ClientPlayer = ClientPlayer(username=sys.argv[1], sock=client_x_everything)
    Thread(target=handle_packet_from_game_server, args=(P,)).start()
    Thread(target=send_json_str_to_server, args=(game_server_ip, P)).start()
    while True:
        update_camera_cords(screen, P.collision_center)
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    shutdown_client(client_x_everything=P.client_sock)
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
                        P.client_sock.sendto(json.dumps(msg).encode(), game_server_ip)
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
                        P.client_sock.sendto(json.dumps(msg).encode(), game_server_ip)
                        logging.debug("A key has been released and sent to the server")
                case pygame.MOUSEBUTTONDOWN:
                    if event.button == pygame.BUTTON_LEFT:
                        c_x, c_y = get_camera_coordinates()
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        laser = P.shoot(mouse_x + c_x, mouse_y + c_y)
                        if laser is not None:
                            msg: dict = {
                                "cmd": "show_proj",
                                "start_coordinates": (laser.x, laser.y),
                                "target_coordinates": (mouse_x, mouse_y)
                            }
                            P.client_sock.sendto(json.dumps(msg).encode(), game_server_ip)
        if check_collision(P=P):
            P.move()  # REMOVES STUTTERING BUG!!!
        c_x, c_y = get_camera_coordinates()
        paint_map(screen=screen)
        animate_player(P=P)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        blit_player(screen=screen, P=P, angle=math.atan2(mouse_y - P.collision_center.y + c_y, mouse_x - P.collision_center.x + c_x))
        display_players()
        move_all_lasers(P=P)
        clock.tick(60)
        pygame.display.update()


if __name__ == '__main__':
    main()
