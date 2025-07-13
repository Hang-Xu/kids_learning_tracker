# 🧠 Kids Learning Tracker – AI-Powered with Image OCR and Flashcards

This is a working prototype of a learning tracker web app for kids. It lets you upload notes or homework (PDF or image), uses AI to extract quiz questions and knowledge, and helps kids review based on the Forgetting Curve.

---

## 🚀 Features

- Upload material (PDF or image)
- Automatic text extraction (PDF or OCR for image)
- Google Gemini API to extract:
  - Key knowledge
  - Quiz questions + answers
- Flashcard-style quiz interface
- Tailwind CSS for modern UI
- User login/session support (local only)

---

## 🛠 Tech Stack

| Component     | Tool               |
|---------------|--------------------|
| Backend       | Flask (Python)     |
| Database      | SQLite             |
| AI Engine     | Google Gemini      |
| Image OCR     | pytesseract        |
| PDF Reader    | PyMuPDF            |
| UI Styling    | Tailwind CSS (CDN) |

---

## ✅ How to Run

1. Install dependencies:
```bash
pip install flask google-generativeai pytesseract Pillow PyMuPDF psycopg2-binary
```

2. Install Tesseract:
- macOS: `brew install tesseract`
- Ubuntu: `sudo apt install tesseract-ocr`

3. Set up PostgreSQL Database:
   - Make sure you have a running PostgreSQL server.
   - Use `psql` or another database tool to create a user and a database for this application.
   - Example using the `psql` command-line tool:
     ```sql
     CREATE DATABASE kids_learning_db;
     CREATE USER your_db_user WITH PASSWORD 'your_db_password';
     GRANT ALL PRIVILEGES ON DATABASE kids_learning_db TO your_db_user;
     ```

4. Configure the startup script.
   - Open the `run.sh` file.
   - Replace the placeholder values for `GEMINI_API_KEY`, `DB_HOST`, `DB_NAME`, `DB_USER`, and `DB_PASS` with your actual credentials.

5. Make the script executable and initialize the database.
   *(This only needs to be done once)*
```bash
chmod +x run.sh
./run.sh init-db
```

5. Visit: [http://localhost:5000](http://localhost:5000)

---

## 📂 Supported File Types

| File Type | Supported | Notes |
|-----------|-----------|-------|
| PDF       | ✅         | Text extracted using PyMuPDF |
| Image     | ✅         | Text extracted using pytesseract |
| Handwriting | ⚠️ Maybe | Accuracy depends on clarity |

---

## 📚 Review Pages

- `/quiz/<id>` — Quiz cards
- `/material/<id>/knowledge` — AI summary

---

## 🧪 Sample Ideas

Try uploading math PDFs or screenshots of typed notes. Gemini will extract knowledge and quiz questions automatically!

---

Built for personal learning use. Prototype only.