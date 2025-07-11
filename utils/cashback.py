import sqlite3
from datetime import datetime

def add_cashback(user_id: int, amount: int, direction: str, order_id: int = None):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO cashback_history (user_id, amount, direction, order_id, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, amount, direction, order_id, now))

    if direction == "in":
        cursor.execute("UPDATE users SET cashback_balance = cashback_balance + ? WHERE id = ?", (amount, user_id))
    elif direction == "out":
        cursor.execute("UPDATE users SET cashback_balance = cashback_balance - ? WHERE id = ?", (amount, user_id))

    conn.commit()
    conn.close()
