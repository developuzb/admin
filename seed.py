import sqlite3
from datetime import datetime


def init_db(db_path="bot.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            name TEXT,
            phone TEXT,
            joined_at TEXT,
            cashback_balance INTEGER DEFAULT 0,
            user_segment TEXT,
            first_seen TEXT,
            loyal_customer INTEGER DEFAULT 0,
            balance INTEGER DEFAULT 0,
            actions_count INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()
    print("✅ Jadval yaratildi (yoki mavjud edi).")


def insert_dummy_user(db_path="bot.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (
            telegram_id, name, phone, joined_at, cashback_balance,
            user_segment, first_seen, loyal_customer, balance, actions_count
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        553740532, "Test Foydalanuvchi", "+998901112233",
        datetime.now().isoformat(), 0,
        "A", datetime.now().isoformat(), 0, 0, 0
    ))
    conn.commit()
    conn.close()
    print("✅ Test foydalanuvchi qo‘shildi.")


# 👉 FUNKSIYALAR YUQORIDA, ENDI Ularni chaqiramiz
init_db()
insert_dummy_user()
