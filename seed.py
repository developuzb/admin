import sqlite3

db = sqlite3.connect("bot.db")
cursor = db.cursor()

# 🆕 balance ustuni
try:
    cursor.execute("ALTER TABLE users ADD COLUMN balance INTEGER DEFAULT 0;")
    print("✅ 'balance' ustuni qo‘shildi.")
except Exception as e:
    print(f"⚠️ balance ustuni mavjud yoki xatolik: {e}")

# 🆕 actions_count ustuni
try:
    cursor.execute(
        "ALTER TABLE users ADD COLUMN actions_count INTEGER DEFAULT 0;")
    print("✅ 'actions_count' ustuni qo‘shildi.")
except Exception as e:
    print(f"⚠️ actions_count ustuni mavjud yoki xatolik: {e}")

db.commit()
db.close()
