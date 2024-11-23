from tkinter import *
from tkinter import ttk
from tkinter import Tk, messagebox
from tkinter.ttk import Notebook
from tkcalendar import DateEntry
import mysql.connector
import bcrypt
from matplotlib import pyplot as plt
import numpy as np

myb = mysql.connector.connect(host="localhost", user="root", passwd="abcd1234", database="ExpenseTracker")

# Object return points there
mycursor = myb.cursor()
# Create users table if it doesn't exist
mycursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    username VARCHAR(255) PRIMARY KEY,
    password_hash VARCHAR(255)
)
''')

# Global variables for images and selection state
checked_image = None
unchecked_image = None
selection_dict = {}
item_to_id = {}

# Function to hash passwords
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Function to verify passwords
def verify_password(hashed, password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def Add_To_database(a, b, c):
    t = user_input.get().strip()
    print(t)
    adding = "Insert into " + t.lower() + " (DATE_OF_EXPENSE,TITLE,MONEY) values(%s,%s,%s)"
    entry = (a, b, c)
    mycursor.execute(adding, entry)
    myb.commit()
    print(mycursor.rowcount, "record inserted.")
    mycursor.execute("SELECT LAST_INSERT_ID()")
    last_id = mycursor.fetchone()[0]
    return last_id

# validating input fields
def validate():
    a = exp_date_field.get()
    b = title_input.get().strip()
    c = expense_input.get().strip()
    if (len(b) == 0 and len(c) == 0):
        messagebox.showerror("Error", "\tFields can't be empty\nAdd Expense and proper title for your expense!")
        return False

    elif (len(c) == 0):
        messagebox.showerror("Error", "Expense field is missing")
        return False

    elif (b == "Select one"):
        messagebox.showerror("Error", "Expense title is missing")
        return False

    val = 0
    try:
        val = float(expense_input.get())
        if (val <= 0):
            messagebox.showerror("Error", "Expense can't be negative or zero.")
            return  False

    except:
        messagebox.showerror("Error", "Enter only numerical value!")
        return False

    return True

# Adding expense after validating
def Addexpense():
    a = exp_date_field.get()
    b = title_input.get().strip()
    c = expense_input.get().strip()

    if (validate()):
        last_id = Add_To_database(a, b, c)
        data = [a, b, c]
        # To show it to user in tree view
        item_id = TVExpense.insert('', 'end', text='', image=unchecked_image, values=data)
        selection_dict[item_id] = False
        item_to_id[item_id] = last_id

def nameval():
    c = user_input.get().strip()
    password = pass_input.get().strip()

    if (len(c) == 0):
        messagebox.showerror("Error", "Username is missing")
        return False
    elif (c.isalpha() != True):
        messagebox.showerror("Error", "Username can't contain Numbers or special characters")
        return False
    elif (len(password) == 0):
        messagebox.showerror("Error", "Password cannot be empty.")
        return False
    else:
        return True

def already():
    mycursor.execute("SHOW TABLES")
    datab = []

    for x in mycursor:
        s = str(x)[2:-3]
        datab.append(s)
    c = 0
    a = user_input.get().strip()

    for i in datab:
        if a.lower() == i.lower():
            print(i)
            # messagebox.showerror("Error", "Username Already Exist")
            return False
        else:
            c = c + 1

    if c == len(datab):
        return True

def removethis():
    wel.destroy()

def remove():
    Name.destroy()

def Not_already():
    mycursor.execute("SHOW TABLES")
    datab = []

    for x in mycursor:
        s = str(x)[2:-3]
        datab.append(s)
    c = 0
    a = user_input.get().strip()

    for i in datab:
        if a.lower() == i.lower():
            return i
        else:
            c = c + 1

    if c == len(datab):
        messagebox.showerror("Error", "Username doesn't exist.\n Kindly sign-up first")
        return False

def login():
    removethis()
    if (nameval()):
        n = Not_already()
        password = pass_input.get().strip()
        mycursor.execute("SELECT password_hash FROM users WHERE username=%s", (n,))
        result = mycursor.fetchone()
        hashed_password = result[0].encode('utf-8')
        if (n):
            if verify_password(hashed_password, password):
                messagebox.showinfo("Success", "Login successful.")
                tab.tab(f1,state='normal')
                tab.tab(f2, state='normal')
                remove()
                # Check if 'id' column exists
                mycursor.execute("SHOW COLUMNS FROM " + n + " LIKE 'id'")
                result = mycursor.fetchone()
                if not result:
                    # Add 'id' column if it doesn't exist
                    alter_sql = "ALTER TABLE " + n + " ADD COLUMN id INT AUTO_INCREMENT PRIMARY KEY FIRST"
                    mycursor.execute(alter_sql)
                    myb.commit()
                mycursor.execute("Select id, DATE_OF_EXPENSE,TITLE, MONEY from " + n)
                myresult = mycursor.fetchall()
                for i in myresult:
                    id, date, title, money = i
                    data = [date, title, money]
                    item_id = TVExpense.insert('', 'end', text='', image=unchecked_image, values=data)
                    selection_dict[item_id] = False
                    item_to_id[item_id] = id
            else:
                messagebox.showerror("Error", "Invalid password.")

def signup():
    removethis()
    if (nameval()):
        if (already()):
            t = user_input.get().strip()
            password = pass_input.get().strip()
            hashed_password = hash_password(password)
            mycursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (t, hashed_password))
            myb.commit()
            str1 = "Create table " + t + "(id INT AUTO_INCREMENT PRIMARY KEY, DATE_OF_EXPENSE date,TITLE varchar(20),MONEY int)"
            mycursor.execute(str1)
            myb.commit()
            # messagebox.showinfo("Success", "Signup successful. You can now login.")
            print(mycursor.rowcount, "record inserted.")
            tab.tab(f1, state='normal')
            tab.tab(f2, state='normal')
            remove()
        else:
            messagebox.showerror("Error", "Username Already Exist")

def on_treeview_click(event):
    # Get the item that was clicked on
    item = TVExpense.identify_row(event.y)
    column = TVExpense.identify_column(event.x)
    # print(f"Clicked on item {item}, column {column}")
    if column == '#0' and item != '':
        # Toggle the checkbox image
        current_state = selection_dict.get(item, False)
        # Update the image
        if current_state:
            TVExpense.item(item, image=unchecked_image)
            selection_dict[item] = False
        else:
            TVExpense.item(item, image=checked_image)
            selection_dict[item] = True

def delete_selected():
    selected_items = [item_id for item_id, selected in selection_dict.items() if selected]
    if not selected_items:
        messagebox.showinfo("Info", "No expenses selected for deletion.")
        return
    t = user_input.get().strip()
    table_name = t.lower()
    for item_id in selected_items:
        # Get the database 'id' for this item
        db_id = item_to_id[item_id]
        # Delete from database
        delete_sql = "DELETE FROM " + table_name + " WHERE id = %s"
        mycursor.execute(delete_sql, (db_id,))
        myb.commit()
        # Delete from Treeview
        TVExpense.delete(item_id)
        # Remove from selection_dict and item_to_id
        del selection_dict[item_id]
        del item_to_id[item_id]
    messagebox.showinfo("Info", "Selected expenses deleted.")

GUI = Tk()
GUI.title("Expense Tracker")
GUI.geometry('700x450')
GUI.resizable(0, 0)

# Load checkbox images
checked_image = PhotoImage(file='checkbox.png')
unchecked_image = PhotoImage(file='checkbox_unchecked.png')

# Keep references to images to prevent garbage collection
GUI.checked_image = checked_image
GUI.unchecked_image = unchecked_image

# select page content by clicking on tabs
tab = Notebook(GUI)

# width and height
wel = Frame(tab, width=700, height=430)  # Welcome tab
Name = Frame(tab, width=700, height=430)
f1 = Frame(tab, width=700, height=430)  # Adding daily Expense
f2 = Frame(tab, width=700, height=430)  # Analysis

# adding tabs
tab.add(wel, text=f'{"Welcome": ^30s}')
tab.add(Name, text=f'{"Login": ^30s}')
tab.add(f1, text=f'{"Expense": ^30s}')
tab.add(f2, text=f'{"Expenditure Analysis": ^30s}')

tab.tab(f1, state='hidden')
tab.tab(f2, state='hidden')

# filling to whole content
tab.pack(fill=BOTH)

# background-color
wel.config(bg="#354a5f")
welcome = Label(wel, text='Expense Tracker', font=('Times New Roman',36,"bold","italic"), bg="#354a5f", fg="white")
welcome.grid(row=0, column=0,padx=100, pady=100)
# ipadx=100, ipady=100)

next = Button(wel, text='>>', command=removethis,bg="red",fg="white")
next.grid(row=1, column=1, padx=10, pady=70, ipadx=40, ipady=10)

# -----UserName----
Name.config(background="#2b3d4f")
yellow = Label(Name, text="Login / Sign Up ", bg="#f99406",fg="White",font=('Times New Roman',30,"bold","italic"))
yellow.grid(row=0, column=0,columnspan=10,ipady=10,ipadx=220)

user = Label(Name, text='Username: ', font=('Times New Roman', 24), bg="#2b3d4f",fg="white")
user.grid(row=3, column=2, padx=55, pady=30)

user = Label(Name, text='Password: ', font=('Times New Roman', 24), bg="#2b3d4f",fg="white")
user.grid(row=4, column=2, padx=55, pady=30)

user_input = StringVar()
pass_input = StringVar()
user_field = Entry(Name, textvariable=user_input, font=('Times New Roman', 18))
user_field.grid(row=3, column=3, padx=40, pady=30)

pass_field = Entry(Name, textvariable=pass_input, font=('Times New Roman', 18),show="*")
pass_field.grid(row=4, column=3, padx=40, pady=30)

# ----Login------
login_button = Button(Name, text='Login', bg="#1bb6fe",fg="white", font=('Times New Roman', 18),command=login)
login_button.grid(row=5, column=2, padx=100, pady=10, ipadx=40, ipady=5)

# ----SignUp------
signup_button = Button(Name, text='Sign Up', command=signup,bg="red",fg="white",font=('Times New Roman', 18))
signup_button.grid(row=5, column=3, padx=0, pady=10, ipadx=30, ipady=5)

f1.config(bg="#2b3d4f")
f2.config(bg="#2b3d4f")

# ----Date------
exp_date = Label(f1, text='Date:', font=('Times New Roman', 18,"bold"), bg="#2b3d4f",fg="white")
exp_date.grid(row=0, column=0, padx=5, pady=5)

# pip install tkcalendar
exp_date_field = DateEntry(f1, width=19, date_pattern='YYYY/MM/DD', background='blue',foreground="#2b3d4f",
                           font=('Times New Roman', 18),bg="#1bb6fe",fg="white")
exp_date_field.grid(row=0, column=1, padx=55, pady=15)

# ----Title------
title = Label(f1, text='Title:', font=('Times New Roman', 18, "bold"), background="#2b3d4f",fg="white")
title.grid(row=1, column=0, padx=5, pady=15)

title_input = StringVar(GUI)

# Drop down menu
option = [
    "Bill Payment",
    "Stationary",
    "Grocery",
    "Restaurant",
    "Shopping",
    "Withdrawal",
    "Social Cause",
    "Rent"
]

# datatype of menu text
drop = OptionMenu(f1, title_input, *option)
drop.config(width=17, font=('Times Roman', 16),bg="#1bb6fe",fg="white")
title_input.set("Select one")
drop.grid(row=1, column=1, padx=55, pady=15)

# ----Expense------
exp = Label(f1, text='Expense:', font=('Times New Roman', 18, "bold"), bg="#2b3d4f",fg="white")
exp.grid(row=2, column=0, padx=55, pady=15)

expense_input = StringVar()

exp_field = Entry(f1, textvariable=expense_input, font=('Times New Roman', 18),bg="#1bb6fe",fg="white")
exp_field.grid(row=2, column=1, padx=55, pady=15)

# ----Add Button----
bf1Add = Button(f1, text='Add', command=Addexpense,bg="red", font=('Times New Roman', 12, "bold"),fg="white")
bf1Add.grid(row=3, column=1, padx=10, pady=10, ipadx=20)

# Treeview with checkboxes
TVList = ['Date', 'Title', 'Expense']
TVExpense = ttk.Treeview(f1, columns=TVList, show='tree headings', height=5)

TVExpense.heading('#0', text='Select')  # First column for checkboxes
for i in TVList:
    TVExpense.heading(i, text=i.title())

TVExpense.grid(row=4, column=0, padx=45, pady=15, columnspan=3)

# Bind click event
TVExpense.bind('<Button-1>', on_treeview_click)

# ----Delete Button----
delete_button = Button(f1, text='Delete Selected', command=delete_selected,bg="red", font=('Times New Roman', 12, "bold"),fg="white")
delete_button.grid(row=5, column=0, padx=10, pady=10, ipadx=20)

# Frame 2
# ---------------------------------------------Expenditure Analysis------------------------------------------------

# title = Label(f2, text='Expenditure Analysis', font=('Times New Roman', 34), background="#f99406",fg="white")
# title.grid(row=0, column=0, padx=55, pady=15)

title = Label(f2, text="Expenditure Analysis ", bg="#f99406",fg="White",font=('Times New Roman',30,"bold","italic"))
title.grid(row=0, column=0,ipady=10,ipadx=175)

def click_weekly():
    t = user_input.get().strip()
    en = "expensetracker." + t.lower()
    mycursor.execute(
        "Select TITLE, sum(Money) TOTAL_EXPENSE from " + en + " where DATE_OF_EXPENSE between DATE_SUB( curdate(), INTERVAL 8 DAY ) and curdate() group by Title;")
    myresult = mycursor.fetchall()

    label = []
    slices = []

    for i in myresult:
        j, k = i
        label.append(j)
        slices.append(k)
    # slices = [1000, 2000]
    plt.style.use("fivethirtyeight")
    colors = ['Blue', 'Yellow', 'Green', 'Red', 'Orange', 'lightblue', 'pink', 'Purple']
    plt.title("Weekly Chart")
    print(slices)
    slc = ["$ "+str(i) for i in slices]
    slices=np.array(slices)
    x, p, texts = plt.pie(slices / slices.sum(),labels=slc, labeldistance=0.75, colors=colors, radius=1.2, autopct="%1.1f%%", normalize=False)
    plt.legend(x, label, loc='best', bbox_to_anchor=(-0.1, 1.), fontsize=15)
    plt.tight_layout()
    plt.show()

# button for knowing the distribution of weekly expense
button_weekly = Button(f2, text='Weekly', command=click_weekly, bg="#1bb6fe",fg="white",font=('Times New Roman',18))
button_weekly.grid(row=1, column=0, padx=50, pady=30, ipadx=10)

def click_monthly():
    t = user_input.get().strip()
    en = "expensetracker." + t.lower()
    mycursor.execute(
        "Select TITLE, sum(Money) TOTAL_EXPENSE from " + en + " where DATE_OF_EXPENSE between DATE_SUB( curdate(), INTERVAL 1 MONTH) and curdate() group by Title");
    myresult = mycursor.fetchall()  # fetching data from database and then splitting acc. to need

    label = []
    slices = []
    for i in myresult:
        j, k = i  # As it was stored in tuple of list form
        label.append(j)  # we converted to list
        slices.append(k)

    plt.style.use("fivethirtyeight")  # Style selected
    colors = ['Blue', 'Yellow', 'Green', 'Red', 'Orange', 'lightblue', 'pink', 'Purple']
    slc = ["$ "+str(i) for i in slices]
    slices=np.array(slices)
    x, p, texts = plt.pie(slices / slices.sum(), labels=slc, labeldistance=0.75, colors=colors, radius=1.2, autopct="%1.1f%%", normalize=False)  # fixing radius and all
    plt.legend(x, label, loc='best', bbox_to_anchor=(-0.1, 1.), fontsize=15)  # Listing the details
    plt.title("Monthly Chart")
    plt.tight_layout()
    plt.show()

# button for knowing the distribution of monthly expense
button_monthly = Button(f2, text='Monthly', command=click_monthly,bg="#1bb6fe",fg="white",font=('Times New Roman',18))
button_monthly.grid(row=2, column=0, padx=50, pady=30, ipadx=10)

def click_yearly():
    t = user_input.get().strip()
    en = "expensetracker." + t.lower()
    mycursor.execute(
        "Select TITLE, sum(Money) TOTAL_EXPENSE from " + en + " where DATE_OF_EXPENSE between DATE_SUB( curdate(), INTERVAL 1 YEAR) and curdate() group by Title");
    myresult = mycursor.fetchall()

    label = []
    slices = []
    for i in myresult:
        j, k = i
        label.append(j)
        slices.append(k)

    plt.style.use("fivethirtyeight")
    colors = ['Blue', 'Yellow', 'Green', 'Red', 'Orange', 'lightblue', 'pink', 'Purple']
    slc = ["$ "+str(i) for i in slices]
    slices=np.array(slices)
    x, p, texts = plt.pie(slices / slices.sum(), labels=slc, labeldistance=0.75, colors=colors, radius=1.2, autopct="%1.1f%%", normalize=False)
    plt.legend(x, label, loc='best', bbox_to_anchor=(-0.1, 1.), fontsize=15)
    plt.title("Yearly Chart")
    plt.tight_layout()
    plt.show()

# button for knowing the distribution of yearly expense
button_yearly = Button(f2, text='Yearly', command=click_yearly,bg="#1bb6fe",fg="white",font=('Times New Roman',18))
button_yearly.grid(row=3, column=0, padx=50, pady=30, ipadx=20)

GUI.mainloop()