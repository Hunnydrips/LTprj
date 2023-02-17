import socket
import login_gui


def init_settings() -> None:
    with open("settings.txt", 'a'):
        pass  # ensuring the file's existence
    with open("settings.txt", 'r') as f:
        if len(f.readlines()) < 3:
            with open("settings.txt", 'w') as file:
                file.write("auto_sign_up\nname\npassword\n")


def connect_to_login_server() -> tuple:                                               # connection to central so to have the ip of login server
    client_x_everything = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_x_everything.sendto("log_requested".encode(), ("127.0.0.1", 8100))
    data = client_x_everything.recvfrom(1024)[0].decode()[1:-1].split(", ")
    login_server_ip = (data[0][1:-1], int(data[1]))
    while not log_in_or_sign_up(client_x_everything, login_server_ip):
        pass
    print("Logged in successfully")
    data = client_x_everything.recvfrom(1024)[0].decode()[1:-1].split(", ")
    game_server_ip = (data[0][1:-1], int(data[1]))
    client_x_everything.sendto("Begin".encode(), game_server_ip)
    return client_x_everything, game_server_ip


def log_in_or_sign_up(client_x_everything: socket.socket(), login_server_ip) -> bool:
    name_hash, password_hash, flag = "", "", ""
    with open("settings.txt", 'r') as f:
        data = f.read().split("\n")
    if data[0] == "true":
        name_hash, password_hash, flag = data[1], data[2], "log_in"
        client_x_everything.sendto(f"{name_hash}${password_hash}${flag}".encode(), login_server_ip)
        response = client_x_everything.recvfrom(1024)[0].decode()
        positive_answer = ["log_in successful", "Created username successfully"]
        if response not in positive_answer:
            data[0] = "false"
            with open("settings.txt", 'w') as f:
                f.write("\n".join(data))
        return response in positive_answer
    else:
        login_gui.login_screen(client_x_everything, login_server_ip)
        return True


def main():
    init_settings()
    client_x_everything, game_server_ip = connect_to_login_server()


if __name__ == '__main__':
    main()
