from threading import Thread
from Server_classes.logic_functions import *
import logging
import socket
import json

ACTIVE_PLAYERS: list = []
IPS: list = []
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
    Thread(target=receive_and_handle_request_from_central, args=(game_server_x_client, game_server_x_central_server)).start()
    address: tuple[str, int] = (data[0][2:-1], int(data[1][:-1]))
    IPS.append(address)
    P: ServerPlayer = ServerPlayer(username=data[2], address=address, sock=game_server_x_client)
    ACTIVE_PLAYERS.append(P)
    ACTIVE_PLAYERS[-1].collision_center = Point(200, 200)
    Thread(target=check_player_pos_validity, args=(P.personal_game_sock, ACTIVE_PLAYERS[-1])).start()
    Thread(target=update_player_images_for_clients, args=(P.personal_game_sock, ACTIVE_PLAYERS[-1])).start()
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
            if ip not in IPS or msg["cmd"] == "begin":
                logging.debug("Packet has now reached server and is now being filtered")
            P: ServerPlayer | Ellipsis = ...
            L: ServerLaser | Ellipsis = ...
            try:
                P: ServerPlayer = ACTIVE_PLAYERS[IPS.index(ip)]  # problem is here, player might not exist due to removal in anti-cheat
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
                    json_str: dict = json.loads(msg["player_to_add"])  # had to turn it into a dictionary
                    if json_str:
                        P.json_str = json_str
                    print(P.json_str)
                case "show_proj":
                    L: ServerLaser = ServerLaser(*msg['start_coordinates'], *msg['target_coordinates'])
                    send_laser_info_to_clients(P=P, L=L)
                case _:
                    pass
        except Exception as e:
            logging.debug(f"Exception found in handle_packet, error code: {e}")


def check_player_pos_validity(game_server_x_client: socket.socket, P: ServerPlayer):
    """
    Prevents players from jumping and operating inconspicuous teleportation
    :param game_server_x_client: socket that contains connection between game server and client
    :param P: every player object
    :return: Nothing
    """
    while P in ACTIVE_PLAYERS:
        if P.x_dir or P.y_dir:
            if check_collision(P):
                if P.move() and P.json_str:
                    client_x, client_y = P.json_str["pos"]
                    if abs(client_x - P.collision_center.x) >= 16000 or abs(client_y - P.collision_center.y) >= 9000:
                        logging.debug(f"Player has made a ridiculous jump and should be disconnected for it!!!\nPlayer name: {P.json_str['name']}\n")
                        ACTIVE_PLAYERS.remove(P)  # removed player from active list
                        IPS.remove(P.address)  # removed ip from IP list
                        msg: dict = {
                            "cmd": "disconnect"
                        }
                        game_server_x_client.sendto(json.dumps(msg).encode(), P.address)  # closing player's game


def update_player_images_for_clients(game_server_x_client: socket.socket, P: ServerPlayer):
    """
    Update player images nearby other players
    :param game_server_x_client: every game server and client socket
    :param P: every player object
    :return: Nothing
    """
    prev_angle: float = 0
    prev_sprite: int = 0
    changed_condition: bool = False
    while P in ACTIVE_PLAYERS:
        msg: dict = {
            "cmd": "load",
            "json_strs": []
        }
        for i, player in enumerate(ACTIVE_PLAYERS):
            if abs(player.collision_center.x - P.collision_center.x) < 1920 and abs(player.collision_center.y - P.collision_center.y) < 1080 and player is not P and player.json_str:
                if player.json_str not in msg["json_strs"]:
                    msg["json_strs"].append(player.json_str)
                if prev_angle != player.json_str['angle'] and prev_sprite != player.json_str['current_sprite']:
                    new_angle: float = player.json_str['angle']
                    new_sprite: int = player.json_str['current_sprite']
                    try:
                        msg["json_strs"][i]['angle'] = new_angle
                        msg["json_strs"][i]['current_sprite'] = new_sprite
                    except IndexError or Exception as e:
                        logging.warning(f"Don't mind the Index error or the potential {e}\n")
                        logging.info("Small thing that doesn't need to be taken care of")
                    finally:
                        prev_angle = new_angle
                        prev_sprite = new_sprite
                        changed_condition = True
        try:
            if len(msg["json_strs"]) and changed_condition:
                logging.debug(f"{changed_condition}")
                game_server_x_client.sendto(json.dumps(msg).encode(), P.address)
                changed_condition = False
        except Exception as e:
            logging.debug(f"An error occurred trying to send graphics to players, error {e}")
        finally:
            time.sleep(.001)  # a bit of waiting so to not entirely flood subnet


def send_laser_info_to_clients(P: ServerPlayer, L: ServerLaser):
    """
    A function whose purpose is to send laser information to all clients in sight
    :param P: The player who has sent the information
    :param L: The laser corresponding to the one that should be printed
    :return: Nothing
    """
    for player in ACTIVE_PLAYERS:
        if abs(player.collision_center.x - P.collision_center.x) < 1920 * 3 and abs(player.collision_center.y - P.collision_center.y) < 1080 * 3 and player is not P:
            msg: dict = {
                "cmd": "show_laser",
                "start_coordinates": (L.x, L.y),
                "target_coordinates": (L.target_x, L.target_y)
            }
            player.personal_game_sock.sendto(json.dumps(msg).encode(), player.address)


def main():
    game_server_x_central_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    game_server_x_central_server.bind((DEFAULT_IP, STATIC_PORT - 1))
    game_server_x_client: socket.socket | Ellipsis = ...
    running = True
    while running:
        game_server_x_client: socket.socket = receive_and_handle_request_from_central(game_server_x_central_server)
        Thread(target=handle_packet_from_player, args=(game_server_x_client,)).start()
    game_server_x_client.close()
    game_server_x_central_server.close()


if __name__ == '__main__':
    main()
