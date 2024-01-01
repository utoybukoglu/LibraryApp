from tkinter import *
import os

def managerPanel(managerName):
    book_dict = {}
    file_path = os.path.join(os.path.dirname(__file__), 'books.txt')
    with open(file_path, "r") as file:
        for line in file:
            book_dict[line.strip().split(";")[2]] = line.strip().split(";")[1]
    file.close()

    master = Tk()
    master.title("Manager Panel")

    report_frame = Frame(master)
    report_frame.grid(row=0, column=0, padx=5, pady=5, sticky=W)

    main_label = Label(report_frame, text="REPORTS")
    main_label.grid(row=1, column=1)

    row = 2
    selected_report_var = StringVar()  # Create a StringVar to store the selected report

    report_contents = ["What is the most rented book overall?", "Which librarian has the highest number of operations?", "What is the total generated revenue by the library?", "What is the average rental period for the 'Harry Potter' book?"]
    reports_numbers = ["1", "2", "3", "4"]  # Define your report options

    i = 0
    for report_num in reports_numbers:
        report_label = Label(report_frame, text=f"({report_num}) {report_contents[i]}")
        report_label.grid(row=row, column=1, padx=10, sticky=W)

        c1 = Radiobutton(report_frame, text="", variable=selected_report_var, value=report_num)
        c1.grid(row=row, column=0, padx=5, sticky=E)

        row += 1
        i += 1

    report_str_var = StringVar()

    button_frame = Frame(master)
    button_frame.grid(row=row + 1, column=0, padx=50, pady=5, sticky=W)

    def send_report():
        selected_report = selected_report_var.get()

        if selected_report:
            report_str = "report;" + selected_report
            report_str_var.set(report_str)  # Set the value in the StringVar
            master.destroy()
        else:
            # Handle the case where no radio button is selected
            # You can display an error message or take other appropriate action
            pass

    create_button = Button(button_frame, text="Create", command=send_report)
    close_button = Button(button_frame, text="Close", command=master.destroy)

    create_button.grid(row=0, column=0)
    close_button.grid(row=0, column=2)

    master.mainloop()

    return report_str_var.get()  # Retrieve the value from StringVar after mainloop