import sqlite3

# Fayl manzilini aniqlang
# yoki to‘liq manzil yozing: "C:/Users/suxrob/Desktop/SQlite2/SQlite2/SQlite2/bot.db"
db_path = "bot.db"

# Ulash
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Ustun bor-yo‘qligini tekshirish
cursor.execute("PRAGMA table_info(services);")
columns = [col[1] for col in cursor.fetchall()]
print("Joriy ustunlar:", columns)

if "cashback_given" not in columns:
    print("➡️  'cashback_given' ustuni qo‘shilmoqda...")
    cursor.execute(
        "ALTER TABLE services ADD COLUMN cashback_given INTEGER DEFAULT 0;")
    conn.commit()
    print("✅ Ustun qo‘shildi.")
else:
    print("ℹ️  'cashback_given' ustuni allaqachon mavjud.")

# Yopish
conn.close()
