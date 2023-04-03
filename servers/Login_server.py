import socket
import hashlib
import sqlite3
from threading import Thread

USER_IPS = []


def is_list_in_other_list(l1: list, l2: list) -> bool:
    return str(l1)[1:-1].__contains__(str(l2)[1:-1])


def in_table(items: list, cur) -> bool:
    x = '*'
    if len(items) == 1:
        x = 'name_hash_hash'
    cur.execute(f'SELECT {x} FROM users')
    rows = cur.fetchall()
    if len(items) == 1:
        rows = [rows]
    for row in rows:
        if is_list_in_other_list(row, items):
            return True
    return False


def init_login_server() -> tuple:
    login_server_x_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    login_server_x_client.bind(("0.0.0.0", 8201))
    login_server_x_central_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    login_server_x_central_server.bind(("0.0.0.0", 8202))
    login_server_x_central_server.sendto("3!a".encode(), ("127.0.0.1", 8101))
    login_server_x_client.sendto("3!b".encode(), ("127.0.0.1", 8101))           # only time it has to access central_server
    return login_server_x_client, login_server_x_central_server


def handle_input_from_central(login_server_x_central_server: socket.socket()) -> None:
    data, ip = login_server_x_central_server.recvfrom(1024)
    data = data.decode()[1:-1].split(", ")
    USER_IPS.append((data[0][1:-1], int(data[1])))
    Thread(target=handle_input_from_central, args=(login_server_x_central_server, )).start()


def handle_input_from_client(login_server_x_client: socket.socket(), login_server_x_central_server: socket.socket()) -> None:
    conn = sqlite3.connect("I_hate_sql.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (name_hash_hash TEXT, password_hash_hash TEXT)")
    data, ip = login_server_x_client.recvfrom(1024)
    if ip in USER_IPS:
        name, password_hash, flag = data.decode().split("$")
        name_hash, password_hash_hash = hashlib.sha256(name.encode()).hexdigest(), hashlib.sha256(password_hash.encode()).hexdigest()
        to_send = 'Incorrect data'
        match flag:
            case "log_in":
                if in_table([name_hash, password_hash_hash], cursor):
                    to_send = "log_in successful"
                    USER_IPS.remove(ip)
                else:
                    to_send = "incorrect username/password"
            case "sign_up":
                if not in_table([name_hash], cursor):
                    cursor.execute("INSERT INTO users VALUES (?, ?)", [name_hash, password_hash_hash])
                    conn.commit()
                    to_send = "Created username successfully"
                    USER_IPS.remove(ip)
                else:
                    to_send = "This username has been already taken"
        login_server_x_client.sendto(to_send.encode(), ip)
        if to_send in ["log_in successful", "Created username successfully"]:
            login_server_x_central_server.sendto(f"This user has been verified, {ip}, {name}".encode(), ("127.0.0.1", 8101))
    Thread(target=handle_input_from_client, args=(login_server_x_client, login_server_x_central_server)).start()


def main():
    login_server_x_client, login_server_x_central_server = init_login_server()
    handle_input_from_central(login_server_x_central_server)
    handle_input_from_client(login_server_x_client, login_server_x_central_server)
    while True:
        pass
    login_server_x_central_server.close()
    login_server_x_client.close()
    cursor.execute('SELECT * FROM users')
    print(cursor.fetchall())
    conn.close()


if __name__ == '__main__':
    main()
