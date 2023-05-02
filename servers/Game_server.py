from threading import Thread
from Server_classes.logic_functions import *
import logging
import socket
import json
import time

ACTIVE_PLAYERS = []
IPS = []
CENTRAL_ADDR = ("127.0.0.1", 8102)
directions_x: dict = {"right": 1, "left": -1}
directions_y: dict = {"up": -1, "down": 1}
logging.basicConfig(level=logging.DEBUG)


def init_game_server() -> tuple:
    """
    Initialise :D
    :return: game server and client socket, game server and central server socket
    """
    game_server_x_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    game_server_x_client.bind(("0.0.0.0", 8301))
    game_server_x_central_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    game_server_x_central_server.bind(("0.0.0.0", 8302))
    game_server_x_central_server.sendto(b"XJ9", CENTRAL_ADDR)
    game_server_x_client.sendto(b"YJ9", CENTRAL_ADDR)
    return game_server_x_client, game_server_x_central_server


def receive_and_handle_request_from_central(game_server_x_client: socket.socket(), game_server_x_central_server: socket.socket()):
    """
    Handle packet from central
    :param game_server_x_client: game server and client socket
    :param game_server_x_central_server: game server and central server socket
    :return: Starting threads and Nothing else
    """
    data = game_server_x_central_server.recvfrom(1024)[0].decode().split(", ")
    Thread(target=receive_and_handle_request_from_central, args=(game_server_x_client, game_server_x_central_server)).start()
    IPS.append((data[0][2:-1], int(data[1][:-1])))
    ACTIVE_PLAYERS.append(ServerPlayer(data[2], (data[0][2:-1], int(data[1][:-1]))))
    ACTIVE_PLAYERS[-1].collision_center = Point(200, 200)
    Thread(target=update_pos_for_clients, args=(game_server_x_client, ACTIVE_PLAYERS[-1])).start()
    Thread(target=update_player_images_for_clients, args=(game_server_x_client, ACTIVE_PLAYERS[-1])).start()


def handle_packet_from_player(game_server_x_client: socket.socket()):
    """
    Handle packets from various clients
    :param game_server_x_client: game server and client socket
    :return: Nothing
    """
    while True:
        try:
            data, ip = game_server_x_client.recvfrom(1024)
            msg = json.loads(data.decode())
            print(msg)
            if ip not in IPS or msg["cmd"] == "begin":
                logging.debug("Packet has now reached server and is now being filtered")
            P: ServerPlayer = ACTIVE_PLAYERS[IPS.index(ip)]
            match msg["cmd"]:
                case "press":
                    direction = msg["key_stroke"]
                    if direction in directions_x:
                        P.x_dir = directions_x[direction]
                    elif direction in directions_y:
                        P.y_dir = directions_y[direction]
                    elif direction == "reload":
                        pass
                    else:
                        logging.debug("Key is not in list, ignoring keystroke")
                case "release":
                    direction = msg["key_stroke"]
                    if direction in directions_x:
                        P.x_dir = 0
                    elif direction in directions_y:
                        P.y_dir = 0
                case "add":
                    P.json_str = msg["player_to_add"]
                    print(P.json_str)
        except Exception as e:
            logging.debug(f"Exception found in receive_packet, error code: {e}")


def update_pos_for_clients(game_server_x_client: socket.socket(), P: ServerPlayer):
    """
    Update locations for each pos player packet
    :param game_server_x_client: every game server and client socket
    :param P: every player object
    :return: Nothing
    """
    while P in ACTIVE_PLAYERS:
        if P.x_dir or P.y_dir:
            if check_collision(P):
                if P.move():
                    time.sleep(.001)
                    msg: dict = {
                        "cmd": 'move',
                        "pos": P.collision_center.to_tuple()
                    }
                    game_server_x_client.sendto(json.dumps(msg).encode(), P.address)


def update_player_images_for_clients(game_server_x_client: socket.socket(), P: ServerPlayer):
    """
    Update player images nearby other players
    :param game_server_x_client: every game server and client socket
    :param P: every player object
    :return: Nothing
    """
    while P in ACTIVE_PLAYERS:
        msg: dict = {
            "cmd": "load",
            "json_strs": []
        }
        for player in ACTIVE_PLAYERS:
            if abs(player.collision_center.x - P.collision_center.x) < 700 and abs(player.collision_center.y - P.collision_center.y) < 700 and player is not P and player.json_str:
                msg["json_strs"].append(player.json_str)
        try:
            if len(msg["json_strs"]):
                game_server_x_client.sendto(json.dumps(msg).encode(), P.address)
        except Exception as e:
            logging.debug(f"An error occurred trying to send json_strs to players, error {e}")
        finally:
            time.sleep(.001)


def main():
    game_server_x_client, game_server_x_central_server = init_game_server()
    receive_and_handle_request_from_central(game_server_x_client, game_server_x_central_server)
    Thread(target=handle_packet_from_player, args=(game_server_x_client,)).start()
    while True:
        pass


if __name__ == '__main__':
    main()
