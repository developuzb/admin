import sqlite3

conn = sqlite3.connect("bot.db")
cursor = conn.cursor()

# cost_price — tan narxi
try:
    cursor.execute(
        "ALTER TABLE services ADD COLUMN cost_price INTEGER DEFAULT 0;")
    print("✅ cost_price ustuni qo‘shildi.")
except:
    print("ℹ️ cost_price allaqachon mavjud.")

# original_price — aksiya oldi narx
try:
    cursor.execute(
        "ALTER TABLE services ADD COLUMN original_price INTEGER DEFAULT 0;")
    print("✅ original_price ustuni qo‘shildi.")
except:
    print("ℹ️ original_price allaqachon mavjud.")

# cashback — %
try:
    cursor.execute(
        "ALTER TABLE services ADD COLUMN cashback INTEGER DEFAULT 0;")
    print("✅ cashback ustuni qo‘shildi.")
except:
    print("ℹ️ cashback allaqachon mavjud.")

conn.commit()
conn.close()
