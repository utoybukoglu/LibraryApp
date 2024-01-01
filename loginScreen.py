from tkinter import *

def loginScreen():
    def getUserInfo():
        username = username_var.get()
        password = password_var.get()
        user_info_str = "login;" + username + ";" + password
        user_info_var.set(user_info_str)

    master = Tk()
    master.geometry("300x150")
    master.title("Login")

    userinfo_frame = Frame(master)
    userinfo_frame.grid(row=0, column=0, padx=5, pady=5, sticky=W)

    username_label = Label(userinfo_frame, text="User name:")
    password_label = Label(userinfo_frame, text="Password:")

    username_label.grid(row=0, column=0, sticky=W, pady=2)
    password_label.grid(row=1, column=0, sticky=W, pady=2)

    username_var = StringVar()
    password_var = StringVar()

    username_entry = Entry(userinfo_frame, textvariable=username_var)
    password_entry = Entry(userinfo_frame, show="*", textvariable=password_var)

    username_entry.grid(row=0, column=1, pady=10)
    password_entry.grid(row=1, column=1, pady=10)

    user_info_var = StringVar()

    def user_login():
        getUserInfo()
        master.destroy()

    login = Button(master, text="Login", command=user_login)
    login.grid(row=2, column=0, pady=5)

    mainloop()

    return user_info_var.get()
