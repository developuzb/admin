import sqlite3

conn = sqlite3.connect("bot.db")
cursor = conn.cursor()

# Eski jadvalni o‘chirib tashlaymiz
cursor.execute("DROP TABLE IF EXISTS orders")

# Yangi to‘liq formatda qayta yaratamiz
cursor.execute("""
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    service_id INTEGER,
    contact TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
""")

conn.commit()
conn.close()
print("✅ orders jadvali yangilandi.")
