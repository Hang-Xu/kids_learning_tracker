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
pip install flask google-generativeai pytesseract Pillow PyMuPDF
```

2. Install Tesseract:
- macOS: `brew install tesseract`
- Ubuntu: `sudo apt install tesseract-ocr`

3. Add your [Gemini API Key](https://makersuite.google.com/app/apikey) in `app.py`:

```python
genai.configure(api_key="YOUR_API_KEY_HERE")
```

4. Run:
```bash
python app.py
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