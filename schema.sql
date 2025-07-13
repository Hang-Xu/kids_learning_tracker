CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS materials (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    title TEXT NOT NULL,
    notes TEXT,
    upload_date TEXT,
    file_path TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS reviews (
    id SERIAL PRIMARY KEY,
    material_id INTEGER,
    review_date TEXT,
    done INTEGER DEFAULT 0,
    FOREIGN KEY (material_id) REFERENCES materials(id)
);

CREATE TABLE IF NOT EXISTS knowledge (
    id SERIAL PRIMARY KEY,
    material_id INTEGER,
    text TEXT,
    FOREIGN KEY (material_id) REFERENCES materials(id)
);

CREATE TABLE IF NOT EXISTS quizzes (
    id SERIAL PRIMARY KEY,
    material_id INTEGER,
    question TEXT,
    answer TEXT,
    FOREIGN KEY (material_id) REFERENCES materials(id)
);

CREATE TABLE IF NOT EXISTS original_text (
    id SERIAL PRIMARY KEY,
    material_id INTEGER,
    text TEXT,
    FOREIGN KEY (material_id) REFERENCES materials(id)
);