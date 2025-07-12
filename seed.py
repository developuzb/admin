import sqlite3


def add_used_cashback_column():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            "ALTER TABLE orders ADD COLUMN used_cashback INTEGER DEFAULT 0")
        conn.commit()
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            pass  # Ustun allaqachon mavjud
        else:
            raise
    finally:
        conn.close()
