import sqlite3
from datetime import datetime


def get_services_with_stats_from_db(db: sqlite3.Connection):
    cursor = db.cursor()

    cursor.execute("""
        SELECT
            s.id,
            s.name,
            s.price,
            s.cost_price,
            s.active,
            s.image,              -- ✅ BU QATORNI QO‘SHING
            s.description,
            s.original_price,
            s.cashback,
            COUNT(o.id) AS order_count,
            (s.price - s.cost_price) * COUNT(o.id) AS total_profit
        FROM services s
        LEFT JOIN orders o ON s.id = o.service_id
        GROUP BY s.id
        ORDER BY total_profit DESC
    """)

    rows = cursor.fetchall()
    return [dict(row) for row in rows]


def get_services_with_stats(db_path: str = "bot.db"):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            s.id,
            s.name,
            s.price,
            s.cost_price,
            s.active,
            s.image,  -- ✅ RASM NOMINI QO‘SHDIK
            s.description,
            s.original_price,
            s.cashback,
            COUNT(o.id) AS order_count,
            (s.price - s.cost_price) * COUNT(o.id) AS total_profit
        FROM services s
        LEFT JOIN orders o ON s.id = o.service_id
        GROUP BY s.id
        ORDER BY total_profit DESC
    """)

    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def add_cashback(user_id: int, amount: int, direction: str, order_id: int = None, db_path: str = "bot.db"):
    """
    Foydalanuvchiga cashback qo‘shish yoki olib tashlash.

    :param user_id: users jadvalidagi ID
    :param amount: qancha summa (so‘m)
    :param direction: 'in' (kiritish) yoki 'out' (ayirish)
    :param order_id: agar mavjud bo‘lsa, cashback qaysi buyurtma bilan bog‘liq
    :param db_path: bazaning manzili (default = 'bot.db')
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Cashback tarixiga yozamiz
    cursor.execute("""
        INSERT INTO cashback_history (user_id, amount, direction, order_id, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, amount, direction, order_id, now))

    # Balansni yangilaymiz
    if direction == "in":
        cursor.execute("""
            UPDATE users SET cashback_balance = cashback_balance + ? WHERE id = ?
        """, (amount, user_id))
    elif direction == "out":
        cursor.execute("""
            UPDATE users SET cashback_balance = cashback_balance - ? WHERE id = ?
        """, (amount, user_id))

    conn.commit()
    conn.close()

def get_dashboard_stats(db: sqlite3.Connection):
    cursor = db.cursor()

    # Buyurtmalar statistikasi
    cursor.execute("""
        SELECT 
            DATE(created_at) as date,
            COUNT(*) as orders,
            SUM(price - cost_price) as profit
        FROM orders
        JOIN services ON orders.service_id = services.id
        WHERE DATE(created_at) >= DATE('now', '-6 days')
        GROUP BY DATE(created_at)
        ORDER BY DATE(created_at)
    """)
    trend_rows = cursor.fetchall()

    labels = []
    order_data = []
    profit_data = []

    for row in trend_rows:
        labels.append(row["date"])
        order_data.append(row["orders"])
        profit_data.append(row["profit"] or 0)

    # Bugungi statistikalar
    cursor.execute("""
        SELECT COUNT(*) FROM orders WHERE DATE(created_at) = DATE('now')
    """)
    today_orders = cursor.fetchone()[0]

    cursor.execute("""
        SELECT SUM(price - cost_price) FROM orders
        JOIN services ON orders.service_id = services.id
        WHERE DATE(created_at) = DATE('now')
    """)
    today_profit = cursor.fetchone()[0] or 0

    # Top xizmatlar
    cursor.execute("""
        SELECT s.name, COUNT(o.id) as order_count,
               (s.price - s.cost_price) * COUNT(o.id) as profit
        FROM services s
        LEFT JOIN orders o ON s.id = o.service_id
        GROUP BY s.id
        ORDER BY order_count DESC
        LIMIT 5
    """)
    top_services = [dict(row) for row in cursor.fetchall()]

    return {
        "today_orders": today_orders,
        "today_profit": today_profit,
        "trend_labels": labels,
        "orders_data": order_data,
        "profit_data": profit_data,
        "top_services": top_services
    }
