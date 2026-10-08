-- 📋 pastebin schema
CREATE TABLE pastes(id INTEGER PRIMARY KEY, token TEXT UNIQUE, iv TEXT, salt TEXT, ciphertext TEXT, lang TEXT DEFAULT 'text', expires_at DATETIME, burn INTEGER DEFAULT 0, views INTEGER DEFAULT 0, created_at DATETIME);
