import sqlite3


def add_column_if_not_exists(cursor, table, column, col_type, default="''"):
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [info[1] for info in cursor.fetchall()]
    if column not in columns:
        print(f"➕ Adding column: {column}")
        cursor.execute(
            f"ALTER TABLE {table} ADD COLUMN {column} {col_type} DEFAULT {default}")
    else:
        print(f"✅ Column already exists: {column}")


if __name__ == "__main__":
    conn = sqlite3.connect("bot.db")  # ← yoki sizning DB faylingiz nomi
    cursor = conn.cursor()

    add_column_if_not_exists(
        cursor, "services", "duration", "TEXT", "'1 soat'")
    add_column_if_not_exists(cursor, "services", "cashback", "INTEGER", "0")
    add_column_if_not_exists(cursor, "services", "image_url", "TEXT", "''")

    conn.commit()
    conn.close()
    print("✅ Ustunlar tekshirildi va zarur bo‘lsa qo‘shildi.")
