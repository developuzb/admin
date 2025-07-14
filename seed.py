def add_last_order_column():
    db = sqlite3.connect("bot.db")
    cursor = db.cursor()
    cursor.execute("ALTER TABLE services ADD COLUMN last_order INTEGER;")
    db.commit()


print("yaratildi")
