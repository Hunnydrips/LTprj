import socket
import math
import struct
import time
from threading import Thread
from Server_classes.server_objects import *
from testing_field import Zone_server

ACTIVE_PLAYERS = []
BORDERS = [0]
IPS = []
ZONE_LIST = []
directions_x: dict = {"right": 1, "left": -1}
directions_y: dict = {"up": -1, "down": 1}


def init_game_server() -> tuple:
    game_server_x_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    game_server_x_client.bind(("0.0.0.0", 8301))
    game_server_x_central_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    game_server_x_central_server.bind(("0.0.0.0", 8302))
    game_server_x_central_server.sendto("XJ9".encode(), ("127.0.0.1", 8102))
    game_server_x_client.sendto("YJ9".encode(), ("127.0.0.1", 8102))
    return game_server_x_client, game_server_x_central_server


def handle_request_from_central(game_server_x_client: socket.socket, game_server_x_central_server: socket.socket):
    data = game_server_x_central_server.recvfrom(1024)[0].decode().split(", ")
    Thread(target=handle_request_from_central, args=(game_server_x_client, game_server_x_central_server)).start()
    IPS.append((data[0][2:-1], int(data[1][:-1])))
    ACTIVE_PLAYERS.append(player(data[2], (data[0][2:-1], int(data[1][:-1]))))
    Thread(target=move_player, args=(game_server_x_client, ACTIVE_PLAYERS[-1])).start()


def handle_request_from_player(game_server_x_client: socket.socket):
    data, ip = game_server_x_client.recvfrom(1024)
    Thread(target=handle_request_from_player, args=(game_server_x_client,)).start()
    data = data.decode()
    if ip not in IPS or data == "Begin":
        return
    P = ACTIVE_PLAYERS[IPS.index(ip)]
    action_type, direction = data.split(" ")
    match action_type:
        case "press":
            if direction in directions_x:
                P.x_dir = directions_x[direction]
            else:
                P.y_dir = directions_y[direction]
        case "release":
            if direction in directions_x:
                P.x_dir = 0
            else:
                P.y_dir = 0


def init_zones(server_amount: int):
    for i in range(server_amount):
        ZONE_LIST.append(Zone_server.zone_server(9001 + i, 1920 * 5 * i, 0, 1920 * 5 * (i + 1), 1080 * 20))


def has_collision_with_borders(P: player, zone: Zone_server.zone_server) -> bool:
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


def move_player(game_server_x_client: socket.socket, P: player):
    while P in ACTIVE_PLAYERS:
        if P.x_dir or P.y_dir:
            if P.move():
                to_send = b'cii$$' + struct.pack("cii", "M".encode(), *P.collision_center.to_tuple())
                game_server_x_client.sendto(to_send, P.address)


def main():
    game_server_x_client, game_server_x_central_server = init_game_server()
    handle_request_from_central(game_server_x_client, game_server_x_central_server)
    handle_request_from_player(game_server_x_client)
    while True:
        pass


if __name__ == '__main__':
    main()
