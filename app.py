from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
from datetime import datetime, timedelta
import sqlite3
import os
import hashlib
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "your_secret_key"
DB_FILE = "kids_learning.db"

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS materials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT NOT NULL,
                notes TEXT,
                upload_date TEXT,
                file_path TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                material_id INTEGER,
                review_date TEXT,
                done INTEGER DEFAULT 0,
                FOREIGN KEY(material_id) REFERENCES materials(id)
            )
        ''')
        conn.commit()

@app.route('/')
@login_required
def index():
    return render_template('index.html', username=session.get('username'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])
        try:
            with sqlite3.connect(DB_FILE) as conn:
                c = conn.cursor()
                c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password))
                conn.commit()
            flash('Signup successful. Please log in.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists.')
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("SELECT id FROM users WHERE username = ? AND password_hash = ?", (username, password))
            user = c.fetchone()
            if user:
                session['user_id'] = user[0]
                session['username'] = username
                return redirect(url_for('index'))
            else:
                flash('Invalid credentials.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.')
    return redirect(url_for('login'))

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        title = request.form['title']
        notes = request.form['notes']
        upload_date = datetime.today().date()
        file = request.files.get('file')
        file_path = None

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO materials (user_id, title, notes, upload_date, file_path) VALUES (?, ?, ?, ?, ?)",
                      (session['user_id'], title, notes, str(upload_date), file_path))
            material_id = c.lastrowid

            days = [0, 1, 3, 7, 14, 30]
            for day in days:
                review_date = upload_date + timedelta(days=day)
                c.execute("INSERT INTO reviews (material_id, review_date) VALUES (?, ?)",
                          (material_id, str(review_date)))
            conn.commit()
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/review')
@login_required
def review():
    today = str(datetime.today().date())
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''
            SELECT reviews.id, materials.title, materials.notes, reviews.review_date, materials.file_path
            FROM reviews
            JOIN materials ON reviews.material_id = materials.id
            WHERE reviews.review_date = ? AND reviews.done = 0 AND materials.user_id = ?
        ''', (today, session['user_id']))
        items = c.fetchall()
    return render_template('review.html', items=items, today=today)

@app.route('/mark_reviewed/<int:review_id>')
@login_required
def mark_reviewed(review_id):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("UPDATE reviews SET done = 1 WHERE id = ?", (review_id,))
        conn.commit()
    return redirect(url_for('review'))

if __name__ == '__main__':
    if not os.path.exists(DB_FILE):
        init_db()
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)


@app.route('/materials')
@login_required
def materials():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''
            SELECT id, title, notes, upload_date, file_path
            FROM materials
            WHERE user_id = ?
            ORDER BY upload_date DESC
        ''', (session['user_id'],))
        materials = c.fetchall()
    return render_template('materials.html', materials=materials)