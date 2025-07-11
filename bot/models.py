def init_db():
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()

    # Bu MUHIM:
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
    ...
    conn.commit()
    conn.close()
