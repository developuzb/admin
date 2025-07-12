import sqlite3
import os


def add_used_cashback_column():
    try:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, "bot.db")

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(
            "ALTER TABLE orders ADD COLUMN used_cashback INTEGER DEFAULT 0")
        conn.commit()
        print("✅ used_cashback ustuni qo‘shildi.")

    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("ℹ️ used_cashback ustuni allaqachon mavjud.")
        else:
            raise
    finally:
        conn.close()


# Funksiyani ishga tushirish
add_used_cashback_column()
