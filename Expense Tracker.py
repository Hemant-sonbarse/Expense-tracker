import datetime
import sqlite3
from tkcalendar import DateEntry
from tkinter import *
import tkinter.messagebox as mb
import tkinter.ttk as ttk

# --- Database Setup ---
def setup_database():
    """Initialize the database and create the necessary table."""
    conn = sqlite3.connect("ExpenseTracker.db")
    cursor = conn.cursor()
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS ExpenseTracker 
        (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
         Date DATETIME, 
         Payee TEXT, 
         Description TEXT, 
         Amount FLOAT, 
         ModeOfPayment TEXT)'''
    )
    conn.commit()
    return conn


# --- GUI Functions ---
def clear_fields():
    """Clear all input fields in the data entry frame."""
    today = datetime.datetime.now().date()
    date.set_date(today)
    payee.set("")
    desc.set("")
    amnt.set(0.0)
    MoP.set("Cash")
    table.selection_remove(*table.selection())

def list_all_expenses():
    """Fetch and display all expenses in the table, and update the total expense."""
    table.delete(*table.get_children())
    total_expense = 0.0
    for record in db.execute("SELECT * FROM ExpenseTracker").fetchall():
        table.insert("", END, values=record)
        total_expense += record[4]  # Add the amount to total_expense
    update_total_expense(total_expense)

def add_expense():
    """Add a new expense to the database."""
    if not all([date.get_date(), payee.get(), desc.get(), amnt.get(), MoP.get()]):
        mb.showerror("Fields Missing", "Please fill all the fields before adding an expense.")
        return
    db.execute(
        '''INSERT INTO ExpenseTracker (Date, Payee, Description, Amount, ModeOfPayment) 
        VALUES (?, ?, ?, ?, ?)''',
        (date.get_date(), payee.get(), desc.get(), amnt.get(), MoP.get())
    )
    db.commit()
    list_all_expenses()
    clear_fields()
    mb.showinfo("Expense Added", "The expense was added successfully!")

def delete_expense():
    """Delete the selected expense from the database."""
    selected_item = table.selection()
    if not selected_item:
        mb.showerror("No Selection", "Please select an expense to delete.")
        return
    expense_id = table.item(selected_item)["values"][0]
    db.execute("DELETE FROM ExpenseTracker WHERE ID = ?", (expense_id,))
    db.commit()
    list_all_expenses()
    mb.showinfo("Expense Deleted", "The selected expense has been deleted.")

def edit_expense():
    """Edit the selected expense."""
    selected_item = table.selection()
    if not selected_item:
        mb.showerror("No Selection", "Please select an expense to edit.")
        return

    values = table.item(selected_item)["values"]
    date.set_date(values[1])
    payee.set(values[2])
    desc.set(values[3])
    amnt.set(values[4])
    MoP.set(values[5])

    def save_changes():
        db.execute(
            '''UPDATE ExpenseTracker 
            SET Date = ?, Payee = ?, Description = ?, Amount = ?, ModeOfPayment = ? 
            WHERE ID = ?''',
            (date.get_date(), payee.get(), desc.get(), amnt.get(), MoP.get(), values[0]),
        )
        db.commit()
        list_all_expenses()
        clear_fields()
        mb.showinfo("Expense Updated", "The expense was updated successfully!")
        edit_button.destroy()

    edit_button = Button(data_entry_frame, text="Save Changes", command=save_changes, bg="#4CAF50", fg="white")
    edit_button.place(x=10, y=450)

def delete_all_expenses():
    """Delete all expenses from the database."""
    confirm = mb.askyesno("Confirm Deletion", "Are you sure you want to delete all expenses?")
    if confirm:
        db.execute("DELETE FROM ExpenseTracker")
        db.commit()
        list_all_expenses()
        mb.showinfo("All Expenses Deleted", "All expenses have been deleted successfully.")

def update_total_expense(total):
    """Update the total expense label at the bottom center."""
    total_label.config(text=f"Total Expense: ₹{total:.2f}")

# --- Entry Widget Helper ---
def on_focus_in(event):
    """Clear the default value of 0.0 in the Amount field on focus."""
    if amnt.get() == 0.0:
        amnt.set("")  # Clear the default 0.0 when the field is focused on

# --- GUI Setup ---
db = setup_database()

# Initialize GUI Window
root = Tk()
root.title("Expense Tracker")
root.geometry("1200x550")
root.resizable(0, 0)

# Variables
date = DateEntry()
payee = StringVar()
desc = StringVar()
amnt = DoubleVar(value=0.0)
MoP = StringVar(value="Cash")

# Frames
data_entry_frame = Frame(root, bg="#f7f7f7")
data_entry_frame.place(x=0, y=30, relheight=0.95, relwidth=0.25)

buttons_frame = Frame(root, bg="#e0e0e0")
buttons_frame.place(relx=0.25, rely=0.05, relwidth=0.75, relheight=0.21)

tree_frame = Frame(root, bg="white")
tree_frame.place(relx=0.25, rely=0.26, relwidth=0.75, relheight=0.74)

# Title Label
Label(root, text="EXPENSE TRACKER", font=("Arial", 16, "bold"), bg="#3f51b5", fg="white").pack(side=TOP, fill=X)

# Data Entry Fields
Label(data_entry_frame, text="Date:", bg="#f7f7f7", fg="black", font=("Arial", 12)).place(x=10, y=50)
DateEntry(data_entry_frame, textvariable=date).place(x=100, y=50)

Label(data_entry_frame, text="Payee:", bg="#f7f7f7", fg="black", font=("Arial", 12)).place(x=10, y=100)
Entry(data_entry_frame, textvariable=payee).place(x=100, y=100)

Label(data_entry_frame, text="Description:", bg="#f7f7f7", fg="black", font=("Arial", 12)).place(x=10, y=150)
Entry(data_entry_frame, textvariable=desc).place(x=100, y=150)

Label(data_entry_frame, text="Amount:", bg="#f7f7f7", fg="black", font=("Arial", 12)).place(x=10, y=200)
amount_entry = Entry(data_entry_frame, textvariable=amnt)
amount_entry.place(x=100, y=200)
amount_entry.bind("<FocusIn>", on_focus_in)  # Bind the FocusIn event

Label(data_entry_frame, text="Mode of Payment:", bg="#f7f7f7", fg="black", font=("Arial", 12)).place(x=10, y=250)
OptionMenu(data_entry_frame, MoP, "Cash", "Cheque", "Credit Card", "Debit Card", "UPI", "Other Methods").place(x=150, y=245)

Button(data_entry_frame, text="Add Expense", command=add_expense, bg="#4CAF50", fg="white").place(x=10, y=300)
Button(data_entry_frame, text="Clear Fields", command=clear_fields, bg="#607d8b", fg="white").place(x=150, y=300)

# Buttons Frame
Button(buttons_frame, text="Delete Expense", command=delete_expense, bg="#f44336", fg="white").pack(side=LEFT, padx=20)
Button(buttons_frame, text="Edit Expense", command=edit_expense, bg="#FF9800", fg="white").pack(side=LEFT, padx=20)
Button(buttons_frame, text="Delete All Expenses", command=delete_all_expenses, bg="#b71c1c", fg="white").pack(side=LEFT, padx=20)

# Treeview for Expense Records
table = ttk.Treeview(tree_frame, columns=("ID", "Date", "Payee", "Description", "Amount", "ModeOfPayment"), show="headings")
table.heading("ID", text="ID")
table.heading("Date", text="Date")
table.heading("Payee", text="Payee")
table.heading("Description", text="Description")
table.heading("Amount", text="Amount")
table.heading("ModeOfPayment", text="Mode of Payment")
table.pack(fill=BOTH, expand=True)

# Total Expense Label (Bottom Center)
total_label = Label(root, text="Total Expense: ₹0.00", font=("Arial", 14), bg="#f7f7f7")
total_label.pack(side=BOTTOM, fill=X)

# Populate Table
list_all_expenses()

# Start GUI Loop
root.mainloop()
