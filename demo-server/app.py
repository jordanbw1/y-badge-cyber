from flask import Flask, jsonify, request, render_template, url_for, session, redirect, flash, send_from_directory
from dotenv import load_dotenv
import os
import datetime
import re
import json


USERS = {
    'jimmy': 'cyberRocks!',
    'katie': 'password',
    'teacher': 'iloveteaching'
}

GRADES = {
    'jimmy': {'Math': 99, 'Science': 88},
    'katie': {'Math': 87, 'Science': 91}
}


load_dotenv(".env")

app = Flask(__name__)
app.config['SECRET_KEY'] = "supersecretkey"


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/grades', methods=['GET'])
def grades():
    # Check if the user is an admin
    if 'username' not in session:
        flash("You need to be signed in to access grades", 'danger')
        return redirect(url_for('login'))
    # Get grades information
    username = session['username']
    user_grades = GRADES.get(username, {})
    return render_template('grades.html', username=username, grades=user_grades)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in USERS and USERS[username] == password:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/list_view', methods=['GET'])
def list_view():
    # Collect all endpoints
    endpoints = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':  # Exclude static files
            endpoints.append({
                'endpoint': rule.endpoint,
                'methods': ','.join(rule.methods),
                'path': str(rule)
            })
    return jsonify({'endpoints': endpoints})


@app.route('/robots.txt', methods=['GET'])
def robots():
    return send_from_directory(app.static_folder, "robots.txt")


# ------------------ Teacher routes ------------------ #
@app.route('/passwords', methods=['GET'])
def passwords():
    return render_template('passwords.html', users=USERS)


@app.route('/teacher_portal', methods=['GET', 'POST'])
def teacher_portal():
    # Confirm teacher signed in
    if 'username' not in session or session['username'] != 'teacher':
        flash('You need to be signed in as a teacher to access this page', 'danger')
        return redirect(url_for('login'))
    if request.method == 'GET':
        return render_template('teacher_portal.html', grades=GRADES)
    if request.method == 'POST':
        # Get the form data
        student = request.form.get('student')
        subject = request.form.get('subject')
        grade = request.form.get('grade')
        # Validate the grade
        if not re.match(r'^\d{1,3}$', grade):
            flash('Invalid grade', 'danger')
            return redirect(url_for('teacher_portal'))
        # Update the grade
        GRADES[student][subject] = int(grade)
        flash('Grade updated', 'success')
        return redirect(url_for('teacher_portal'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
