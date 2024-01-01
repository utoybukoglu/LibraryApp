import copy
import os
import socket
from datetime import datetime
from threading import *


class ClientThread(Thread):
    def __init__(self, clientsocket, clientaddress):
        Thread.__init__(self)
        self.clientsocket = clientsocket
        self.clientaddress = clientaddress
        print("Connection from ", clientaddress)

    def validate_user(self, username, password):
        with open("users.txt", "r") as file:
            for line in file:
                user, passw, role = line.strip().split(";")
                if username == user and password == passw:
                    return role
        file.close()
        return ""

    def run(self):
        while True:
            user_info = self.clientsocket.recv(1024).decode()
            login, username, password = user_info.split(";")
            role = self.validate_user(username, password)
            if role != "":
                self.clientsocket.send(f"loginsuccess;{username};{role}".encode())
                if role == "librarian":
                    operation_info = self.clientsocket.recv(1024).decode()
                    operation_detail_previous = operation_info.split(";")
                    items_id = operation_detail_previous[4:]
                    operation_detail = create_operations(operation_detail_previous, items_id)

                    if operation_detail[0] == "rent":
                        if check_book_availability(operation_detail[4:]):
                            if check_rent_situation(operation_detail[2]):
                                update_book_file_rent(operation_detail[4:])
                                update_operations_file(operation_detail)
                                self.clientsocket.send("rentsuccess".encode())
                            else:
                                self.clientsocket.send("renterror".encode())
                        else:
                            self.clientsocket.send("availabilityerror".encode())
                    else:
                        if check_return_situation(operation_detail[2], operation_detail[4:]):
                            update_book_file_return(operation_detail[4:])
                            update_operations_file(operation_detail)
                            cost = calculate_rent_fee(operation_detail)
                            self.clientsocket.send(("returnsuccess;" + str(cost)).encode())
                        else:
                            self.clientsocket.send("returnerror".encode())

                    break
                elif role == "manager":
                    report_info = self.clientsocket.recv(1024).decode()
                    report_detail = report_info.split(";")
                    if report_detail[1] == "1":
                        book = max_rented_book()
                        self.clientsocket.send(("report;1;"+book).encode())
                    elif report_detail[1] == "2":
                        librarian_name = max_librarian()
                        self.clientsocket.send(("report;2;"+librarian_name).encode())
                    elif report_detail[1] == "3":
                        revenue = total_revenue()
                        self.clientsocket.send(("report;3;"+str(revenue)).encode())
                    elif report_detail[1] == "4":
                        period = avg_rental_period()
                        self.clientsocket.send(("report;4;"+str(period)).encode())
                    else:
                        self.clientsocket.send("reporterror".encode())
            else:
                self.clientsocket.send("loginfailure".encode())
        self.clientsocket.close()

def takeBookData():
    bookDataList = []
    with open("books.txt", "r") as file:
        for line in file:
            bookDataList.append(line.strip())
    return bookDataList


def check_book_availability(book_id_list):
    book_list = takeBookData()
    availability_count = 0
    for book in book_list:
        if book.split(";")[0] in book_id_list:
            if int(book.split(";")[-1]) > 0:
                availability_count += 1

    if availability_count == len(book_id_list):
        return True
    else:
        return False


def takeOperationsData():
    operationDataList = []

    # Check if the file exists and is not empty
    if os.path.exists("operations.txt") and os.path.getsize("operations.txt") > 0:
        with open("operations.txt", "r") as file:
            for line in file:
                operationDataList.append(line.strip())
    return operationDataList


def check_rent_situation(clientsUsername):
    operation_list = takeOperationsData()
    client_operation_list = []
    for operation in operation_list:
        if clientsUsername == operation.split(";")[2]:
            client_operation_list.append(operation)

    rent_count = 0
    return_count = 0
    for operation in client_operation_list:
        if "rent" == operation.split(";")[0]:
            operation_items = operation.split(";")
            count = len(operation_items) - 4
            rent_count += count
        else:
            operation_items = operation.split(";")
            count = len(operation_items) - 4
            return_count += count

    if rent_count == return_count:
        return True
    else:
        return False


def check_return_situation(clientsUsername, items_id):
    operation_list = takeOperationsData()
    client_operation_list = []
    for operation in operation_list:
        if clientsUsername == operation.split(";")[2]:
            client_operation_list.append(operation)

    rent_books = {}
    return_book_list = []
    for operation in client_operation_list:
        if "rent" == operation.split(";")[0]:
            for i in range(4, len(operation.split(";"))):
                if operation.split(";")[i] not in rent_books.keys():
                    rent_books[operation.split(";")[i]] = 1
                else:
                    rent_books[operation.split(";")[i]] += 1
        else:
            return_book_list += operation.split(";")[4:]

    for item in return_book_list:
        rent_books[item] -= 1

    flag = 0
    for item in items_id:
        if rent_books[item] == 0:
            flag = 1

    if flag == 1:
        return False
    else:
        return True


def is_sublist(larger_list, sublist):
    if not sublist:  # An empty list is a sublist of any list
        return True
    if not larger_list:  # An empty list can't have sublists
        return False

    for i in range(len(larger_list) - len(sublist) + 1):
        if larger_list[i:i+len(sublist)] == sublist:
            return True
    return False


def update_book_file_rent(item_id_list):
    book_list = takeBookData()
    updated_books = []  # Create a new list to store updated book data

    for book in book_list:
        parts = book.split(";")
        book_id = parts[0]

        if book_id in item_id_list:
            # If the book_id is in the item_id_list, decrement the last field
            parts[-1] = str(int(parts[-1]) - 1)

        updated_books.append(";".join(parts))  # Join the parts back together

    # Write the updated book data to the file
    with open("books.txt", 'w') as file:
        for updated_book in updated_books:
            file.write(updated_book + "\n")


def update_operations_file(operation_detail):
    # Write the operation data to the file
    with open("operations.txt", 'a') as file:
        for i in range(len(operation_detail)):
            if i == (len(operation_detail) - 1):
                file.write(operation_detail[i] + "\n")
            else:
                file.write(operation_detail[i] + ";")


def calculate_rent_fee(operation_detail):
    operation_list = takeOperationsData()
    client_operation_list = []
    for operation in operation_list:
        if operation_detail[2] == operation.split(";")[2] and operation.split(";")[0] == "rent":
            if is_sublist(operation.split(";")[4:], operation_detail[4:]) or operation.split(";")[4:] == operation_detail[4:]:
                client_operation_list.append(operation)

    date_strings = []
    for operation in client_operation_list:
        date_strings.append(operation.split(";")[3])

    # Find the greatest (most recent) date using the max() function
    greatest_date_string = max(date_strings, key=parse_date)

    # Convert date strings to datetime objects
    date1 = datetime.strptime(greatest_date_string, "%d.%m.%Y")
    date2 = datetime.strptime(operation_detail[3], "%d.%m.%Y")

    # Calculate the number of days between the two dates
    delta = date2 - date1
    days_between = delta.days

    book_list = takeBookData()
    price_per_day = 0
    for book in book_list:
        if book.split(";")[0] in operation_detail[4:]:
            price_per_day += float(book.split(";")[-2])

    total_cost = days_between * price_per_day
    return total_cost


# Define a function to convert a date string to a datetime object
def parse_date(date_str):
    return datetime.strptime(date_str, "%d.%m.%Y")


def update_book_file_return(item_id_list):
    book_list = takeBookData()
    updated_books = []  # Create a new list to store updated book data

    for book in book_list:
        parts = book.split(";")
        book_id = parts[0]

        if book_id in item_id_list:
            # If the book_id is in the item_id_list, increment the last field
            parts[-1] = str(int(parts[-1]) + 1)

        updated_books.append(";".join(parts))  # Join the parts back together

    # Write the updated book data to the file
    with open("books.txt", 'w') as file:
        for updated_book in updated_books:
            file.write(updated_book + "\n")


def create_operations(operation_detail_previous, items_id):
    operation_detail = copy.deepcopy(operation_detail_previous)
    j = 0
    for i in range(4, len(operation_detail)):
        operation_detail[i] = items_id[j]
        j += 1

    return operation_detail


def max_rented_book():
    operation_list = takeOperationsData()
    book = {}
    for operation in operation_list:
        if operation.split(";")[0] == "rent":
            for item in range(4, len(operation.split(";"))):
                if operation.split(";")[item] not in book.keys():
                    book[operation.split(";")[item]] = 1
                else:
                    book[operation.split(";")[item]] += 1

    max_book_id = max(zip(book.values(), book.keys()))[1]
    book_list = takeBookData()
    for book in book_list:
        parts = book.split(";")
        if max_book_id == parts[0]:
            return parts[1]

def max_librarian():
    operation_list = takeOperationsData()
    librarians = {}
    for operation in operation_list:
        if operation.split(";")[1] not in librarians.keys():
            librarians[operation.split(";")[1]] = 1
        else:
            librarians[operation.split(";")[1]] += 1

    return max(zip(librarians.values(), librarians.keys()))[1]


def total_revenue():
    total_cost = 0
    operation_list = takeOperationsData()
    for operation in operation_list:
        if operation.split(";")[0] == "return":
            total_cost += calculate_rent_fee(operation.split(";"))

    return total_cost


def avg_rental_period():
    operation_list = takeOperationsData()
    harry_potter_rent_date = []
    for operation in operation_list:
        if operation.split(";")[0] == "rent":
            for item in operation.split(";")[4:]:
                if item == "3":
                    harry_potter_rent_date.append(operation.split(";")[3])

    if len(harry_potter_rent_date) == 0:
        return 0
    else:
        harry_potter_count = 0
        book_list = takeBookData()
        for book in book_list:
            if book.split(";")[0] == "3":
                harry_potter_count = int(book.split(";")[-1])

        if harry_potter_count != 5:
            harry_potter_rent_date_updated = harry_potter_rent_date[0: -(5 - harry_potter_count)]
        else:
            harry_potter_rent_date_updated = copy.deepcopy(harry_potter_rent_date)

        days_between_list = []
        for i in range(len(harry_potter_rent_date_updated)-1):
            # Convert date strings to datetime objects
            date1 = datetime.strptime(harry_potter_rent_date_updated[i], "%d.%m.%Y")
            date2 = datetime.strptime(harry_potter_rent_date_updated[i+1], "%d.%m.%Y")

            # Calculate the number of days between the two dates
            delta = date2 - date1
            days_between = delta.days
            days_between_list.append(int(days_between))

    if len(days_between_list) == 0:
        return 0
    else:
        total = sum(days_between_list)
        average = total / len(days_between_list)
        return abs(average)


HOST = "127.0.0.1"
PORT = 6000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
print("Server is started")
print("Waiting for connections")
while True:
    server.listen()
    clientsocket, clientaddress = server.accept()
    newThread = ClientThread(clientsocket, clientaddress)
    newThread.start()