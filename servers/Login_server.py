from sqlite3 import Cursor, Connection
from threading import Thread
from hashlib import sha256
from typing import Any
import socket
import sqlite3

USER_IPS: list = []
LOCAL_HOST: str = "127.0.0.1"
PORT: int = 8101
CENTRAL_ADDR: tuple[str, int] = (LOCAL_HOST, PORT)


def is_list_in_other_list(l1: list, l2: list) -> bool:
    """
    :param l1: List 1
    :param l2: List 2
    :return: if one list contains the other
    """
    return str(l1)[1:-1].__contains__(str(l2)[1:-1])


def in_table(items: list, cur: Cursor) -> bool:
    """
    :param items: objects inside table
    :param cur: cursor object (SQL)
    :return: if a row exists in items
    """
    x: str = '*'
    if len(items) == 1:
        x = 'name_hash_hash'
    cur.execute(f'SELECT {x} FROM users')
    rows: Any = cur.fetchall()
    if len(items) == 1:
        rows: list = [rows]
    for row in rows:
        if is_list_in_other_list(row, items):
            return True
    return False


def init_login_server() -> tuple:
    """
    Initialise :D
    :return: login server and client socket, and login server and central server socket
    """
    login_server_x_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    login_server_x_client.bind(("0.0.0.0", 8201))
    login_server_x_central_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    login_server_x_central_server.bind(("0.0.0.0", 8202))
    login_server_x_central_server.sendto(b"3!a", CENTRAL_ADDR)
    login_server_x_client.sendto(b"3!b", CENTRAL_ADDR)  # only time it has to access central_server
    return login_server_x_client, login_server_x_central_server


def handle_input_from_central(login_server_x_central_server: socket.socket):
    """
    Handling central packet for getting client
    :param login_server_x_central_server: login server and central server socket
    :return: Nothing, eternal loop using a thread
    """
    data, ip = login_server_x_central_server.recvfrom(1024)
    data = data.decode()[1:-1].split(", ")
    USER_IPS.append((data[0][1:-1], int(data[1])))
    Thread(target=handle_input_from_central, args=(login_server_x_central_server, )).start()


def handle_input_from_client(login_server_x_client: socket.socket, login_server_x_central_server: socket.socket):
    """
    Handling client packet for login process
    :param login_server_x_client: login server and client socket
    :param login_server_x_central_server: login server and central server socket
    :return: Nothing
    """
    conn: Connection = sqlite3.connect("I_hate_sql.db")
    cursor: Cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (name_hash TEXT, password_hash_hash TEXT)")
    data, client_ip = login_server_x_client.recvfrom(1024)
    if client_ip in USER_IPS:
        client_name, password_hash, flag = data.decode().split("$")
        name_hash, password_hash_hash = sha256(client_name.encode()).hexdigest(), sha256(password_hash.encode()).hexdigest()           # hash technique
        to_send: str = 'Incorrect data'
        match flag:
            case "log_in":
                if in_table([name_hash, password_hash_hash], cursor):
                    to_send = "log_in successful"
                    USER_IPS.remove(client_ip)
                else:
                    to_send = "incorrect username/password"
            case "sign_up":
                if not in_table([name_hash], cursor):
                    cursor.execute("INSERT INTO users VALUES (?, ?)", [name_hash, password_hash_hash])
                    conn.commit()
                    to_send = "Created username successfully"
                    USER_IPS.remove(client_ip)
                else:
                    to_send = "This username has been already taken"
        login_server_x_client.sendto(to_send.encode(), client_ip)                          # May or may not be successful
        if to_send in ["log_in successful", "Created username successfully"]:
            login_server_x_central_server.sendto(f"This user has been verified, {client_ip}, {client_name}".encode(), CENTRAL_ADDR)           # 100% successful
    Thread(target=handle_input_from_client, args=(login_server_x_client, login_server_x_central_server)).start()


def main():
    login_server_x_client, login_server_x_central_server = init_login_server()
    handle_input_from_central(login_server_x_central_server)
    handle_input_from_client(login_server_x_client, login_server_x_central_server)
    while True:
        pass
    login_server_x_central_server.close()
    login_server_x_client.close()
    conn.close()


if __name__ == '__main__':
    main()
