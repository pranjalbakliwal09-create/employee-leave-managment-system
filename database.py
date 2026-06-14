import sqlite3

conn = sqlite3.connect('employees.db')

cursor = conn.cursor()

# Employees Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    password TEXT,
    role TEXT,
    total_leaves INTEGER,
    used_leaves INTEGER
)
''')

# Leave Requests Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS leave_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER,
    leave_type TEXT,
    days INTEGER,
    reason TEXT,
    status TEXT
)
''')

conn.commit()
conn.close()

print("Database Ready!")