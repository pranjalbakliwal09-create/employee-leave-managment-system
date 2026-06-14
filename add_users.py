import sqlite3

conn = sqlite3.connect('employees.db')
cursor = conn.cursor()

users = [
    (
        "Admin",
        "admin@gmail.com",
        "admin123",
        "admin",
        30,
        0
    ),

    (
        "Rahul",
        "rahul@gmail.com",
        "1234",
        "employee",
        24,
        5
    ),

    (
        "Priya",
        "priya@gmail.com",
        "1234",
        "employee",
        20,
        3
    )
]

cursor.executemany('''
INSERT OR IGNORE INTO employees
(name, email, password, role, total_leaves, used_leaves)
VALUES (?, ?, ?, ?, ?, ?)
''', users)

conn.commit()
conn.close()

print("Users Added!")