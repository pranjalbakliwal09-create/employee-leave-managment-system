import sqlite3

conn = sqlite3.connect('employees.db')

cursor = conn.cursor()

cursor.execute("SELECT * FROM employees")

data = cursor.fetchall()

print(data)

conn.close()