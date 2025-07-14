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


def add_missing_columns():
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()

    # Ustunlar ro‘yxatini tekshir
    cursor.execute("PRAGMA table_info(orders);")
    columns = [col[1] for col in cursor.fetchall()]

    additions = {
        "phone": "TEXT",
        "service_name": "TEXT",
        "contact_method": "TEXT",
        "contact_time": "TEXT",
        "name": "TEXT",
        "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    }

    for column_name, column_type in additions.items():
        if column_name not in columns:
            print(f"➕ Ustun qo‘shilmoqda: {column_name}")
            cursor.execute(
                f"ALTER TABLE orders ADD COLUMN {column_name} {column_type};")
        else:
            print(f"✅ Ustun mavjud: {column_name}")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    add_missing_columns()
