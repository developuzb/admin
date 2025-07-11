import sqlite3

def init_db():
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()

    # USERS jadvali (A/B test va sodiq mijozlar uchun kengaytirilgan)
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE,
        name TEXT,
        phone TEXT,
        joined_at TEXT,
        cashback_balance INTEGER DEFAULT 0,
        user_segment TEXT,              -- 'A' yoki 'B'
        first_seen TEXT,                -- birinchi kirgan vaqt
        loyal_customer INTEGER DEFAULT 0  -- 1 = sodiq mijoz
    )
    """)

        # SERVICES jadvali
    c.execute("""
    CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        price INTEGER,
        original_price INTEGER,
        cost_price INTEGER,  -- ✅ Tan narxi (foyda hisobida ishlatiladi)
        cashback INTEGER,
        image TEXT,
        payment_options TEXT,
        active INTEGER DEFAULT 1
    )
    """)


    # ORDERS jadvali
    c.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        service_id INTEGER,
        phone TEXT,
        contact_time TEXT,
        created_at TEXT,
        status TEXT,
        used_cashback INTEGER,
        source TEXT
    )
    """)

    # CASHBACK_HISTORY jadvali
    c.execute("""
    CREATE TABLE IF NOT EXISTS cashback_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount INTEGER,
        direction TEXT,
        order_id INTEGER,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect("bot.db")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
