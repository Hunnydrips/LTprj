from tkinter import *
import hashlib
import socket

client_x_everything = socket.socket()
login_server_ip = ('', 0)


def send_credentials(root, username, password, var_flag, str_flag):
    name_hash = hashlib.sha256(username.encode()).hexdigest()
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    if var_flag.get():
        with open("settings.txt", 'r') as f:
            data = f.readlines()
        with open("settings.txt", 'w') as f:
            data[0] = "true"
            data[1] = name_hash
            data[2] = password_hash
            f.write("\n".join(data))
    client_x_everything.sendto(f"{name_hash}${password_hash}${str_flag}".encode(), login_server_ip)
    response = client_x_everything.recvfrom(1024)[0].decode()
    positive_answer = ["log_in successful", "Created username successfully"]
    if response in positive_answer:
        root.destroy()


def login_screen(Client_x_everything=socket.socket(), Login_server_ip=("", 0)):
    global client_x_everything
    global login_server_ip
    client_x_everything = Client_x_everything
    login_server_ip = Login_server_ip
    root = Tk()
    root.title("")
    root.geometry("925x500+200+300")
    root.configure(bg='#FFF')
    root.resizable(False, False)
    image = PhotoImage(file="Laser_tag_initial_screen.png")
    Label(root, image=image, background="white").place(x=0, y=0)
    frm = Frame(root, width=350, height=400, bg="white")
    frm.place(x=480, y=70)
    heading = Label(frm, text="Sign-in", fg="#57a1f8", bg="white", font=("Microsoft YaHei UI Light", 23, "bold"))
    heading.place(x=100, y=5)

    label2 = Label(frm, text="Remember me?", fg="black", bg="white", font=("Microsoft YaHei UI Light", 9))
    label2.place(x=25, y=200)

    var_flag = IntVar()
    stay_in = Checkbutton(frm, width=1, height=1, cursor="hand2", bg="white", fg="#57a1f8", variable=var_flag,
                          activebackground="white", activeforeground="white")
    stay_in.place(x=120, y=200)

    def sign_in():
        username = user.get()
        password = passcode.get()
        if username != "username" and password != "password" and username and password:
            send_credentials(root, username, password, var_flag, "log_in")
        else:
            pass

    def sign_up():
        root.destroy()
        sign_up_screen()

    def on_enter(e):
        if user.get() == "username":
            user.delete(0, "end")

    def on_leave(e):
        name = user.get()
        if not name:
            user.insert(0, "username")

    def on_enter2(e):
        if passcode.get() == "password":
            passcode.delete(0, "end")

    def on_leave2(e):
        name = passcode.get()
        if not name:
            passcode.insert(0, "password")

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

    Button(frm, width=39, pady=7, text="Sign-in", fg="white", bg="#57a1f8", border=0, command=sign_in).place(x=35,
                                                                                                             y=264)
    label = Label(frm, text="Don't have an account?", fg="black", bg="white", font=("Microsoft YaHei UI Light", 9))
    label.place(x=75, y=300)

    Sign_up = Button(frm, width=6, text="Sign-up", border=0, bg="white", cursor="hand2", fg="#57a1f8", command=sign_up)
    Sign_up.place(x=215, y=300)

    root.mainloop()


def sign_up_screen():
    root = Tk()
    root.title("")
    root.geometry("925x500+200+300")
    root.configure(bg='#FFF')
    root.resizable(False, False)
    image = PhotoImage(file="Laser_tag_initial_screen.png")
    Label(root, image=image, background="white").place(x=0, y=0)
    frm = Frame(root, width=350, height=400, bg="white")
    frm.place(x=480, y=70)
    heading = Label(frm, text="Sign-in", fg="#57a1f8", bg="white", font=("Microsoft YaHei UI Light", 23, "bold"))
    heading.place(x=100, y=5)

    def sign_up():
        username = user.get()
        password = passcode.get()
        confirm_password = confirm_passcode.get()
        if username != "username" and password != "password" and confirm_password == password and username and password:
            send_credentials(root, username, password, var_flag, "sign_up")
        else:
            pass

    def sign_in():
        root.destroy()
        login_screen()

    def on_enter(e):
        x = user.get()
        if x == "username":
            user.delete(0, "end")
        if len(x) > 10:
            user.insert(0, x[:-1])

    def on_leave(e):
        name = user.get()
        if not name:
            user.insert(0, "username")

    def on_enter2(e):
        if passcode.get() == "password":
            passcode.delete(0, "end")

    def on_leave2(e):
        password = passcode.get()
        if not password:
            passcode.insert(0, "password")

    def on_enter3(e):
        if confirm_passcode.get() == "confirm-password":
            confirm_passcode.delete(0, "end")

    def on_leave3(e):
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
    stay_in = Checkbutton(frm, width=1, height=1, cursor="hand2", bg="white", fg="#57a1f8", variable=var_flag, activebackground="white", activeforeground="white")
    stay_in.place(x=120, y=264)

    root.mainloop()

