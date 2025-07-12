import sqlite3

conn = sqlite3.connect("bot.db")  # yoki kerakli to‘liq yo‘l
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    service_id INTEGER,
    contact TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
""")

conn.commit()
conn.close()
