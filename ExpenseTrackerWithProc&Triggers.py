from tkinter import *
from tkinter import ttk
from tkinter import Tk, messagebox
from tkinter.ttk import Notebook
from tkcalendar import DateEntry
import mysql.connector
import bcrypt
from matplotlib import pyplot as plt
import numpy as np
from tkinter import simpledialog

# Connect to the MySQL database
myb = mysql.connector.connect(host="localhost", user="root", passwd="abcd1234", database="ExpenseTracker")

# Create a cursor object
mycursor = myb.cursor()

# Create the 'users' table if it doesn't exist
mycursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    username VARCHAR(255) PRIMARY KEY,
    password_hash VARCHAR(255)
)
''')
myb.commit()

# Function to hash passwords
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Function to verify passwords
def verify_password(hashed, password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

# Function to add expense using stored procedure
def Add_To_database(a, b, c):
    t = user_input.get().strip()
    print(t)
    # Call stored procedure to add expense
    mycursor.callproc('AddExpense', (t.lower(), a, b, int(c)))
    myb.commit()
    print(mycursor.rowcount, "record inserted.")


# Validating input fields
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
        data = [a, b, c]
        # Add to database
        Add_To_database(a, b, c)
        # Retrieve the last inserted id
        mycursor.execute("SELECT MAX(id) FROM " + GUI.name)
        result = mycursor.fetchone()
        if result:
            id = result[0]
            TVExpense.insert('', 'end', id=id, values=data)
        else:
            pass

def nameval():
    c = user_input.get().strip()
    password = pass_input.get().strip()

    if (len(c) == 0):
        messagebox.showerror("Error", "Username is missing")
        return False
    elif (not c.isalpha()):
        messagebox.showerror("Error", "Username can't contain numbers or special characters")
        return False
    elif (len(password) == 0):
        messagebox.showerror("Error", "Password cannot be empty.")
        return False
    else:
        return True

def already():
    mycursor.execute("SELECT username FROM users")
    users = [x[0].lower() for x in mycursor.fetchall()]
    a = user_input.get().strip().lower()
    if a in users:
        return False
    else:
        return True

def removethis():
    wel.destroy()

def remove():
    Name.destroy()

def Not_already():
    mycursor.execute("SELECT username FROM users")
    users = [x[0] for x in mycursor.fetchall()]
    a = user_input.get().strip()
    for user in users:
        if a.lower() == user.lower():
            return user
    messagebox.showerror("Error", "Username doesn't exist.\n Kindly sign-up first")
    return False

def login():
    removethis()
    if (nameval()):
        n = Not_already()
        print(n)
        password = pass_input.get().strip()
        if n:
            mycursor.execute("SELECT password_hash FROM users WHERE username=%s", (n,))
            result = mycursor.fetchone()
            if result:
                hashed_password = result[0].encode('utf-8')
                if verify_password(hashed_password, password):
                    messagebox.showinfo("Success", "Login successful.")
                    tab.tab(f1,state='normal')
                    tab.tab(f2, state='normal')
                    remove()
                    # Call stored procedure to get expenses
                    mycursor.callproc('GetExpenses', (n,))
                    for result in mycursor.stored_results():
                        myresult = result.fetchall()
                    GUI.name = n
                    for i in myresult:
                        print(i)
                        TVExpense.insert('', 'end', id=i[0], values=i[1:])
                    # Call stored procedure to get categories
                    mycursor.callproc('GetCategories', (GUI.name,))
                    for result in mycursor.stored_results():
                        res = result.fetchall()
                    for i in res:
                        if i[0] not in GUI.opt:
                            GUI.opt.append(i[0])
                            drop['menu'].add_command(label=i[0], command=lambda value=i[0]: title_input.set(value))
                else:
                    messagebox.showerror("Error", "Invalid password.")
            else:
                messagebox.showerror("Error", "User not found.")

def signup():
    removethis()
    if (nameval()):
        if (already()):
            t = user_input.get().strip()
            password = pass_input.get().strip()
            hashed_password = hash_password(password)
            # Call stored procedure to create user
            mycursor.callproc('CreateUser', (t, hashed_password.decode('utf-8')))
            myb.commit()
            GUI.name = t
            # Insert default categories
            for i in GUI.opt:
                mycursor.callproc('AddCategory', (t, i))
                myb.commit()
            print(mycursor.rowcount, "record inserted.")
            tab.tab(f1, state='normal')
            tab.tab(f2, state='normal')
            remove()
        else:
            messagebox.showerror("Error", "Username Already Exist")

def on_select_all():
    for exp in TVExpense.get_children():
        TVExpense.selection_add(exp)

def delete_selection():
    selected_expenses = TVExpense.selection()
    print(selected_expenses)
    for exp in selected_expenses:
        # Call stored procedure to delete expense
        mycursor.callproc('DeleteExpense', (GUI.name, int(exp)))
        myb.commit()
        print("Deleted expense with id:", exp)
        TVExpense.delete(exp)

def prompt_for_category():
    while True:
        cat = simpledialog.askstring("Add Category", "Enter a new category name:")
        if not cat:
            messagebox.showerror("Error", "Category name cannot be empty. Please try again.")
            return
        elif cat.strip() in [c for c in GUI.opt]:
            messagebox.showerror("Error", "Category already exists. Please enter a unique category.")
        else:
            add_cat(cat.strip())
            messagebox.showinfo("Success", f"Category '{cat.strip()}' added successfully.")
            break

def add_cat(cat):
    try:
        # Call stored procedure to add category
        mycursor.callproc('AddCategory', (GUI.name, cat))
        myb.commit()
        GUI.opt.append(cat)
        drop['menu'].add_command(label=cat, command=lambda value=cat: title_input.set(value))
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"An error occurred while adding the category: {e}")

# Initialize the main window
GUI = Tk()
GUI.title("Expense Tracker")
GUI.geometry('700x600')
GUI.resizable(1, 1)

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
GUI.opt = option

# Set up the notebook tabs
tab = Notebook(GUI)

# Create frames for each tab
wel = Frame(tab, width=700, height=600)  # Welcome tab
Name = Frame(tab, width=700, height=600)
f1 = Frame(tab, width=700, height=600)  # Adding daily Expense
f2 = Frame(tab, width=700, height=600)  # Analysis

# Add tabs to the notebook
tab.add(wel, text=f'{"Welcome": ^30s}')
tab.add(Name, text=f'{"Login": ^30s}')
tab.add(f1, text=f'{"Expense": ^30s}')
tab.add(f2, text=f'{"Expenditure Analysis": ^30s}')

# Hide certain tabs until needed
tab.tab(f1, state='hidden')
tab.tab(f2, state='hidden')

# Pack the notebook
tab.pack(fill=BOTH)

# Welcome Tab Configuration
wel.config(bg="#354a5f")
welcome = Label(wel, text='Expense Tracker', font=('Times New Roman',36,"bold","italic"), bg="#354a5f", fg="white")
welcome.grid(row=0, column=0,padx=100, pady=100)

next = Button(wel, text='>>', command=removethis,bg="red",fg="white")
next.grid(row=1, column=1, padx=10, pady=70, ipadx=40, ipady=10)

# Login/Sign Up Tab Configuration
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

# Login and Sign Up Buttons
login_button = Button(Name, text='Login', bg="#1bb6fe",fg="white", font=('Times New Roman', 18),command=login)
login_button.grid(row=5, column=2, padx=100, pady=10, ipadx=40, ipady=5)

signup_button = Button(Name, text='Sign Up', command=signup,bg="red",fg="white",font=('Times New Roman', 18))
signup_button.grid(row=5, column=3, padx=0, pady=10, ipadx=30, ipady=5)

# Expense Tab Configuration
f1.config(bg="#2b3d4f")
f2.config(bg="#2b3d4f")

# Date Entry
exp_date = Label(f1, text='Date:', font=('Times New Roman', 18,"bold"), bg="#2b3d4f",fg="white")
exp_date.grid(row=0, column=0, padx=5, pady=5)

exp_date_field = DateEntry(f1, width=19, date_pattern='YYYY/MM/DD', background='blue',foreground="#2b3d4f",
                           font=('Times New Roman', 18),bg="#1bb6fe",fg="white")
exp_date_field.grid(row=0, column=1, padx=55, pady=15)

# Title Entry
title = Label(f1, text='Title:', font=('Times New Roman', 18, "bold"), background="#2b3d4f",fg="white")
title.grid(row=1, column=0, padx=5, pady=15)

title_input = StringVar(GUI)

drop = OptionMenu(f1, title_input, *GUI.opt)
drop.config(width=17, font=('Times Roman', 16),bg="#1bb6fe",fg="white")
title_input.set("Select one")
drop.grid(row=1, column=1, padx=55, pady=15)

add_category_button = Button(f1, text='Add Category', command=prompt_for_category, bg="#1bb6fe", fg="white", font=('Times New Roman', 12, "bold"))
add_category_button.grid(row=6, column=1, padx=10, pady=10, ipadx=20)

# Expense Amount Entry
exp = Label(f1, text='Expense:', font=('Times New Roman', 18, "bold"), bg="#2b3d4f",fg="white")
exp.grid(row=2, column=0, padx=55, pady=15)

expense_input = StringVar()

exp_field = Entry(f1, textvariable=expense_input, font=('Times New Roman', 18),bg="#1bb6fe",fg="white")
exp_field.grid(row=2, column=1, padx=55, pady=15)

# Add and Delete Buttons
bf1Add = Button(f1, text='Add Expense', command=Addexpense,bg="red", font=('Times New Roman', 12, "bold"),fg="white")
bf1Add.grid(row=3, column=1, padx=10, pady=10, ipadx=20)

delete_button = Button(f1, text='Delete Selected', command=delete_selection,bg="red", font=('Times New Roman', 12, "bold"),fg="white")
delete_button.grid(row=5, column=0, padx=10, pady=10, ipadx=20)
select_button = Button(f1, text='Select All', command=on_select_all,bg="red", font=('Times New Roman', 12, "bold"),fg="white")
select_button.grid(row=5, column=1, padx=10, pady=10, ipadx=20)

# Expense Treeview
TVList = ['Date', 'Title', 'Expense']
TVList_id = ['id','Date', 'Title', 'Expense']
TVExpense = ttk.Treeview(f1, column=TVList_id, show='headings', height=5)

for i in TVList:
    TVExpense.heading(i, text=i.title())
TVExpense.grid(row=4, column=0, padx=45, pady=15, columnspan=3)

# Expenditure Analysis Tab Configuration
title = Label(f2, text="Expenditure Analysis ", bg="#f99406",fg="White",font=('Times New Roman',30,"bold","italic"))
title.grid(row=0, column=0,ipady=10,ipadx=175)

def click_weekly():
    t = user_input.get().strip()
    # Call stored procedure to get weekly expenses
    mycursor.callproc('GetWeeklyExpenses', (t.lower(),))
    for result in mycursor.stored_results():
        myresult = result.fetchall()
    label = []
    slices = []
    for i in myresult:
        j, k = i
        label.append(j)
        slices.append(k)
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

button_weekly = Button(f2, text='Weekly', command=click_weekly, bg="#1bb6fe",fg="white",font=('Times New Roman',18))
button_weekly.grid(row=1, column=0, padx=50, pady=30, ipadx=10)

def click_monthly():
    t = user_input.get().strip()
    # Call stored procedure to get monthly expenses
    mycursor.callproc('GetMonthlyExpenses', (t.lower(),))
    for result in mycursor.stored_results():
        myresult = result.fetchall()
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
    plt.title("Monthly Chart")
    plt.tight_layout()
    plt.show()

button_monthly = Button(f2, text='Monthly', command=click_monthly,bg="#1bb6fe",fg="white",font=('Times New Roman',18))
button_monthly.grid(row=2, column=0, padx=50, pady=30, ipadx=10)

def click_yearly():
    t = user_input.get().strip()
    # Call stored procedure to get yearly expenses
    mycursor.callproc('GetYearlyExpenses', (t.lower(),))
    for result in mycursor.stored_results():
        myresult = result.fetchall()
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

button_yearly = Button(f2, text='Yearly', command=click_yearly,bg="#1bb6fe",fg="white",font=('Times New Roman',18))
button_yearly.grid(row=3, column=0, padx=50, pady=30, ipadx=20)

# Start the main event loop
GUI.mainloop()
