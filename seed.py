import sqlite3

# Bazaga ulanamiz
conn = sqlite3.connect("bot.db")
cursor = conn.cursor()

# Ustunni qo‘shamiz
try:
    cursor.execute(
        "ALTER TABLE orders ADD COLUMN timestamp TEXT DEFAULT (datetime('now'))")
    conn.commit()
    print("✅ 'timestamp' ustuni qo‘shildi.")
except sqlite3.OperationalError as e:
    print(f"⚠️ Xatolik: {e}")

# Ustunlar ro‘yxatini tekshiramiz
cursor.execute("PRAGMA table_info(orders)")
columns = cursor.fetchall()
for col in columns:
    print(col)

# Ulani yopamiz
conn.close()
