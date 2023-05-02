from tkinter import *
import logging
import hashlib
import socket

client_x_everything: socket.socket = socket.socket()
login_server_ip: tuple = ('', 0)
logging.basicConfig(level=logging.DEBUG)


class InvalidPasswordException(Exception):
    """
    Class is for raising this type of exception, easier to detect bugs
    """
    pass


def send_credentials(root, username, password, var_flag, str_flag):
    """
    sends credentials to login server so to keep in DB
    :param root: primal object of the tkinter module
    :param username: player's username
    :param password: player's password
    :param var_flag: integer flag
    :param str_flag: string flag
    :return: Nothing
    """
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    if var_flag.get():
        with open("settings.txt", 'r') as f:
            data = f.readlines()
        with open("settings.txt", 'w') as f:
            data[0] = "true"
            data[1] = username
            data[2] = password_hash
            f.write("\n".join(data))
    client_x_everything.sendto(f"{username}${password_hash}${str_flag}".encode(), login_server_ip)
    response = client_x_everything.recvfrom(1024)[0].decode()
    positive_answer = ["log_in successful", "Created username successfully"]
    if response in positive_answer:
        root.destroy()


def login_screen(Client_x_everything: socket.socket = socket.socket(), Login_server_ip: tuple = ("", 0)):
    """
    Big function that consists of smaller, indicates the login screen
    :param Client_x_everything: client and everything socket
    :param Login_server_ip: login server ip
    :return: Nothing
    """
    global client_x_everything
    global login_server_ip
    client_x_everything = Client_x_everything
    login_server_ip = Login_server_ip
    root: Tk = Tk()
    root.title("")
    root.geometry("925x500+200+300")
    root.configure(bg='#FFF')
    root.resizable(False, False)
    image: PhotoImage = PhotoImage(file="Laser_tag_initial_screen.png")
    Label(root, image=image, background="white").place(x=0, y=0)
    frm: Frame = Frame(root, width=350, height=400, bg="white")
    frm.place(x=480, y=70)
    heading: Label = Label(frm, text="Sign-in", fg="#57a1f8", bg="white", font=("Microsoft YaHei UI Light", 23, "bold"))
    heading.place(x=100, y=5)

    label2: Label = Label(frm, text="Remember me?", fg="black", bg="white", font=("Microsoft YaHei UI Light", 9))
    label2.place(x=25, y=200)

    var_flag: IntVar = IntVar()
    stay_in: Checkbutton = Checkbutton(frm, width=1, height=1, cursor="hand2", bg="white", fg="#57a1f8", variable=var_flag, activebackground="white", activeforeground="white")
    stay_in.place(x=120, y=200)

    def sign_in():
        """
        Mini sign-in function
        :return: Nothing
        """
        username = user.get()
        password = passcode.get()
        try:
            if username != "username" and password != "password" and username and password:
                send_credentials(root, username, password, var_flag, "log_in")
            else:
                raise InvalidPasswordException
        except InvalidPasswordException:
            logging.debug("Exception has occurred, Invalid password")

    def sign_up():
        """
        Go to sign-up screen
        :return: Nothing
        """
        root.destroy()
        sign_up_screen()

    def on_enter(e):
        """
        For text box
        :param e: required variable
        :return: Nothing
        """
        if user.get() == "username":
            user.delete(0, "end")

    def on_leave(e):
        """
        For text box
        :param e: required variable
        :return: Nothing
        """
        name = user.get()
        if not name:
            user.insert(0, "username")

    def on_enter2(e):
        """
        For text box
        :param e: required variable
        :return: Nothing
        """
        if passcode.get() == "password":
            passcode.delete(0, "end")

    def on_leave2(e):
        """
        For text box
        :param e: required variable
        :return: Nothing
        """
        name = passcode.get()
        if not name:
            passcode.insert(0, "password")

    user: Entry = Entry(frm, width=25, fg="black", border=0, font=("Microsoft YaHei UI Light", 11))
    user.place(x=30, y=80)
    user.insert(0, "username")
    user.bind("<FocusIn>", on_enter)
    user.bind("<FocusOut>", on_leave)
    Frame(frm, width=295, height=2, bg="black").place(x=25, y=107)

    passcode = Entry(frm, width=25, fg="black", border=0, font=("Microsoft YaHei UI Light", 11), show="*")
    passcode.place(x=30, y=150)
    passcode.bind("<FocusIn>", on_enter2)
    passcode.bind("<FocusOut>", on_leave2)
    passcode.insert(0, "password")
    Frame(frm, width=295, height=2, bg="black").place(x=25, y=177)

    Button(frm, width=39, pady=7, text="Sign-in", fg="white", bg="#57a1f8", border=0, command=sign_in).place(x=35,
                                                                                                             y=264)
    label = Label(frm, text="Don't have an account?", fg="black", bg="white", font=("Microsoft YaHei UI Light", 9))
    label.place(x=75, y=300)

    Sign_up = Button(frm, width=6, text="Sign-up", border=0, bg="white", cursor="hand2", fg="#57a1f8", command=sign_up)
    Sign_up.place(x=215, y=300)

    root.mainloop()


def sign_up_screen():
    """
    Fresh root, no need for parameters again, func for sign-up this time
    :return: Nothing
    """
    root = Tk()
    root.title("")
    root.geometry("925x500+200+300")
    root.configure(bg='#FFF')
    root.resizable(False, False)
    image = PhotoImage(file="Laser_tag_initial_screen.png")
    Label(root, image=image, background="white").place(x=0, y=0)
    frm = Frame(root, width=350, height=400, bg="white")
    frm.place(x=480, y=70)
    heading = Label(frm, text="Sign-up", fg="#57a1f8", bg="white", font=("Microsoft YaHei UI Light", 23, "bold"))
    heading.place(x=100, y=5)

    def validate_password(username: str, password: str, confirm_password: str):
        """
        Password validation function, easier to read
        :param username: player's username
        :param password: player's password
        :param confirm_password: the same password so to confirm
        :return: if the user has correctly inserted a username and password
        """
        return username != "username" and password != "password" and confirm_password == password and username and password

    def sign_up():
        """
        Basic operational sign-up screen
        :return: Nothing
        """
        username = user.get()
        password = passcode.get()
        confirm_password = confirm_passcode.get()
        try:
            if validate_password(username, password, confirm_password):
                send_credentials(root, username, password, var_flag, "sign_up")
            else:
                raise InvalidPasswordException
        except InvalidPasswordException:
            logging.debug("Exception has occurred, Invalid password")

    def sign_in():
        """
        Return to sign-in screen
        :return: Nothing
        """
        root.destroy()
        login_screen()

    def on_enter(e):
        """
        For text box
        :param e: required variable
        :return: Nothing
        """
        x = user.get()
        if x == "username":
            user.delete(0, "end")
        if len(x) > 10:
            user.insert(0, x[:-1])

    def on_leave(e):
        """
        For text box
        :param e: required variable
        :return: Nothing
        """
        name = user.get()
        if not name:
            user.insert(0, "username")

    def on_enter2(e):
        """
        For text box
        :param e: required variable
        :return: Nothing
        """
        if passcode.get() == "password":
            passcode.delete(0, "end")

    def on_leave2(e):
        """
        For text box
        :param e: required variable
        :return: Nothing
        """
        password = passcode.get()
        if not password:
            passcode.insert(0, "password")

    def on_enter3(e):
        """
        For text box
        :param e: required variable
        :return: Nothing
        """
        if confirm_passcode.get() == "confirm-password":
            confirm_passcode.delete(0, "end")

    def on_leave3(e):
        """
        For text box
        :param e: required variable
        :return: Nothing
        """
        confirm_password = confirm_passcode.get()
        if not confirm_password:
            confirm_passcode.insert(0, "confirm-password")

    user = Entry(frm, width=25, fg="black", border=0, font=("Microsoft YaHei UI Light", 11))
    user.place(x=30, y=80)
    user.insert(0, "username")
    user.bind("<FocusIn>", on_enter)
    user.bind("<FocusOut>", on_leave)
    Frame(frm, width=295, height=2, bg="black").place(x=25, y=107)

    passcode = Entry(frm, width=25, fg="black", border=0, font=("Microsoft YaHei UI Light", 11), show="*")
    passcode.place(x=30, y=150)
    passcode.bind("<FocusIn>", on_enter2)
    passcode.bind("<FocusOut>", on_leave2)
    passcode.insert(0, "password")
    Frame(frm, width=295, height=2, bg="black").place(x=25, y=177)

    confirm_passcode = Entry(frm, width=25, fg="black", border=0, font=("Microsoft YaHei UI Light", 11))
    confirm_passcode.place(x=30, y=220)
    confirm_passcode.bind("<FocusIn>", on_enter3)
    confirm_passcode.bind("<FocusOut>", on_leave3)
    confirm_passcode.insert(0, "confirm-password")
    Frame(frm, width=295, height=2, bg="black").place(x=25, y=247)

    Button(frm, width=39, pady=7, text="Sign-up", fg="white", bg="#57a1f8", border=0, command=sign_up).place(x=35,
                                                                                                             y=290)
    label = Label(frm, text="Already have an account?", fg="black", bg="white", font=("Microsoft YaHei UI Light", 9))
    label.place(x=70, y=330)

    Sign_in = Button(frm, width=6, text="Sign-in", border=0, bg="white", cursor="hand2", fg="#57a1f8", command=sign_in)
    Sign_in.place(x=215, y=330)

    label2 = Label(frm, text="Remember me?", fg="black", bg="white", font=("Microsoft YaHei UI Light", 9))
    label2.place(x=25, y=264)

    var_flag = IntVar()
    stay_in = Checkbutton(frm, width=1, height=1, cursor="hand2", bg="white", fg="#57a1f8", variable=var_flag,
                          activebackground="white", activeforeground="white")
    stay_in.place(x=120, y=264)

    root.mainloop()
