import mysql.connector

myb = mysql.connector.connect(host="localhost", user="root", passwd="abcd1234", database="ExpenseTracker")
mycursor = myb.cursor()

#Creating table from query
# id INT AUTO_INCREMENT PRIMARY KEY, 
mycursor.execute("CREATE TABLE Expense (DATE_OF_EXPENSE date,TITLE varchar(20),MONEY int)")
myb.commit()