import sqlite3



db = sqlite3.connect("db.db", check_same_thread=False)
cursor = db.cursor()

# Zarur bo'lgan jadvallarni tekshirish
cursor.execute("""
CREATE TABLE IF NOT EXISTS queue (
    chat_id INTEGER PRIMARY KEY
);
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS chats (
    chat_one INTEGER NOT NULL,
    chat_two INTEGER NOT NULL
);
""")
db.commit()