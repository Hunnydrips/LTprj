import socket
from threading import Thread

ACTIVE_USERS = []
USERNAMES = []


def init_game_server() -> tuple:
    game_server_x_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    game_server_x_client.bind(("0.0.0.0", 8301))
    game_server_x_central_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    game_server_x_central_server.bind(("0.0.0.0", 8302))
    game_server_x_central_server.sendto("XJ9".encode(), ("127.0.0.1", 8102))
    game_server_x_client.sendto("YJ9".encode(), ("127.0.0.1", 8102))
    return game_server_x_client, game_server_x_central_server


def handle_request_from_central(game_server_x_central_server):
    data = game_server_x_central_server.recvfrom(1024)[0].decode().split(", ")
    ACTIVE_USERS.append((data[0][2:-1], int(data[1][:-1])))
    USERNAMES.append(data[2])
    Thread(target=handle_request_from_central, args=(game_server_x_central_server, )).start()


def handle_request_from_player(game_server_x_client):
    data, ip = game_server_x_client.recvfrom(1024)
    if ip not in ACTIVE_USERS:
        Thread(target=handle_request_from_player, args=(game_server_x_client, )).start()
        return
    match data.decode():
        case "Begin":
            print(USERNAMES[ACTIVE_USERS.index(ip)], "is starting to play")


def main():
    game_server_x_client, game_server_x_central_server = init_game_server()
    handle_request_from_central(game_server_x_central_server)
    handle_request_from_player(game_server_x_client)


if __name__ == '__main__':
    main()
