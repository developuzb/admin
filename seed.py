import sqlite3


def add_service_name_column():
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()

    try:
        # Ustun mavjudligini tekshirish (mavjud bo‘lsa, qo‘shmaslik uchun)
        cursor.execute("PRAGMA table_info(orders);")
        columns = [col[1] for col in cursor.fetchall()]
        if "service_name" not in columns:
            cursor.execute("ALTER TABLE orders ADD COLUMN service_name TEXT;")
            print("✅ 'service_name' ustuni qo‘shildi.")
        else:
            print("ℹ️ 'service_name' ustuni allaqachon mavjud.")
    except Exception as e:
        print(f"❌ Xatolik: {e}")
    finally:
        conn.commit()
        conn.close()


if __name__ == "__main__":
    add_service_name_column()
