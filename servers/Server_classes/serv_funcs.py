from threading import Thread
import queue
import socket
import struct

packet_queue = queue.Queue()
ACTIVE_PLAYERS = {}
# DEMO_PLAYER = {"x": None, "y": None, "sock": None, "addr": None, "graphic_data": None}


def receive_packet(P_dict: dict):
    sock = P_dict["sock"]
    while not sock._closed:
        data, ip = sock.recvfrom(1024)
        if ip == P_dict["addr"]:
            packet_queue.put({"data": data, "player": P_dict})


def handle_packet_queue():
    while True:
        if not packet_queue.empty():
            Thread(target=handle_packet, args=(packet_queue.get(),)).start()


def handle_request_from_central(game_server_x_client: socket.socket, game_server_x_central_server: socket.socket):
    data = game_server_x_central_server.recvfrom(1024)[0].decode().split(", ")
    Thread(target=handle_request_from_central, args=(game_server_x_client, game_server_x_central_server)).start()
    addr = (data[0][2:-1], int(data[1][:-1]))
    new_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    new_player = {"x": 200, "y": 200, "sock": new_sock, "addr": addr, "graphic_data": None}
    ACTIVE_PLAYERS.update({addr: new_player})
    Thread(target=receive_packet, args=(new_player,)).start()


def handle_packet(packet: dict):
    player: dict = packet["player"]
    data: bytes = packet["data"]
    fmt_ = data.split(b"!")[0]
    struct_data = data[len(fmt_) + 1:]
    unpacked_data = struct.unpack(fmt_, struct_data)
    action_type = unpacked_data[0]
    match action_type:
        case b"new_loc":
            new_x, new_y = unpacked_data[1], unpacked_data[2]
            if abs(player["x"] - new_x) < 100 and abs(player["y"] - new_y) < 100:
                player["x"], player["y"] = new_x, new_y
        case b"graphic_data":
            player["graphic_data"] = unpacked_data[1]
        case b"shoot":
            pass
        case b"chat":
            pass
            