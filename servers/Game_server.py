from threading import Thread
from testing_field import Zone_server
from Server_classes.server_objects import *
from Server_classes.logic_functions import *
import logging
import socket
import json
import math
import time

ACTIVE_PLAYERS = []
BORDERS = [0]
IPS = []
ZONE_LIST = []
directions_x: dict = {b"right": 1, b"left": -1}
directions_y: dict = {b"up": -1, b"down": 1}


def init_game_server() -> tuple:
    game_server_x_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    game_server_x_client.bind(("0.0.0.0", 8301))
    game_server_x_central_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    game_server_x_central_server.bind(("0.0.0.0", 8302))
    game_server_x_central_server.sendto(b"XJ9", ("127.0.0.1", 8102))
    game_server_x_client.sendto(b"YJ9", ("127.0.0.1", 8102))
    return game_server_x_client, game_server_x_central_server


def receive_and_handle_request_from_central(game_server_x_client: socket.socket,
                                            game_server_x_central_server: socket.socket):
    data = game_server_x_central_server.recvfrom(1024)[0].decode().split(", ")
    Thread(target=receive_and_handle_request_from_central,
           args=(game_server_x_client, game_server_x_central_server)).start()
    IPS.append((data[0][2:-1], int(data[1][:-1])))
    ACTIVE_PLAYERS.append(ServerPlayer(data[2], (data[0][2:-1], int(data[1][:-1]))))
    ACTIVE_PLAYERS[-1].collision_center = Point(200, 200)


def receive_packet_from_player(game_server_x_client: socket.socket):
    while True:
        try:
            data, ip = game_server_x_client.recvfrom(1024)
            msg = json.loads(data.decode())
            print(msg)
            if ip not in IPS or msg["cmd"] == "begin":
                logging.debug("Packet has reached server and is now being filtered")
            P: ServerPlayer = ACTIVE_PLAYERS[IPS.index(ip)]
            match msg["cmd"]:
                case "press":
                    dir = msg["key_stroke"]
                    if dir in directions_x:
                        P.x_dir = directions_x[dir]
                    elif dir in directions_y:
                        P.y_dir = directions_y[dir]
                    elif dir == "reload":
                        pass
                case "release":
                    dir = msg["key_stroke"]
                    if dir in directions_x:
                        P.x_dir = 0
                    elif dir in directions_y:
                        P.y_dir = 0
                case "add":
                    P.json_str = msg["player_to_add"]
        except Exception as e:
            logging.debug("Exception found in receive_packet")


def init_zones(server_amount: int):
    for i in range(server_amount):
        ZONE_LIST.append(Zone_server.zone_server(9001 + i, 1920 * 5 * i, 0, 1920 * 5 * (i + 1), 1080 * 20))


def has_collision_with_borders(P: ServerPlayer, zone: Zone_server.zone_server) -> bool:
    return not (zone.top_left_pos.x + 1920 - 1 < P.collision_center.x < zone.bottom_right_pos.x - 1920 + 1)


def is_distribution_equal() -> bool:
    c = 0
    for zone in ZONE_LIST:
        c += zone.get_amount_of_players_in_zone()
    c /= 10
    for zone in ZONE_LIST:
        if zone.get_amount_of_players_in_zone() not in range(math.floor(c - 3), math.ceil(c + 3)):
            return False
    return True


def balance_load(lst: list, depth: int):
    if depth == 0:
        return
    new_x_border = lst[len(lst) // 2].collision_center.x + lst[len(lst) // 2 + 1].collision_center.x
    new_x_border /= 2
    BORDERS.append(new_x_border)
    balance_load(lst[:len(lst) // 2], depth - 1)
    balance_load(lst[len(lst) // 2 + 1:], depth - 1)


def balance_equaliser():
    if not is_distribution_equal():
        balance_load(ACTIVE_PLAYERS, 2)
        BORDERS.append(1920 * 20)
        BORDERS.sort()
        for i, b in enumerate(BORDERS[:-1]):
            ZONE_LIST[i].top_left_pos.x = b
            ZONE_LIST[i].bottom_right_pos.x = BORDERS[i + 1]
        x = len(BORDERS)
        for i in range(x):
            BORDERS.remove(BORDERS[i])
        BORDERS.append(0)


def move_player(game_server_x_client: socket.socket, P: ServerPlayer):
    while P in ACTIVE_PLAYERS:
        if P.x_dir or P.y_dir:
            if check_collision(P):
                if P.move():
                    time.sleep(.001)
                    msg = {
                        "cmd": 'move',
                        "pos": P.collision_center.to_tuple()
                    }
                    game_server_x_client.sendto(json.dumps(msg).encode(), P.address)


def main():
    game_server_x_client, game_server_x_central_server = init_game_server()
    receive_and_handle_request_from_central(game_server_x_client, game_server_x_central_server)
    Thread(target=receive_packet_from_player, args=(game_server_x_client,)).start()
    Thread(target=move_player, args=(game_server_x_client, ACTIVE_PLAYERS[-1])).start()
    while True:
        pass


if __name__ == '__main__':
    main()
