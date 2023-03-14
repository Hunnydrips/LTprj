import socket
from threading import Thread
from Classes import Player
from Classes import Zone_server
import math

ACTIVE_PLAYERS = []
BORDERS = [0]
IPS = []
ZONE_LIST = []


def init_game_server() -> tuple:
    game_server_x_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    game_server_x_client.bind(("0.0.0.0", 8301))
    game_server_x_central_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    game_server_x_central_server.bind(("0.0.0.0", 8302))
    game_server_x_central_server.sendto("XJ9".encode(), ("127.0.0.1", 8102))
    game_server_x_client.sendto("YJ9".encode(), ("127.0.0.1", 8102))
    return game_server_x_client, game_server_x_central_server


def handle_request_from_central(game_server_x_central_server) -> None:
    data = game_server_x_central_server.recvfrom(1024)[0].decode().split(", ")
    IPS.append((data[0][2:-1], int(data[1][:-1])))
    ACTIVE_PLAYERS.append(Player.player(data[2], (data[0][2:-1], int(data[1][:-1]))))
    Thread(target=handle_request_from_central, args=(game_server_x_central_server,)).start()


def handle_request_from_player(game_server_x_client) -> None:
    data, ip = game_server_x_client.recvfrom(1024)
    if ip not in IPS:
        Thread(target=handle_request_from_player, args=(game_server_x_client,)).start()
        return
    match data.decode():
        case "Begin":
            pass


def init_zones(server_amount: int) -> None:
    for i in range(server_amount):
        ZONE_LIST.append(Zone_server.zone_server(9001 + i, 1920 * 5 * i, 0, 1920 * 5 * (i + 1), 1080 * 20))


def has_collision_with_borders(player: Player.player, zone: Zone_server.zone_server) -> bool:
    return not (zone.top_left_pos.x + 1920 - 1 < player.pos.x < zone.bottom_right_pos.x - 1920 + 1)


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


def get_x_of_player(player: Player.player) -> int:
    return player.pos.x


def main():
    game_server_x_client, game_server_x_central_server = init_game_server()
    handle_request_from_central(game_server_x_central_server)
    handle_request_from_player(game_server_x_client)


if __name__ == '__main__':
    main()
