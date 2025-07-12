import sqlite3

conn = sqlite3.connect("bot.db")  # kerakli to‘liq yo‘lni yozing
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

print("✅ orders jadvali yaratildi.")
