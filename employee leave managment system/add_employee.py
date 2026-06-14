import sqlite3

conn = sqlite3.connect('employees.db')

cursor = conn.cursor()

employees = [
    ("Rahul", 24, 5),
    ("Priya", 20, 3),
    ("Amit", 18, 10),
    ("Sneha", 30, 8)
]

cursor.executemany('''
INSERT INTO employees (name, total_leaves, used_leaves)
VALUES (?, ?, ?)
''', employees)

conn.commit()
conn.close()

print("Employees Added Successfully!")