from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
from flask_mail import Mail, Message


app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- EMAIL CONFIG ---------------- #

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'admin@gmail.com'
app.config['MAIL_PASSWORD'] = 'admin123'

mail = Mail(app)


# ---------------- DATABASE CONNECTION ---------------- #

def get_db_connection():
    conn = sqlite3.connect('employees.db')
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- LOGIN ---------------- #

@app.route('/', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM employees WHERE email=? AND password=?",
            (email, password)
        )

        user = cursor.fetchone()
        conn.close()

        if user:

            session['user_id'] = user['id']
            session['role'] = user['role']

            if user['role'] == 'admin':
                return redirect('/admin')

            return redirect('/dashboard')

        else:
            flash("Invalid email or password")

    return render_template('login.html')


# ---------------- DASHBOARD ---------------- #

@app.route('/dashboard')
def dashboard():

    if 'user_id' not in session:
        return redirect('/')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM employees WHERE id=?",
        (session['user_id'],)
    )

    user = cursor.fetchone()
    conn.close()

    return render_template('dashboard.html', user=user)


# ---------------- REQUEST LEAVE ---------------- #

@app.route('/request_leave', methods=['GET', 'POST'])
def request_leave():

    if 'user_id' not in session:
        return redirect('/')

    if request.method == 'POST':

        leave_type = request.form['leave_type']
        days = int(request.form['days'])
        reason = request.form['reason']

        employee_id = session['user_id']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT total_leaves, used_leaves FROM employees WHERE id=?",
            (employee_id,)
        )

        employee = cursor.fetchone()

        remaining = employee['total_leaves'] - employee['used_leaves']

        if days <= remaining:

            cursor.execute('''
                INSERT INTO leave_requests
                (employee_id, leave_type, days, reason, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                employee_id,
                leave_type,
                days,
                reason,
                'Pending'
            ))

            conn.commit()
            flash("Leave request submitted successfully")

        else:
            flash("Not enough leave balance")

        conn.close()

        return redirect('/dashboard')

    return render_template('request_leave.html')


# ---------------- ADMIN PANEL ---------------- #

@app.route('/admin')
def admin():

    if 'user_id' not in session:
        return redirect('/')

    if session['role'] != 'admin':
        return redirect('/dashboard')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT leave_requests.id,
               employees.name,
               employees.email,
               leave_requests.leave_type,
               leave_requests.days,
               leave_requests.reason,
               leave_requests.status
        FROM leave_requests
        INNER JOIN employees
        ON leave_requests.employee_id = employees.id
    """)

    leaves = cursor.fetchall()
    conn.close()

    return render_template('admin.html', leaves=leaves)


# ---------------- APPROVE LEAVE ---------------- #

@app.route('/approve/<int:id>')
def approve(id):

    if 'user_id' not in session:
        return redirect('/')

    if session['role'] != 'admin':
        return redirect('/dashboard')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT leave_requests.employee_id,
               leave_requests.days,
               leave_requests.status,
               employees.email,
               employees.name
        FROM leave_requests
        INNER JOIN employees
        ON leave_requests.employee_id = employees.id
        WHERE leave_requests.id=?
    """, (id,))

    leave = cursor.fetchone()

    if leave and leave['status'] == 'Pending':

        employee_id = leave['employee_id']
        days = leave['days']
        employee_email = leave['email']
        employee_name = leave['name']

        # Update leave request
        cursor.execute(
            "UPDATE leave_requests SET status='Approved' WHERE id=?",
            (id,)
        )

        # Update used leaves
        cursor.execute(
            "UPDATE employees SET used_leaves = used_leaves + ? WHERE id=?",
            (days, employee_id)
        )

        conn.commit()

        # ---------------- SEND EMAIL ---------------- #

        msg = Message(
            'Leave Approved',
            sender=app.config['MAIL_USERNAME'],
            recipients=[employee_email]
        )

        msg.body = f"""
Hello {employee_name},

Your leave request for {days} day(s) has been approved.

Thank you.
HR Department
"""

        mail.send(msg)

        flash("Leave approved and email sent")

    conn.close()

    return redirect('/admin')


# ---------------- REJECT LEAVE ---------------- #

@app.route('/reject/<int:id>')
def reject(id):

    if 'user_id' not in session:
        return redirect('/')

    if session['role'] != 'admin':
        return redirect('/dashboard')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get employee email
    cursor.execute("""
        SELECT employees.email,
               employees.name
        FROM leave_requests
        INNER JOIN employees
        ON leave_requests.employee_id = employees.id
        WHERE leave_requests.id=?
    """, (id,))

    employee = cursor.fetchone()

    cursor.execute(
        "UPDATE leave_requests SET status='Rejected' WHERE id=?",
        (id,)
    )

    conn.commit()

    # ---------------- SEND REJECTION EMAIL ---------------- #

    if employee:

        msg = Message(
            'Leave Rejected',
            sender=app.config['MAIL_USERNAME'],
            recipients=[employee['email']]
        )

        msg.body = f"""
Hello {employee['name']},

Your leave request has been rejected.

Thank you.
HR Department
"""

        mail.send(msg)

    conn.close()

    return redirect('/admin')


# ---------------- LEAVE HISTORY ---------------- #

@app.route('/history/<int:id>')
def history(id):

    if 'user_id' not in session:
        return redirect('/')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM leave_requests WHERE employee_id=?",
        (id,)
    )

    history = cursor.fetchall()
    conn.close()

    return render_template('history.html', history=history)


# ---------------- LOGOUT ---------------- #

@app.route('/logout')
def logout():

    session.clear()

    return redirect('/')



if __name__ == '__main__':
    app.run(debug=True)