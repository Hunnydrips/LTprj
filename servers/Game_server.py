from threading import Thread
from Server_classes.logic_functions import *
from typing import Tuple
import logging
import socket
import json

ADDR = Tuple[str, int]
ACTIVE_PLAYERS_DICT: dict[ADDR, ServerPlayer] = {}
CENTRAL_ADDR: tuple = ("127.0.0.1", 8102)
STATIC_PORT: int = 8302
DEFAULT_IP: str = "0.0.0.0"

directions_x: dict = {
    "right": 1,
    "left": -1
}

directions_y: dict = {
    "up": -1,
    "down": 1
}

logging.basicConfig(level=logging.DEBUG)


def init_game_server() -> socket.socket:
    """
    Initialise the game and client socket that is unique per player
    :return: game server and client socket
    """
    global STATIC_PORT
    game_server_x_client: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # game server socket
    logging.info((DEFAULT_IP, STATIC_PORT))
    game_server_x_client.bind((DEFAULT_IP, STATIC_PORT))
    STATIC_PORT += 1
    return game_server_x_client


def send_initial_signals(game_server_x_central_server: socket.socket, game_server_x_client: socket.socket):
    """
    A function separated so to send initial codes to resume code
    :param game_server_x_central_server: game server and central server socket
    :param game_server_x_client: game server and client socket
    :return: Nothing
    """
    game_server_x_central_server.sendto(b"XJ9", CENTRAL_ADDR)
    game_server_x_client.sendto(b"YJ9", CENTRAL_ADDR)


def receive_and_handle_request_from_central(game_server_x_central_server: socket.socket) -> socket.socket:
    """
    Handle packet from central server
    :param game_server_x_central_server: game server and central server socket
    :return: starting game-threads and Nothing else
    """
    game_server_x_client = init_game_server()
    send_initial_signals(game_server_x_central_server=game_server_x_central_server, game_server_x_client=game_server_x_client)
    data: list = game_server_x_central_server.recvfrom(1024)[0].decode().split(", ")
    Thread(target=receive_and_handle_request_from_central, args=(game_server_x_central_server,)).start()
    address: tuple[str, int] = (data[0][2:-1], int(data[1][:-1]))
    P: ServerPlayer = ServerPlayer(username=data[2], address=address, sock=game_server_x_client)
    ACTIVE_PLAYERS_DICT[address] = P
    P.collision_center = Point(200, 200)
    # Thread(target=check_player_pos_validity, args=(P.personal_game_sock, P)).start()
    Thread(target=update_player_images_for_clients, args=(P.personal_game_sock, P)).start()
    return game_server_x_client


def handle_packet_from_player(game_server_x_client: socket.socket):
    """
    Handle packets from various clients using numeral sockets
    :param game_server_x_client: a unique game server and client socket
    :return: Nothing
    """
    while True:
        try:
            data, ip = game_server_x_client.recvfrom(1024)
            msg = json.loads(data.decode())
            print(msg)
            if ip not in ACTIVE_PLAYERS_DICT or msg["cmd"] == "begin":
                logging.debug("Packet has now reached server and is now being filtered")
            P: ServerPlayer = ...
            try:
                P: ServerPlayer = ACTIVE_PLAYERS_DICT[ip]
            except Exception as e:
                logging.debug(f"An exception has occurred {e}")
            match msg["cmd"]:
                case "press":
                    direction = msg["key_stroke"]
                    if direction in directions_x:
                        P.x_dir = directions_x[direction]
                    elif direction in directions_y:
                        P.y_dir = directions_y[direction]
                    elif direction == "reload":
                        logging.debug("No need to do here anything apart from catch the case")
                    else:
                        logging.debug("Key is not in list, ignoring keystroke")
                case "release":
                    direction = msg["key_stroke"]
                    if direction in directions_x:
                        P.x_dir = 0
                    elif direction in directions_y:
                        P.y_dir = 0
                case "add":
                    json_str: JSONStr = json.loads(msg["player_to_add"])  # had to turn it into a dictionary

                    P.update_queue.append(json_str)
                case "show_proj":
                    L: ServerLaser = ServerLaser(*msg['start_coordinates'], *msg['target_coordinates'])
                    send_laser_info_to_clients(P=P, L=L)
                case _:
                    pass
        except Exception as e:
            logging.debug(f"Exception found in handle_packet, error code: {e}")


def delete_player(P: ServerPlayer):
    del ACTIVE_PLAYERS_DICT[P.address]  # removed player from active list
    msg: dict = {
        "cmd": "disconnect"
    }
    P.personal_game_sock.sendto(json.dumps(msg).encode(), P.address)  # closing player's game


def check_bounds(P1: ServerPlayer, P2: ServerPlayer) -> bool:
    """
    Checks the bounds of two players in sight
    :param P1: First player
    :param P2: Second player
    :return: ...
    """
    return abs(P1.collision_center.x - P2.collision_center.x) < 1920 and abs(P1.collision_center.y - P2.collision_center.y) < 1080


def update_player_images_for_clients(game_server_x_client: socket.socket, P: ServerPlayer):
    """
    Update player images nearby other players
    :param game_server_x_client: every game server and client socket
    :param P: every player object
    :return: Nothing
    """
    msg = {
        "cmd": "load"
    }
    while True:
        if not P.update_queue:
            time.sleep(0)
            if not P.online:
                return  # end thread since player disconnected
            continue
        json_str: JSONStr = P.update_queue.popleft()
        if not P.check_validity(tuple(json_str["pos"])):
            delete_player(P)
            return
        for player in ACTIVE_PLAYERS_DICT.values():
            if check_bounds(P, player) and player != P:
                msg["json_str"] = json_str
                game_server_x_client.sendto(json.dumps(msg).encode(), player.address)


def send_laser_info_to_clients(P: ServerPlayer, L: ServerLaser):
    """
    A function whose purpose is to send laser information to all clients in sight
    :param P: The player who has sent the information
    :param L: The laser corresponding to the one that should be printed
    :return: Nothing
    """
    msg: dict = {
        "cmd": "show_laser",
        "start_coordinates": (L.x, L.y),
        "target_coordinates": (L.target_x, L.target_y)
    }
    data = json.dumps(msg).encode()
    for player in ACTIVE_PLAYERS_DICT.values():
        if player is not P:
            player.personal_game_sock.sendto(data, player.address)


def main():
    game_server_x_central_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    game_server_x_central_server.bind((DEFAULT_IP, STATIC_PORT - 1))
    game_server_x_client: socket.socket = ...
    running = True
    while running:
        game_server_x_client: socket.socket = receive_and_handle_request_from_central(game_server_x_central_server)
        Thread(target=handle_packet_from_player, args=(game_server_x_client,)).start()
    game_server_x_client.close()
    game_server_x_central_server.close()


if __name__ == '__main__':
    main()
