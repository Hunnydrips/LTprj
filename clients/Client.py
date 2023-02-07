import socket
import hashlib


def init_settings():
    with open("settings.txt", 'a'):
        pass  # ensuring the file's existence
    with open("settings.txt", 'r') as f:
        if len(f.readlines()) < 3:
            with open("settings.txt", 'w') as file:
                file.write("auto_sign_up\nname\npassword\n")


def connect():                                               # connection to central so to have the ip of login server
    client_x_everything = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_x_everything.sendto("log_requested".encode(), ("127.0.0.1", 8100))
    data = client_x_everything.recvfrom(1024)[0].decode()[1:-1].split(", ")
    login_server_ip = (data[0][1:-1], int(data[1]))
    while not log_in_or_sign_up(client_x_everything, login_server_ip):
        # todo: graphic shit too
        pass
    return client_x_everything, login_server_ip


def log_in_or_sign_up(client_x_everything: socket.socket(), login_server_ip):
    name_hash, password_hash, flag = "", "", ""
    with open("settings.txt", 'r') as f:
        data = f.read().split("\n")
    if data[0] == "true":
        name_hash, password_hash, flag = data[1], data[2], "log_in"
    else:
        name_hash = hashlib.sha256(input("Enter username: ").encode()).hexdigest()
        password_hash = hashlib.sha256(input("Submit password: ").encode()).hexdigest()
        flag = input("log_in or sign_up: ")
        if input("Keep signed in: ") == "true":
            with open("settings.txt", 'r') as f:
                data = f.readlines()
            with open("settings.txt", 'w') as f:
                data[0] = "true"
                data[1] = name_hash
                data[2] = password_hash
                f.write("\n".join(data))
    client_x_everything.sendto(f"{name_hash}${password_hash}${flag}".encode(), login_server_ip)
    response = client_x_everything.recvfrom(1024)[0].decode()
    positive_answer = ["log_in successful", "Created username successfully"]
    # todo: graphic func that takes the response and presents it on the screen
    return response in positive_answer


def main():
    init_settings()
    client_x_everything, login_server_ip = connect()


if __name__ == '__main__':
    main()
