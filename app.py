from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from functools import wraps
from datetime import datetime, timedelta
import os
import hashlib
from werkzeug.utils import secure_filename
import uuid
import psycopg2
import psycopg2.extras
import google.generativeai as genai
import json

# Import our new AI utility functions
from ai_utils import extract_text_from_file, generate_knowledge_and_quiz

app = Flask(__name__)
# It's important to use a strong, secret key.
# For production, load this from an environment variable.
# e.g., app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'a-default-fallback-key')
app.secret_key = "a-very-secret-key-that-you-should-change"

# --- Gemini API Configuration ---
# For security, set your API key as an environment variable
# in your terminal before running the app. For example:
# export GEMINI_API_KEY='YOUR_API_KEY_HERE'

# --- PostgreSQL Configuration ---
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "kids_learning_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "")


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

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    conn = psycopg2.connect(host=DB_HOST,
                            database=DB_NAME,
                            user=DB_USER,
                            password=DB_PASS)
    return conn

def init_db():
    with get_db_connection() as conn:
        with conn.cursor() as c:
            # Read the schema from the .sql file to initialize the database
            with open('schema.sql', 'r') as f:
                c.execute(f.read())
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
            with get_db_connection() as conn:
                with conn.cursor() as c:
                    c.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, password))
                conn.commit()
            flash('Signup successful. Please log in.', 'success')
            return redirect(url_for('login'))
        except psycopg2.IntegrityError:
            flash('Username already exists.')
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])
        with get_db_connection() as conn:
            with conn.cursor() as c:
                c.execute("SELECT id FROM users WHERE username = %s AND password_hash = %s", (username, password))
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
            # Generate a unique filename to prevent overwrites
            original_filename = secure_filename(file.filename)
            _, extension = os.path.splitext(original_filename)
            unique_filename = str(uuid.uuid4()) + extension
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)

        with get_db_connection() as conn:
            with conn.cursor() as c:
                c.execute("INSERT INTO materials (user_id, title, notes, upload_date, file_path) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                          (session['user_id'], title, notes, str(upload_date), file_path))
                material_id = c.fetchone()[0]
            
            # --- AI INTEGRATION ---
            if file_path:
                print(f"Processing file for AI content: {file_path}")
                # 1. Extract text from the saved file
                extracted_text = extract_text_from_file(file_path)

                if extracted_text:
                    # Store the original extracted text
                    c.execute("INSERT INTO original_text (material_id, text) VALUES (%s, %s)",
                              (material_id, extracted_text))

                    # 2. Generate knowledge and quiz using Gemini
                    ai_content = generate_knowledge_and_quiz(extracted_text)

                    if ai_content:
                        # 3. Save the generated content to the database
                        # Save knowledge summary
                        c.execute("INSERT INTO knowledge (material_id, text) VALUES (%s, %s)",
                                  (material_id, ai_content.get('knowledge_summary')))
                        
                        # Save quiz questions
                        for q in ai_content.get('quiz', []):
                            c.execute("INSERT INTO quizzes (material_id, question, answer) VALUES (%s, %s, %s)",
                                      (material_id, q.get('question'), q.get('answer')))
                        print("Successfully saved AI content to database.")
            
            days = [0, 1, 3, 7, 14, 30]
            for day in days:
                review_date = upload_date + timedelta(days=day)
                c.execute("INSERT INTO reviews (material_id, review_date) VALUES (%s, %s)",
                          (material_id, str(review_date)))
            conn.commit()
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/review')
@login_required
def review():
    today = str(datetime.today().date())
    with get_db_connection() as conn:
        with conn.cursor() as c:
            c.execute('''
            SELECT reviews.id, materials.title, materials.notes, reviews.review_date, materials.file_path
            FROM reviews
            JOIN materials ON reviews.material_id = materials.id
            WHERE reviews.review_date = %s AND reviews.done = 0 AND materials.user_id = %s
        ''', (today, session['user_id']))
            items = c.fetchall()
    return render_template('review.html', items=items, today=today)

@app.route('/mark_reviewed/<int:review_id>')
@login_required
def mark_reviewed(review_id):
    with get_db_connection() as conn:
        with conn.cursor() as c:
            c.execute("UPDATE reviews SET done = 1 WHERE id = %s", (review_id,))
        conn.commit()
    return redirect(url_for('review'))


@app.route('/materials')
@login_required
def materials():
    with get_db_connection() as conn:
        with conn.cursor() as c:
            c.execute('''
            SELECT id, title, notes, upload_date, file_path
            FROM materials
            WHERE user_id = %s
            ORDER BY upload_date DESC
        ''', (session['user_id'],))
            materials = c.fetchall()
    return render_template('materials.html', materials=materials)

@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/material/<int:material_id>/original')
@login_required
def original_text(material_id):
    with get_db_connection() as conn:
        with conn.cursor() as c:
            # Fetch original text and material title
            c.execute("SELECT text FROM original_text WHERE material_id = %s", (material_id,))
            original_text_item = c.fetchone()
            c.execute("SELECT title FROM materials WHERE id = %s", (material_id,))
            material_title = c.fetchone()
    return render_template('original_text.html',
                           original_text=original_text_item,
                           title=material_title[0] if material_title else "Original Text")

@app.route('/material/<int:material_id>/knowledge')
@login_required
def knowledge(material_id):
    with get_db_connection() as conn:
        with conn.cursor() as c:
            # Fetch knowledge text and material title
            c.execute("SELECT text FROM knowledge WHERE material_id = %s", (material_id,))
            knowledge_item = c.fetchone()
            c.execute("SELECT title FROM materials WHERE id = %s", (material_id,))
            material_title = c.fetchone()
    return render_template('knowledge.html', knowledge=knowledge_item, title=material_title[0] if material_title else "Knowledge")

@app.route('/quiz/<int:material_id>')
@login_required
def quiz(material_id):
    with get_db_connection() as conn:
        with conn.cursor() as c:
            # Fetch all quiz questions for the material
            c.execute("SELECT question, answer FROM quizzes WHERE material_id = %s", (material_id,))
            quiz_items = c.fetchall()
            c.execute("SELECT title FROM materials WHERE id = %s", (material_id,))
            material_title = c.fetchone()
    return render_template('quiz.html', quizzes=quiz_items, title=material_title[0] if material_title else "Quiz")

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    # The database is now initialized via the run.sh script
    app.run(debug=True)