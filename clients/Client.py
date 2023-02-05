import socket


def conn():
    client_x_everything = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_x_everything.sendto("log_requested".encode(), ("127.0.0.1", 8100))
    data = client_x_everything.recvfrom(1024)[0].decode()[1:-1].split(", ")
    login_server_ip = (data[0][1:-1], int(data[1]))
    client_x_everything.sendto("sigma f = ma".encode(), login_server_ip)


def main():
    conn()


if __name__ == '__main__':
    main()
