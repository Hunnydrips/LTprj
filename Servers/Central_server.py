import socket
from threading import Thread


def init_central_server() -> tuple:
    central_server_x_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    central_server_x_client.bind(("0.0.0.0", 8100))
    central_server_x_login_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    central_server_x_login_server.bind(("0.0.0.0", 8101))
    return central_server_x_client, central_server_x_login_server


def connect_to_login(central_server_x_login_server: socket.socket()):
    login_ip_for_server = ""
    login_ip_for_client = ""
    while not login_ip_for_server or not login_ip_for_client:
        (data, ip) = central_server_x_login_server.recvfrom(1024)
        match data.decode():
            case "3!a":
                login_ip_for_server = ip
            case "3!b":
                login_ip_for_client = ip
    return login_ip_for_client, login_ip_for_server


def handle_request(central_server_x_client: socket.socket(), central_server_x_login_server: socket.socket(), log_serv_ip_for_server: tuple, log_serv_ip_for_clients: tuple):
    # while True:
    data, ip = central_server_x_client.recvfrom(1024)
    print(data, ip)
    if data.decode() == "log_requested":
        central_server_x_login_server.sendto(str(ip).encode(), log_serv_ip_for_server)
        central_server_x_client.sendto(str(log_serv_ip_for_clients).encode(), ip)
    Thread(target=handle_request, args=(central_server_x_client, central_server_x_login_server, log_serv_ip_for_server, log_serv_ip_for_clients)).start()


def main():
    central_server_x_client, central_server_x_login_server = init_central_server()
    client_ip, login_serv_ip = connect_to_login(central_server_x_login_server)
    handle_request(central_server_x_client, central_server_x_login_server, login_serv_ip, client_ip)
    while True:
        pass
    central_server_x_client.close()
    central_server_x_login_server.close()


if __name__ == '__main__':
    main()
