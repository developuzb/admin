import sqlite3


def create_orders_table():
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY,
        service_id INTEGER NOT NULL,
        service_name TEXT,
        user_id INTEGER NOT NULL,
        phone TEXT,
        contact_method TEXT,
        contact_time TEXT,
        name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    print("✅ 'orders' jadvali yaratildi yoki mavjud edi.")
    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_orders_table()
