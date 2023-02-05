import socket
import hashlib


def conn():
    client_x_everything = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_x_everything.sendto("log_requested".encode(), ("127.0.0.1", 8100))
    data = client_x_everything.recvfrom(1024)[0].decode()[1:-1].split(", ")
    login_server_ip = (data[0][1:-1], int(data[1]))
    log_in_or_sign_up(client_x_everything, login_server_ip)
    return client_x_everything, login_server_ip


def log_in_or_sign_up(client_x_everything: socket.socket(), login_server_ip):
    name_hash, password_hash, flag = "", "", ""
    with open("settings.txt", 'r') as f:
        data = f.read().split("\n")
        print(data)
    if data[0] == "true":
        name_hash, password_hash, flag = data[1], data[2], "log_in"
    else:
        name_hash = hashlib.sha256(input("Enter username: ").encode()).hexdigest()
        password_hash = hashlib.sha256(input("Submit password: ").encode()).hexdigest()
        flag = input("log_in or sign_up")
        if input("Keep signed in") == "true":
            with open("settings.txt", 'r') as f:
                data = f.readlines()
            with open("settings.txt", 'w') as f:
                data[0] = "true"
                data[1] = name_hash
                data[2] = password_hash
                f.write("\n".join(data))
    client_x_everything.sendto(f"{name_hash}${password_hash}${flag}".encode(), login_server_ip)


def main():
    client_x_everything, login_server_ip = conn()


if __name__ == '__main__':
    main()
