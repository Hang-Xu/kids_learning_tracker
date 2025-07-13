import os
import google.generativeai as genai
import pytesseract
from PIL import Image
import fitz  # PyMuPDF
import json

def extract_text_from_file(file_path):
    """Extracts text from a given file (PDF, image, or text)."""
    try:
        if file_path.lower().endswith('.pdf'):
            text_parts = []
            with fitz.open(file_path) as doc:
                for page in doc:
                    text_parts.append(page.get_text())
            return "".join(text_parts)
        elif file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            return pytesseract.image_to_string(Image.open(file_path))
        elif file_path.lower().endswith('.txt'):
            with open(file_path, 'r') as f:
                return f.read()
    except Exception as e:
        print(f"Error extracting text from {file_path}: {e}")
    return ""

def generate_knowledge_and_quiz(text_content):
    """
    Uses Gemini to generate a knowledge summary and quiz questions from text.
    Returns a dictionary with 'knowledge' and 'quiz'.
    """
    if not text_content or not text_content.strip():
        print("Cannot generate AI content from empty or whitespace-only text.")
        return None

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        print("GEMINI_API_KEY environment variable not set.")
        return None
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""
    Based on the following text, please perform two tasks:
    1. Provide a concise summary of the most important knowledge points for a child to learn.
    2. Create a list of 5-10 quiz questions, each with a clear, short answer. The difficulty of these questions should closely match the complexity and style of the content in the provided text.

    Please format your response as a single JSON object with two keys: "knowledge_summary" and "quiz".
    The "knowledge_summary" key should have a string value.
    The "quiz" key should have a value that is an array of objects, where each object has a "question" and "answer" key.

    Example format:
    {{
      "knowledge_summary": "A brief summary of the text.",
      "quiz": [
        {{ "question": "What is the first question?", "answer": "The first answer." }},
        {{ "question": "What is the second question?", "answer": "The second answer." }}
      ]
    }}

    Here is the text:
    ---
    {text_content}
    ---
    """
    try:
        response = model.generate_content(prompt)
        # Clean up the response to extract the JSON part
        json_response_text = response.text.strip().lstrip("```json").rstrip("```")
        return json.loads(json_response_text)
    except (json.JSONDecodeError, Exception) as e:
        print(f"Error generating or parsing AI content: {e}")
        return None