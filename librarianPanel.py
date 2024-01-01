from tkinter import *
import os

def librarianPanel(librarianName):
    book_dict = {}
    bookId_dict = {}
    file_path = os.path.join(os.path.dirname(__file__), 'books.txt')
    with open(file_path, "r") as file:
        for line in file:
            book_dict[line.strip().split(";")[2]] = line.strip().split(";")[1]#author:bookname
            bookId_dict[line.strip().split(";")[0]] = line.strip().split(";")[1]#id:bookname
    file.close()

    master = Tk()
    master.title("Librarian Panel")

    book_frame = Frame(master)
    book_frame.grid(row=0, column=0, padx=5, pady=5, sticky=W)

    main_label = Label(book_frame, text="BOOKS")
    main_label.grid(row=1, column=0)

    row = 2
    selected_books = {}  # Use a dictionary to store the Checkbutton variables
    for item in book_dict.items():
        book_label = Label(book_frame, text=f"{item[1]} by {item[0]}")
        book_label.grid(row=row, column=0, padx=10, sticky=W)

        var = IntVar()
        c1 = Checkbutton(book_frame, variable=var)
        c1.grid(row=row, column=1, padx=5, sticky=E)
        selected_books[item[1]] = var  # Store the variable in the dictionary

        row += 1

    date_label = Label(master, text="Date(dd.mm.yyyy):")
    date_label.grid(row=row + 1, column=0, sticky=W, padx=10)

    date_entry = Entry(master)
    date_entry.grid(row=row + 1, column=0, padx=135, pady=10)

    client_label = Label(master, text="Client's name:")
    client_label.grid(row=row + 2, column=0, sticky=W, padx=25)

    client_entry = Entry(master)
    client_entry.grid(row=row + 2, column=0, sticky=W, padx=125, pady=10)

    panel_return = StringVar()

    button_frame = Frame(master)
    button_frame.grid(row=row + 3, column=0, padx=50, pady=5, sticky=W)

    def rent_book():
        selected_books_list = [item for item, var in selected_books.items() if var.get()]
        date_value = date_entry.get()
        client_name = client_entry.get()

        rent_str = "rent;" + librarianName + ";" + client_name + ";" + date_value + ";"
        bookId_list = []
        i = 0
        for id in bookId_dict:
            if bookId_dict[id] == selected_books_list[i]:
                bookId_list.append(id)
                rent_str += id + ";"
                i+=1
                if i == len(selected_books_list):
                    break 
        rent_str = rent_str[:-1]

        panel_return.set(rent_str)  # Set the value in the StringVar
        master.destroy()

    def return_book():
        selected_books_list = [item for item, var in selected_books.items() if var.get()]
        date_value = date_entry.get()
        client_name = client_entry.get()

        return_str = "return;" + librarianName + ";" + client_name + ";" + date_value + ";"
        bookId_list = []
        i = 0
        for id in bookId_dict:
            if bookId_dict[id] == selected_books_list[i]:
                bookId_list.append(id)
                return_str += id + ";"
                i+=1
                if i == len(selected_books_list):
                    break
        return_str = return_str[:-1]
        panel_return.set(return_str)  # Set the value in the StringVar
        master.destroy()

    rent_button = Button(button_frame, text="Rent", command=rent_book)
    return_button = Button(button_frame, text="Return", command=return_book)
    close_button = Button(button_frame, text="Close", command=master.destroy)

    rent_button.grid(row=0, column=0)
    return_button.grid(row=0, column=1)
    close_button.grid(row=0, column=2)

    mainloop()

    return panel_return.get()  # Retrieve the value from StringVar after mainloop