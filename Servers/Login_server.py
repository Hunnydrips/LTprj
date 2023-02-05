import socket
import time

user_ips = []


def init_login_server() -> tuple:
    login_server_x_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    login_server_x_client.bind(("0.0.0.0", 8201))
    login_server_x_central_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    login_server_x_central_server.bind(("0.0.0.0", 8202))
    login_server_x_central_server.sendto("3!a".encode(), ("127.0.0.1", 8101))
    login_server_x_client.sendto("3!b".encode(), ("127.0.0.1", 8101))           # only time it has to access central_server
    return login_server_x_client, login_server_x_central_server


def handle_input_from_central(login_server_x_central_server: socket.socket()):
    # while True:
    data, ip = login_server_x_central_server.recvfrom(1024)
    data = data.decode()[1:-1].split(", ")
    user_ips.append((data[0][1:-1], int(data[1])))


def handle_input_from_client(login_server_x_client: socket.socket()):
    data, ip = login_server_x_client.recvfrom(1024)
    if ip in user_ips:
        print(data.decode())


def main():
    login_server_x_client, login_server_x_central_server = init_login_server()
    handle_input_from_central(login_server_x_central_server)
    handle_input_from_client(login_server_x_client)
    login_server_x_central_server.close()
    login_server_x_client.close()


if __name__ == '__main__':
    main()
