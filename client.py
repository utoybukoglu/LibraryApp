import socket
from loginScreen import loginScreen
from librarianPanel import librarianPanel
from managerPanel import managerPanel

def connect_to_server():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 6000))
    while True:
        user_info = loginScreen()
        client_socket.send(user_info.encode())
        response = client_socket.recv(1024).decode()
        if response != "loginfailure":
            print(response)
            role = response.split(";")[2]
            if role == "librarian":
                panel_output = librarianPanel(librarianName=response.split(";")[1])
                client_socket.send(panel_output.encode())
                librarian_operation_message = client_socket.recv(1024).decode()
                print(librarian_operation_message)
                break
            elif role == "manager":
                report_str = managerPanel(managerName=user_info.split(";")[1])
                client_socket.send(report_str.encode())
                manager_operation_message = client_socket.recv(1024).decode()
                print(manager_operation_message)
                break
        else:
            print(response)
    client_socket.close()
connect_to_server()