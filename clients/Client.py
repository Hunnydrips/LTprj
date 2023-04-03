import socket
import struct
import sys
import login_gui
from threading import Thread
from Client_classes.graphic_functions import *
from Client_classes.client_objects import *
from pygame.locals import *

event_to_packet: dict = {pygame.K_d: ["right", 1], pygame.K_a: ["left", -1], pygame.K_w: ["up", -1], pygame.K_s: ["down", 1]}
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
    client_x_everything.sendto("log_requested".encode(), ("127.0.0.1", 8100))
    data = client_x_everything.recvfrom(1024)[0].decode()[1:-1].split(", ")
    login_server_ip = (data[0][1:-1], int(data[1]))
    while not log_in_or_sign_up(client_x_everything, login_server_ip):
        pass
    print("Logged in successfully")
    data = client_x_everything.recvfrom(1024)[0].decode()[1:-1].split(", ")
    game_server_ip = (data[0][1:-1], int(data[1]))
    client_x_everything.sendto("Begin".encode(), game_server_ip)
    print("Connection to game server has been established")
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


def handle_request_from_game_server(client_x_everything: socket.socket, P):
    data, ip = client_x_everything.recvfrom(1024)
    Thread(target=handle_request_from_game_server, args=(client_x_everything, P)).start()
    format_, to_unpack = data.split(b"$$")
    data = struct.unpack(format_.decode(), to_unpack)
    flag = data[0]
    if flag == b'M':
        x, y = int(data[1]), int(data[2])
        P.collision_center = point(x, y)
    # print("server data:", *data)
    # print("client data:", P.collision_center.to_tuple())


def move_all_lasers(P: player):
    c_x, c_y = get_camera_coordinates()
    for Laser in P.lasers:
        if Laser.move():
            P.lasers.remove(Laser)
        else:
            tmp_rect = Laser.rect.copy()
            tmp_rect.center = tmp_rect.center[0] - c_x, tmp_rect.center[1] - c_y
            screen.blit(Laser.to_blit, tmp_rect)
            distance = -52
            if Laser.state == 0:
                distance = 0
            x, y = pos_by_distance_and_angle(Laser.angle, 0, distance, point(*tmp_rect.center))
            laser_collide_rect = pygame.Rect((x, y), (30, 30))
            laser_collide_rect.center = x, y
            pygame.draw.rect(screen, BLUE, laser_collide_rect, 4)


def main():
    init_settings()
    client_x_everything, game_server_ip = log_in()
    pygame.init()
    clock = pygame.time.Clock()
    P = player()
    running = True
    Thread(target=handle_request_from_game_server, args=(client_x_everything, P)).start()
    while running:
        update_camera_cords(screen, P.collision_center)
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_r:
                            P.reload()
                    if event.key in event_to_packet:
                        client_x_everything.sendto(f"press {event_to_packet[event.key][0]}".encode(), game_server_ip)
                        if event.key in list(event_to_packet.keys())[:2]:
                            P.x_dir = event_to_packet[event.key][1]
                        else:
                            P.y_dir = event_to_packet[event.key][1]
                case pygame.KEYUP:
                    if event.key in event_to_packet:
                        client_x_everything.sendto(f"release {event_to_packet[event.key][0]}".encode(), game_server_ip)
                        if event.key in list(event_to_packet.keys())[:2]:
                            P.x_dir = 0
                        else:
                            P.y_dir = 0
                case pygame.MOUSEBUTTONDOWN:
                    if event.button == pygame.BUTTON_LEFT:
                        c_x, c_y = get_camera_coordinates()
                        P.shoot(pygame.mouse.get_pos()[0] + c_x, pygame.mouse.get_pos()[1] + c_y)
                        print(P.collision_center.to_tuple(), pygame.mouse.get_pos()[0] + c_x, pygame.mouse.get_pos()[1] + c_y)
                # if P.x_dir or P.y_dir:
                #     if P.status == "idle":
                #         P.status = "move"
                #         P.animations[P.status].reset()
                #     else:
                #         P.next_status = "move"
        paint_map(screen)
        animate_player(P)
        blit_player(screen, P, *pygame.mouse.get_pos())
        move_all_lasers(P)
        clock.tick(60)
        pygame.display.update()


if __name__ == '__main__':
    main()
