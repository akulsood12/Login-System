from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import smtplib
import random

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Database Setup
def create_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    email TEXT UNIQUE,
                    password TEXT)''')
    conn.commit()
    conn.close()

create_db()

# Send OTP via Email
def send_otp(email):
    otp = str(random.randint(100000, 999999))
    session['otp'] = otp
    sender_email = "your_email@gmail.com"
    sender_password = "your_password"

    message = f"Subject: Your OTP Code\n\nYour OTP is {otp}. Please do not share it."

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, message)
        server.quit()
    except Exception as e:
        print("Error:", e)

# Home Page
@app.route('/')
def home():
    return render_template('index.html')

# Signup Page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('signup'))

        send_otp(email)
        session['temp_user'] = {'name': name, 'email': email, 'password': password}
        return redirect(url_for('verify_otp'))
    
    return render_template('signup.html')

# OTP Verification
@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        user_otp = request.form['otp']
        if user_otp == session['otp']:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            user = session.pop('temp_user')
            c.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", 
                      (user['name'], user['email'], user['password']))
            conn.commit()
            conn.close()
            flash("Signup Successful! You can now login.", "success")
            return redirect(url_for('login'))
        else:
            flash("Invalid OTP!", "danger")
            return redirect(url_for('verify_otp'))
    
    return render_template('verify_otp.html')

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
        user = c.fetchone()
        conn.close()
        
        if user:
            session['user'] = user[1]  # Store username in session
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password!", "danger")
    
    return render_template('login.html')

# Dashboard Page
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=session['user'])

# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
