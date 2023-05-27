from threading import Thread
import socket
import logging

logging.basicConfig(level=logging.DEBUG)
BASE_PORT: int = 8100


def init_central_server() -> tuple:
    """
    Initialises every socket
    :return: A tuple of the three necessitated sockets for the game
    """
    central_server_x_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    central_server_x_client.bind(("0.0.0.0", BASE_PORT))
    central_server_x_login_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    central_server_x_login_server.bind(("0.0.0.0", BASE_PORT + 1))
    central_server_x_game_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    central_server_x_game_server.bind(("0.0.0.0", BASE_PORT + 2))
    return central_server_x_client, central_server_x_login_server, central_server_x_game_server


def connect_to_login(central_server_x_login_server: socket.socket) -> tuple:
    """
    Main connection line to log-in server
    :param central_server_x_login_server: central server and login server socket
    :return: IPS of client and server in relation to log-in
    """
    login_ip_for_server, login_ip_for_client = "", ""
    while not login_ip_for_server or not login_ip_for_client:
        data, ip = central_server_x_login_server.recvfrom(1024)
        match data:
            case b"3!a":
                login_ip_for_server: tuple | str = ip
            case b"3!b":
                login_ip_for_client: tuple | str = ip
    return login_ip_for_client, login_ip_for_server


def connect_to_game(central_server_x_game_server: socket.socket) -> tuple:
    """
    Main connection line to game server
    :param central_server_x_game_server: central server and game server socket
    :return: IPS of client and server in relation to game server
    """
    game_ip_for_server, game_ip_for_client = "", ""
    while not game_ip_for_server or not game_ip_for_client:
        data, ip = central_server_x_game_server.recvfrom(1024)
        match data:
            case b"XJ9":
                game_ip_for_server: tuple | str = ip
            case b"YJ9":
                game_ip_for_client: tuple | str = ip
    Thread(target=connect_to_game, args=(central_server_x_game_server,)).start()  # thread for each game_x_client socket created
    return game_ip_for_client, game_ip_for_server


def handle_packet_from_client(central_server_x_client: socket.socket, central_server_x_login_server: socket.socket,
                              log_serv_ip_for_server: tuple, log_serv_ip_for_clients: tuple):
    """
    Handle client packets generally
    :param central_server_x_client: central server and client socket
    :param central_server_x_login_server: central server and login server socket
    :param log_serv_ip_for_server: login server ip for central
    :param log_serv_ip_for_clients: login server ip for clients
    :return: Nothing
    """
    print(log_serv_ip_for_server)
    while True:
        data, client_ip = central_server_x_client.recvfrom(1024)
        logging.debug(f"User has entered, details: {data, client_ip}")
        if data == b"log_requested":
            central_server_x_login_server.sendto(str(client_ip).encode(), log_serv_ip_for_server)
            central_server_x_client.sendto(str(log_serv_ip_for_clients).encode(), client_ip)


def handle_packet_from_login_server(central_server_x_login_server: socket.socket, central_server_x_game_server: socket.socket, central_server_x_client: socket.socket,
                                    game_serv_ip_for_server: tuple, game_serv_ip_for_clients: tuple):
    """
    Handle packets coming specifically from the login server for players, nice isolation
    :param central_server_x_login_server: central server and login server socket
    :param central_server_x_game_server: central server and game server socket
    :param central_server_x_client: central server and client socket
    :param game_serv_ip_for_server: game server ip for central
    :param game_serv_ip_for_clients: game server ip for clients
    :return: Nothing
    """
    data = central_server_x_login_server.recvfrom(1024)[0].decode()
    if data.startswith("This user has been verified, "):
        data = data[30:].replace("'", "").replace(")", "")
        data = data.split(", ")
        client_ip = (data[0], int(data[1]))
        central_server_x_game_server.sendto(f"{client_ip}, {data[2]}".encode(), game_serv_ip_for_server)
        central_server_x_client.sendto(str(game_serv_ip_for_clients).encode(), client_ip)
    Thread(target=handle_packet_from_login_server, args=(
        central_server_x_login_server, central_server_x_game_server, central_server_x_client, game_serv_ip_for_server, game_serv_ip_for_clients)).start()


def main():
    central_server_x_client, central_server_x_login_server, central_server_x_game_server = init_central_server()
    login_serv_ip_for_client, login_serv_ip = connect_to_login(central_server_x_login_server)
    Thread(target=handle_packet_from_client, args=(central_server_x_client, central_server_x_login_server, login_serv_ip, login_serv_ip_for_client)).start()
    game_serv_ip_for_client, game_serv_ip = connect_to_game(central_server_x_game_server)
    handle_packet_from_login_server(central_server_x_login_server, central_server_x_game_server, central_server_x_client, game_serv_ip, game_serv_ip_for_client)
    while True:
        pass  # let the main thread run by
    central_server_x_client.close()
    central_server_x_login_server.close()
    central_server_x_game_server.close()


if __name__ == '__main__':
    main()
