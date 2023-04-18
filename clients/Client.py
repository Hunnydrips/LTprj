from threading import Thread
from Client_classes.graphic_functions import *
from Client_classes.client_objects import *
from pygame.locals import *
import socket
import logging
import json
import sys
import login_gui

central_addr: tuple = ("127.0.0.1", 8100)
event_to_packet: dict = {pygame.K_d: ["right", 1], pygame.K_a: ["left", -1], pygame.K_w: ["up", -1],
                         pygame.K_s: ["down", 1]}
screen: pygame.Surface = pygame.display.set_mode((600, 600), RESIZABLE)


def init_settings():
    with open("settings.txt", 'a'):
        pass  # ensuring the file's existence
    with open("settings.txt", 'r') as f:
        if len(f.readlines()) < 3:
            with open("settings.txt", 'w') as file:
                file.write("auto_sign_up\nname\npassword\n")


def log_in() -> tuple[socket.socket, tuple[str, int]]:  # connection to central so to have the ip of login server
    client_x_everything = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_x_everything.sendto(b"log_requested", central_addr)
    data = client_x_everything.recvfrom(1024)[0].decode()[1:-1].split(", ")
    login_server_ip = (data[0][1:-1], int(data[1]))
    while not log_in_or_sign_up(client_x_everything, login_server_ip):
        logging.debug("Waiting for somebody to connect")
    logging.debug("Logged in successfully")
    data = client_x_everything.recvfrom(1024)[0].decode()[1:-1].split(", ")
    game_server_ip = (data[0][1:-1], int(data[1]))
    client_x_everything.sendto(json.dumps({"cmd": "begin"}).encode(), game_server_ip)
    logging.debug("Connection to game server has been established :D")
    return client_x_everything, game_server_ip


def log_in_or_sign_up(client_x_everything: socket.socket(), login_server_ip: tuple) -> bool:
    name_hash, password_hash, flag = "", "", ""
    with open("settings.txt", 'r') as f:
        data = f.read().split("\n")
    if data[0] == "true":
        name_hash, password_hash, flag = data[1], data[2], "log_in"
        client_x_everything.sendto(f"{name_hash}${password_hash}${flag}".encode(), login_server_ip)
        resp = client_x_everything.recvfrom(1024)[0].decode()
        positive_answer = ["log_in successful", "Created username successfully"]
        if resp not in positive_answer:
            data[0] = "false"
            with open("settings.txt", 'w') as f:
                f.write("\n".join(data))
        return resp in positive_answer
    else:
        login_gui.login_screen(client_x_everything, login_server_ip)
        return True


def receive_request_from_game_server(client_x_everything: socket.socket, P: ClientPlayer):
    while True:
        data, ip = client_x_everything.recvfrom(1024)
        msg = json.loads(data.decode())
        print(msg)
        if msg["cmd"] == 'move':
            x, y = msg["pos"][0], msg["pos"][1]
            P.collision_center = Point(x, y)
            print(P.collision_center)
        print("server data:", *data)
        print("client data:", P.collision_center.to_tuple())


def move_all_lasers(P: ClientPlayer):
    c_x, c_y = get_camera_coordinates()
    for P_laser in P.lasers:
        if P_laser.move():
            P.lasers.remove(P_laser)
        else:
            tmp_rect = P_laser.rect.copy()
            tmp_rect.center = tmp_rect.center[0] - c_x, tmp_rect.center[1] - c_y
            screen.blit(P_laser.to_blit, tmp_rect)
            distance = -52
            if P_laser.state == 0:
                distance = 0
            x, y = pos_by_distance_and_angle(P_laser.angle, 0, distance, Point(*tmp_rect.center))
            laser_collide_rect = pygame.Rect((x, y), (30, 30))
            laser_collide_rect.center = x, y
            pygame.draw.rect(screen, BLUE, laser_collide_rect, 4)


def main():
    init_settings()
    client_x_everything, game_server_ip = log_in()
    pygame.init()
    clock = pygame.time.Clock()
    P = ClientPlayer()
    Thread(target=receive_request_from_game_server, args=(client_x_everything, P)).start()
    running = True
    while running:
        update_camera_cords(screen, P.collision_center)
        player_attr: dict = {
            "pos": P.collision_center.to_tuple(),
            "angle": P.angle,
            "status": P.status,
            "name": "my_nickname",
            "current_sprite": P.animations[P.status].current_sprite
        }
        packet_data = json.dumps(player_attr)
        msg: dict = {
            "cmd": "add",
            "player_to_add": packet_data
        }
        client_x_everything.sendto(json.dumps(msg).encode(), game_server_ip)
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_r:
                            P.reload()
                    msg: dict = {
                        "cmd": ...,
                        "key_stroke": event_to_packet[event.key][0]
                    }
                    if event.key in event_to_packet:
                        msg["cmd"] = "press"
                        client_x_everything.sendto(json.dumps(msg).encode(), game_server_ip)
                        if event.key in list(event_to_packet.keys())[:2]:
                            P.x_dir = event_to_packet[event.key][1]
                        else:
                            P.y_dir = event_to_packet[event.key][1]
                        logging.debug("A key has been pressed and sent to the server")
                case pygame.KEYUP:
                    if event.key in event_to_packet:
                        msg["cmd"] = "release"
                        client_x_everything.sendto(json.dumps(msg).encode(), game_server_ip)
                        if event.key in list(event_to_packet.keys())[:2]:
                            P.x_dir = 0
                        else:
                            P.y_dir = 0
                        logging.debug("A key has been released and sent to the server")
                case pygame.MOUSEBUTTONDOWN:
                    # client-sided for now
                    if event.button == pygame.BUTTON_LEFT:
                        c_x, c_y = get_camera_coordinates()
                        P.shoot(pygame.mouse.get_pos()[0] + c_x, pygame.mouse.get_pos()[1] + c_y)
                        # print(P.collision_center.to_tuple(), pygame.mouse.get_pos()[0] + c_x, pygame.mouse.get_pos()[1] + c_y)
                # if P.x_dir or P.y_dir:
                #     if P.status == "idle":
                #         P.status = "move"
                #         P.animations[P.status].reset()
                #     else:
                #         P.next_status = "move"
        paint_map(screen)
        # for P in player_list:
        animate_player(P)
        blit_player(screen, P, *pygame.mouse.get_pos())
        move_all_lasers(P)
        clock.tick(60)
        pygame.display.update()


if __name__ == '__main__':
    main()
