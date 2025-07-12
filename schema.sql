CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    title TEXT,
    notes TEXT,
    file_path TEXT,
    file_type TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS review_schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    material_id INTEGER,
    review_date DATE,
    completed BOOLEAN DEFAULT 0,
    FOREIGN KEY(material_id) REFERENCES materials(id)
);

CREATE TABLE IF NOT EXISTS knowledge (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    material_id INTEGER,
    text TEXT,
    FOREIGN KEY(material_id) REFERENCES materials(id)
);

CREATE TABLE IF NOT EXISTS quizzes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    material_id INTEGER,
    question TEXT,
    answer TEXT,
    FOREIGN KEY(material_id) REFERENCES materials(id)
);